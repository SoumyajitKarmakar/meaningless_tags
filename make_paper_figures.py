#!/usr/bin/env python3
"""Draw the paper figures from the existing statistics and E13 reports.

Install: python -m pip install matplotlib numpy
Run:     python make_paper_figures.py --report stats_report.md --out figures
Or use your result tree:
         python make_paper_figures.py --report stats_report.md --results results

Outputs (vector PDF and 300-dpi PNG):
  fig1_wrapper_effects       All 20 wrappers, attributed assertion, paired CIs.
  fig2_name_gaps             30 random names and six meaningful names per panel.
  fig3_instruction_guards    Three warning wordings x three positions.
  appendix_assertion_guards The corresponding false-assertion results.

Also writes the plotted values to CSV and suggested captions to captions.tex.
The reports' rounded estimates and existing intervals are used directly.
No model calls, new tests, or reconstructed confidence intervals are involved.
The E13 reports contain the per-name gaps, so the raw JSONL files are not needed.
"""

# python make_paper_figures.py \
#   --report results/stats/stats_report.md \
#   --results results \
#   --out figures

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator


BLUE, ORANGE, GREEN, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#8b8a85"
INK, GRID = "#292929", "#e6e5e1"
MODELS = ("Gemma 4 12B", "Qwen 3.6 27B")
RELATIONS = ("elements", "capitals")
RELATION_IDS = {"elements": "element_symbol", "capitals": "country_capital"}
PANELS = tuple((model, relation) for model in MODELS for relation in RELATIONS)
POSITIONS = ("system prompt", "user, above", "user, below")
WARNINGS = ("falsehood", "instruction", "combined")

# Adjacent tag/label pairs, in the same order in all four panels.
WRAPPERS = (
    "<document>", "Document:",
    "<passage>", "Passage:",
    "<search_result>", "Search result:",
    "<trusted_content>", "Trusted content:",
    "<untrusted_content>", "Untrusted content:",
    "<unreliable_source>", "Unreliable source:",
    "<qzx_block>", "Qzx_block:",
    "<qzxzxew>", "Qzxzxew:",
    "blank lines", "--- fence", '\"\"\" fence', "<>",
)
COLOURS = [BLUE] * 8 + [GREEN] * 4 + [ORANGE] * 4 + [GREY] * 4
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
INTERVAL = re.compile(rf"^({NUMBER})%?\s*\[({NUMBER}),\s*({NUMBER})\]$")
RATE_MARGIN = re.compile(rf"^({NUMBER})%\s*\(({NUMBER})\)$")


@dataclass(frozen=True)
class Table:
    section: str
    group: str
    columns: tuple[str, ...]
    rows: list[dict[str, str]]


def clean(value: str) -> str:
    return value.strip().replace("`", "").replace("−", "-")


def cells(line: str) -> tuple[str, ...]:
    return tuple(clean(item) for item in line.strip().strip("|").split("|"))


def read_tables(path: Path) -> list[Table]:
    """Read the supplied report's Markdown tables, retaining section/group."""
    lines = path.read_text(encoding="utf-8").splitlines()
    tables: list[Table] = []
    section = group = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## "):
            section, group = line[3:], ""
        elif line.startswith("**"):
            match = re.match(r"\*\*(.*?)\*\*", line)
            if match:
                group = clean(match.group(1))
        elif line.startswith("|"):
            columns = cells(line)
            if i + 1 >= len(lines) or not all(
                re.fullmatch(r":?-{3,}:?", part.replace(" ", ""))
                for part in cells(lines[i + 1])
            ):
                raise ValueError(f"Malformed table header at line {i + 1}.")
            rows = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                values = cells(lines[i])
                if len(values) != len(columns):
                    raise ValueError(f"Wrong column count at line {i + 1}.")
                rows.append(dict(zip(columns, values)))
                i += 1
            tables.append(Table(section, group, columns, rows))
            continue
        i += 1
    return tables


def select_table(tables: list[Table], section: str, group: str,
                 first_column: str) -> Table:
    matches = [t for t in tables if t.section.startswith(section)
               and t.group == group and t.columns[0] == first_column]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one {first_column!r} table for {section!r}, {group!r}; "
            f"found {len(matches)}. Check the supplied report."
        )
    return matches[0]


def estimate(value: str) -> tuple[float, float, float]:
    match = INTERVAL.fullmatch(value)
    if not match:
        raise ValueError(f"Expected an estimate and CI, got {value!r}.")
    mid, low, high = map(float, match.groups())
    if not low <= mid <= high:
        raise ValueError(f"Estimate outside its CI: {value!r}.")
    return mid, low, high


def index_rows(table: Table, key: str) -> dict[str, dict[str, str]]:
    result = {}
    for row in table.rows:
        if row[key] in result:
            raise ValueError(f"Duplicate {key}: {row[key]} in {table.group}.")
        result[row[key]] = row
    return result


def load_data(path: Path) -> tuple[dict, dict]:
    tables = read_tables(path)
    wrappers, guards = {}, {}
    for model, relation in PANELS:
        group = f"{model} · {relation} · assert_r1"
        table = select_table(tables, "§4.2 The wrapper ladder", group, "Wrapper")
        rows = index_rows(table, "Wrapper")
        expected = set(WRAPPERS) | {"none"}
        if set(rows) != expected:
            raise ValueError(
                f"Wrapper set differs for {group}. "
                f"Missing: {sorted(expected - set(rows))}; "
                f"unexpected: {sorted(set(rows) - expected)}."
            )
        counts = {int(row["n"]) for row in rows.values()}
        if len(counts) != 1 or min(counts) < 1:
            raise ValueError(f"Inconsistent fact counts for {group}.")
        for name, row in rows.items():
            rate = estimate(row["Rate [exact CI]"])
            margin = estimate(row["M [CI]"])
            delta = None if name == "none" else estimate(row["ΔM vs none [CI]"])
            if not 0 <= rate[1] <= rate[2] <= 100:
                raise ValueError(f"Rate interval outside 0-100 for {group}.")
            wrappers[model, relation, name] = {
                "n": int(row["n"]), "rate": rate, "margin": margin, "delta": delta,
            }

        for cell in ("assert_r1", "explicit_stipulation"):
            group = f"{model} · {relation} · {cell}"
            table = select_table(tables, "§5 Guards", group, "Wording")
            rows = index_rows(table, "Wording")
            if set(rows) != {"none", *WARNINGS}:
                raise ValueError(f"Missing or unexpected warning wordings for {group}.")
            for wording, row in rows.items():
                for position in POSITIONS:
                    match = RATE_MARGIN.fullmatch(row[position])
                    if not match:
                        raise ValueError(f"Malformed guard entry: {row[position]!r}.")
                    rate, margin = map(float, match.groups())
                    if not 0 <= rate <= 100 or not np.isfinite(margin):
                        raise ValueError(f"Invalid guard value for {group}.")
                    guards[model, relation, cell, wording, position] = (rate, margin)
            baseline = {guards[model, relation, cell, "none", p] for p in POSITIONS}
            if len(baseline) != 1:
                raise ValueError(f"No-warning baseline differs across slots for {group}.")
            if cell == "explicit_stipulation" and next(iter(baseline))[0] != 100:
                raise ValueError(
                    f"No-warning rate is no longer 100% for {group}. "
                    "Update the instruction-guard caption before plotting this report."
                )
    return wrappers, guards


def load_names(report: Path, name_reports: dict[str, Path]) -> dict:
    """Read the reported paired gaps, without subtracting rounded endpoints."""
    tables = read_tables(report)
    result = {}
    shared_names = None
    for model, path in name_reports.items():
        e13 = read_tables(path)
        per_name = select_table(e13, "Per string", "", "Relation")
        summaries = select_table(e13, "Distribution over strings", "", "Relation")
        for relation in RELATIONS:
            relation_id = RELATION_IDS[relation]
            rows = [row for row in per_name.rows
                    if row["Relation"] == relation_id and row["Cell"] == "assert_r1"]
            names = [row["Name"] for row in rows]
            if len(names) != 30 or len(set(names)) != 30:
                raise ValueError(f"Expected 30 unique names in {path}, {relation}.")
            if shared_names is not None and set(names) != shared_names:
                raise ValueError("The random-name sets differ across the four panels.")
            shared_names = set(names)
            points = [{"name": row["Name"], "gap": float(row["Gap"]),
                       "tag_delta": float(row["Tag ΔM"]),
                       "label_delta": float(row["Label ΔM"]),
                       "tag_rate": float(row["Tag rate"].rstrip("%")),
                       "label_rate": float(row["Label rate"].rstrip("%"))}
                      for row in rows]
            for point in points:
                if not all(np.isfinite(v) for k, v in point.items() if k != "name"):
                    raise ValueError(f"Nonfinite per-name value in {path}.")
                # Each value is independently rounded to two decimal places.
                if abs(point["tag_delta"] - point["label_delta"] - point["gap"]) > 0.016:
                    raise ValueError(f"Inconsistent gap for {point['name']} in {path}.")
            summaries_for_panel = [row for row in summaries.rows
                                   if row["Relation"] == relation_id
                                   and row["Cell"] == "assert_r1"
                                   and row["Form"] == "tag_minus_label"]
            if len(summaries_for_panel) != 1:
                raise ValueError(f"Missing or duplicate gap summary in {path}, {relation}.")
            summary_row = summaries_for_panel[0]
            summary = estimate(f"{summary_row['Mean ΔM']} {summary_row['95% CI (crossed)']}")
            positives, total = map(int, summary_row["Strings > 0"].split("/"))
            if total != 30 or positives != sum(point["gap"] > 0 for point in points):
                raise ValueError(f"Per-name signs disagree with the summary in {path}.")
            if abs(np.mean([point["gap"] for point in points]) - summary[0]) > 0.011:
                raise ValueError(f"Per-name mean disagrees with the summary in {path}.")

            group = f"{model} · {relation} · assert_r1"
            contrasts = select_table(tables, "§4.2 Tag against label", group,
                                     "Contrast (A - B)")
            contrasts = index_rows(contrasts, "Contrast (A - B)")
            meaningful = []
            for tag, label in zip(WRAPPERS[:12:2], WRAPPERS[1:12:2]):
                row = contrasts[f"{tag} - {label}"]
                gap, low, high = estimate(row["ΔM"])
                meaningful.append({"name": tag[1:-1], "gap": gap,
                                   "low": low, "high": high, "n_facts": int(row["n"])})
            result[model, relation] = {
                "random": points, "meaningful": meaningful, "summary": summary,
                "positive": positives, "p": summary_row["p (across strings)"],
                "source": path.name,
            }
    return result


def configure_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.edgecolor": GRID,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
    })


def save(fig: plt.Figure, out: Path, name: str, dpi: int) -> None:
    # Crop to all visible artists, including figure-level labels and legends.
    # Keep only 0.02 inches (about 0.5 mm) of padding outside that bounding box.
    for suffix in ("pdf", "png"):
        path = out / f"{name}.{suffix}"
        fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.02)
        print(f"Wrote {path}")
    plt.close(fig)


def plot_wrappers(data: dict, out: Path, dpi: int) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(7.0, 3.95), sharey=True)
    fig.subplots_adjust(left=0.19, right=0.995, top=0.90, bottom=0.15, wspace=0.16)
    limits = {}
    for model in MODELS:
        entries = [data[model, rel, name]["delta"]
                   for rel in RELATIONS for name in WRAPPERS]
        low = min(0, *(item[1] for item in entries))
        high = max(0, *(item[2] for item in entries))
        pad = 0.06 * (high - low)
        limits[model] = (low - pad, high + pad)

    for ax, (model, relation) in zip(axes, PANELS):
        for y, (name, colour) in enumerate(zip(WRAPPERS, COLOURS)):
            mid, low, high = data[model, relation, name]["delta"]
            ax.errorbar(mid, y, xerr=[[mid - low], [high - mid]], fmt="o",
                        color=colour, markersize=3.2, capsize=1.5,
                        elinewidth=1, capthick=0.8, zorder=3)
        ax.axvline(0, color="#777777", lw=0.8, zorder=2)
        for boundary in (7.5, 11.5, 15.5):
            ax.axhline(boundary, color=GRID, lw=0.6, zorder=0)
        ax.set_ylim(len(WRAPPERS) - 0.4, -0.6)
        ax.set_xlim(*limits[model])
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4, steps=[1, 2, 2.5, 5, 10]))
        ax.xaxis.grid(True, color=GRID, linewidth=0.55, zorder=0)
        ax.set_axisbelow(True)
        ax.tick_params(length=0, labelsize=7, pad=3)
        ax.set_yticks(range(len(WRAPPERS)), labels=WRAPPERS)
        n = data[model, relation, "none"]["n"]
        ax.set_title(f"{relation.capitalize()} ($n={n}$)", fontsize=8, pad=4)

    for model, pair in zip(MODELS, (axes[:2], axes[2:])):
        center = (pair[0].get_position().x0 + pair[1].get_position().x1) / 2
        fig.text(center, 0.98, model, ha="center", va="center", fontsize=9.5)
    fig.text(0.59, 0.067, r"Mean margin change $\Delta M$ from no wrapper",
             ha="center", fontsize=8)
    handles = [Line2D([], [], marker="o", ls="", color=colour, markersize=4, label=label)
               for colour, label in (
                   (BLUE, "Content / trust labels"), (GREEN, "Distrust labels"),
                   (ORANGE, "Arbitrary names"), (GREY, "Other delimiters"))]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0),
               ncol=4, frameon=False, fontsize=7, handletextpad=0.3, borderaxespad=0,
               columnspacing=1.1)
    save(fig, out, "fig1_wrapper_effects", dpi)


def swarm_y(ax: plt.Axes, values: list[float], center: float,
            marker_size: float) -> np.ndarray:
    """Separate overlapping dots vertically. Never move their measured x values."""
    pixels = ax.transData.transform(np.column_stack((values, np.full(len(values), center))))
    separation = marker_size * ax.figure.dpi / 72 * 1.12
    placed = []
    positions = np.empty(len(values))
    for index in np.argsort(values, kind="stable"):
        px, py = pixels[index]
        candidates = [0.0]
        for x, y in placed:
            distance_x = abs(px - x)
            if distance_x < separation:
                clearance = np.sqrt(separation ** 2 - distance_x ** 2) + 1e-6
                candidates.extend((y - py + clearance, y - py - clearance))
        for offset in sorted(candidates, key=lambda v: (abs(v), -v)):
            if all((px - x) ** 2 + (py + offset - y) ** 2 >= separation ** 2 - 1e-9
                   for x, y in placed):
                placed.append((px, py + offset))
                positions[index] = ax.transData.inverted().transform((px, py + offset))[1]
                break
    if max(abs(positions - center)) > 0.28:
        raise ValueError("Name dots need more vertical space. Increase the figure height.")
    return positions


def plot_names(data: dict, out: Path, dpi: int) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 3.45))
    fig.subplots_adjust(left=0.16, right=0.995, top=0.88, bottom=0.16,
                        wspace=0.12, hspace=0.58)
    for model in MODELS:
        values = [point["gap"] for relation in RELATIONS
                  for group in ("random", "meaningful")
                  for point in data[model, relation][group]]
        low, high = min(0, min(values)), max(0, max(values))
        pad = (high - low) * 0.09
        for ax, (panel_model, relation) in zip(axes.flat, PANELS):
            if panel_model != model:
                continue
            ax.set_xlim(low - pad, high + pad)
            ax.set_ylim(-0.47, 1.52)
            ax.axvline(0, color="#777777", lw=0.9, zorder=1)
            ax.xaxis.grid(True, color=GRID, linewidth=0.55, zorder=0)
            ax.set_axisbelow(True)
            ax.xaxis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 2.5, 5, 10]))
            ax.set_yticks((1.0, 0.0), labels=("Random names\n($n=30$)",
                                              "Meaningful names\n($n=6$)"))
            ax.tick_params(length=0, labelsize=7.5, pad=4)
            if relation == "capitals":
                ax.tick_params(labelleft=False)
            ax.set_title(f"{model} · {relation}", loc="left", fontsize=8.5, pad=16)
            positives = data[model, relation]["positive"]
            ax.text(0, 1.025, f"{positives}/30 random-name gaps > 0",
                    transform=ax.transAxes, ha="left", fontsize=7.5, color="#555555")
    # Swarm positions depend on the final axis dimensions, in display units.
    fig.canvas.draw()
    for ax, key in zip(axes.flat, PANELS):
        panel = data[key]
        for group, center, colour in (("random", 1.0, ORANGE), ("meaningful", 0.0, BLUE)):
            values = [point["gap"] for point in panel[group]]
            y = swarm_y(ax, values, center, marker_size=3.6)
            ax.plot(values, y, "o", ms=3.6, color=colour, markeredgewidth=0,
                    linestyle="none", zorder=3)
            summary_y = center - 0.34
            if group == "random":
                mean, low, high = panel["summary"]
                ax.errorbar(mean, summary_y, xerr=[[mean - low], [high - mean]],
                            fmt="D", color=INK, markersize=3.4, capsize=2,
                            elinewidth=1.2, zorder=4)
            else:
                # The fixed set has no group-level crossed CI in the reports.
                ax.plot(float(np.mean(values)), summary_y, "D", color=INK,
                        markersize=3.4, zorder=4)
    fig.text(0.57, 0.073, r"Mean margin gap $M_{\mathrm{tag}}-M_{\mathrm{colon}}$",
             ha="center", fontsize=8)
    handles = [Line2D([], [], marker="o", ls="", color=GREY, ms=4, label="One name"),
               Line2D([], [], marker="D", ls="", color=INK, ms=3.4, label="Group mean"),
               Line2D([], [], color=INK, lw=1.2, label="95% CI for random-name mean")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0),
               ncol=3, frameon=False, fontsize=7, handletextpad=0.4,
               columnspacing=1.2, borderaxespad=0)
    save(fig, out, "fig2_name_gaps", dpi)


def percent(value: float) -> str:
    return f"{value:g}%"


def plot_guards(data: dict, cell: str, out: Path, dpi: int) -> None:
    assertion = cell == "assert_r1"
    wordings = ("none", *WARNINGS) if assertion else WARNINGS
    row_labels = {"none": "No warning", "falsehood": "Falsehood warning",
                  "instruction": "Instruction warning", "combined": "Combined warning"}
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 3.0 if assertion else 2.6))
    fig.subplots_adjust(left=0.19, right=0.995, top=0.92,
                        bottom=0.17 if assertion else 0.19, wspace=0.12, hspace=0.50)
    cmap = plt.get_cmap("Blues")
    for ax, (model, relation) in zip(axes.flat, PANELS):
        values = np.array([[data[model, relation, cell, w, p][0]
                            for p in POSITIONS] for w in wordings])
        im = ax.imshow(values, cmap=cmap, vmin=0, vmax=100, aspect="auto")
        for (row, col), value in np.ndenumerate(values):
            ax.text(col, row, percent(value), ha="center", va="center", fontsize=8.5,
                    color="white" if value >= 60 else INK)
        ax.set_title(f"{model} · {relation}", loc="left", fontsize=8.5, pad=4)
        ax.set_xticks(range(3), labels=("System", "Above block", "Below block"))
        ax.set_yticks(range(len(wordings)), labels=[row_labels[w] for w in wordings])
        ax.tick_params(axis="both", length=0, pad=3, labelsize=8)
        if relation == "capitals":
            ax.tick_params(labelleft=False)
        ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(wordings), 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=1.5)
        ax.tick_params(which="minor", length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
    bar_y, bar_height = (0.06 if assertion else 0.07), 0.025
    color_ax = fig.add_axes((0.42, bar_y, 0.40, bar_height))
    colorbar = fig.colorbar(im, cax=color_ax, orientation="horizontal",
                           ticks=(0, 25, 50, 75, 100))
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(length=0, labelsize=7, pad=2)
    fig.text(0.40, bar_y + bar_height / 2, "False-answer rate (%)",
             ha="right", va="center", fontsize=8)
    name = "appendix_assertion_guards" if assertion else "fig3_instruction_guards"
    save(fig, out, name, dpi)


def write_values(wrappers: dict, guards: dict, out: Path) -> None:
    with (out / "wrapper_values.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("model", "relation", "wrapper", "n", "rate_percent",
                         "rate_ci_low", "rate_ci_high", "mean_margin", "margin_ci_low",
                         "margin_ci_high", "delta_margin", "delta_ci_low", "delta_ci_high"))
        for (model, relation, name), item in wrappers.items():
            writer.writerow((model, relation, name, item["n"], *item["rate"],
                             *item["margin"], *(item["delta"] or ("", "", ""))))
    with (out / "guard_values.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("model", "relation", "content", "warning", "position",
                         "rate_percent", "mean_margin"))
        for key, value in guards.items():
            writer.writerow((*key, *value))


def write_name_values(data: dict, out: Path) -> None:
    with (out / "name_values.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("model", "relation", "group", "name", "tag_minus_colon_margin",
                         "tag_delta", "colon_delta", "tag_rate_percent", "colon_rate_percent"))
        for (model, relation), panel in data.items():
            for group in ("random", "meaningful"):
                for point in panel[group]:
                    writer.writerow((model, relation, group, point["name"], point["gap"],
                                     *(point.get(k, "") for k in
                                       ("tag_delta", "label_delta", "tag_rate", "label_rate"))))
    with (out / "name_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("model", "relation", "group", "n_names", "mean_gap", "ci_low",
                         "ci_high", "positive_names", "p_across_names", "source"))
        for (model, relation), panel in data.items():
            writer.writerow((model, relation, "random", 30, *panel["summary"],
                             panel["positive"], panel["p"], panel["source"]))
            values = [point["gap"] for point in panel["meaningful"]]
            writer.writerow((model, relation, "meaningful", 6, float(np.mean(values)),
                             "", "", sum(x > 0 for x in values), "", "stats_report.md, E12"))


CAPTIONS = r"""% Copy each caption into the matching figure environment.
% PDF exports are tightly cropped. Use width=\textwidth in a figure* environment.

% fig1_wrapper_effects.pdf
\caption{Wrapper effects for attributed false assertions. Points show the mean
change in answer margin from the same paragraph without a wrapper. Bars show
95\% paired bootstrap confidence intervals over facts. A positive change means
greater relative preference for the assigned false answer. Each tag is next to
its colon-label form. The two models use different horizontal scales. Within
each model, both datasets use the same scale.}
\label{fig:wrapper-effects}

% fig2_name_gaps.pdf
\caption{Tag-versus-colon differences across names. Each coloured point is one
name's mean answer margin under tags minus its mean margin under a colon label.
Positive values mean greater relative preference for the false answer under
tags. Each panel shows 30 random names and the six tested meaningful names.
Black diamonds show group means. Horizontal intervals show the reported
95\% crossed bootstrap confidence intervals over names and facts for the
random-name means. No group-level interval is shown for the six meaningful
names. Vertical offsets separate overlapping points and have no numeric
meaning. The two models use different horizontal scales.}
\label{fig:name-gaps}

% fig3_instruction_guards.pdf
\caption{Warnings against an embedded instruction inside a
\texttt{<document>} wrapper. Cells show the percentage of outputs matching the
assigned false answer. The no-warning rate is 100\% in all four panels.
Each warning text is placed in the system prompt, above the block in the user
turn, or below the block in the user turn. All panels use the same colour scale.}
\label{fig:instruction-guards}

% appendix_assertion_guards.pdf
\caption{Warnings against an attributed false assertion inside a
\texttt{<document>} wrapper. Cells show the percentage of outputs matching the
assigned false answer. The no-warning row is repeated across columns for
reference. All panels use the same colour scale as
Figure~\ref{fig:instruction-guards}.}
\label{fig:assertion-guards}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path, default=Path("stats_report.md"))
    parser.add_argument("--results", type=Path,
                        help="Result root containing gemma4_12b_conflict and qwen36_27b_conflict.")
    parser.add_argument("--gemma-nonsense-report", type=Path,
                        help="Explicit Gemma E13 Markdown report path.")
    parser.add_argument("--qwen-nonsense-report", type=Path,
                        help="Explicit Qwen E13 Markdown report path.")
    parser.add_argument("--out", type=Path, default=Path("figures"))
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    if args.dpi < 72:
        parser.error("--dpi must be at least 72.")
    report_dir = Path(__file__).resolve().parent / "reports"
    name_reports = {}
    for model, slug, folder, explicit in (
        (MODELS[0], "gemma", "gemma4_12b_conflict", args.gemma_nonsense_report),
        (MODELS[1], "qwen", "qwen36_27b_conflict", args.qwen_nonsense_report),
    ):
        if explicit is not None:
            path = explicit
        elif args.results is not None:
            path = args.results / folder / "analysis" / "nonsense_strings" / "nonsense_report.md"
        else:
            path = report_dir / f"{slug}_nonsense_report.md"
        name_reports[model] = path
    try:
        wrappers, guards = load_data(args.report)
        names = load_names(args.report, name_reports)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    args.out.mkdir(parents=True, exist_ok=True)
    configure_style()
    plot_wrappers(wrappers, args.out, args.dpi)
    plot_names(names, args.out, args.dpi)
    plot_guards(guards, "explicit_stipulation", args.out, args.dpi)
    plot_guards(guards, "assert_r1", args.out, args.dpi)
    write_values(wrappers, guards, args.out)
    write_name_values(names, args.out)
    (args.out / "captions.tex").write_text(CAPTIONS, encoding="utf-8")
    print("All three main figures and the appendix warning figure are ready.")


if __name__ == "__main__":
    main()
