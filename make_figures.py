#!/usr/bin/env python3
"""Build every figure and the qualitative example block for the write-up.

Figures come from the per-cell CSVs the experiment scripts write under
results/, so this runs on a laptop with no GPU and no model. The example block
needs the raw per-prompt JSONL (which carries the prompt text and the model's
actual output); if those files are absent the script says so and still writes
the figures. A figure whose inputs are missing is skipped with a note.

    python make_figures.py --results results --out figures

By default this reads the expanded runs (delimiter_v2, channel_v2,
nonsense_strings). To redraw the original write-up's figures:

    python make_figures.py --delimiter-dir delimiter --channel-dir channel

Palette: the three categorical hues are slots 1-3 of the reference theme,
which validate on the all-pairs list (scatter, small multiples) as well as the
adjacent list (bars). Colour encodes what a thing *is* -- a wrapper's kind, a
warning's wording -- never its rank, so a ladder can be re-sorted without
repainting anything. The scatter adds marker shape so identity is never
colour alone.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import textwrap
from pathlib import Path
from typing import Any, Mapping, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from E11_source_channel import GUARD_CHANNELS, GUARDS, SLOTS
from E12_delimiter import IRRELEVANT_CELL, WRAPPERS


# --- palette -------------------------------------------------------------
# Slots 1-3 of the reference categorical theme; these three validate on the
# all-pairs list (scatter) as well as the adjacent list (bars).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK_2, INK_3 = "#0b0b0b", "#52514e", "#8b8a85"
GRID, SURFACE = "#e6e5e1", "#ffffff"
# Sequential blue ramp, light -> dark, for the one ordered encoding (Figure 1).
BLUE_RAMP = ["#9ec5f4", "#5598e7", "#2a78d6", "#184f95"]

MODELS = (("gemma", "Gemma 4 12B"), ("qwen", "Qwen 3.6 27B"))
MODEL_DIRS = {"gemma": "gemma4_12b_conflict", "qwen": "qwen36_27b_conflict"}
RELATIONS = (("element_symbol", "elements"), ("country_capital", "capitals"))

# What each wrapper is, which is what colour encodes.
ROLE = {
    "tag_document": "named", "tag_passage": "named", "tag_search": "named",
    "tag_trusted": "named",
    "label_document": "named", "label_passage": "named", "label_search": "named",
    "label_trusted": "named",
    "tag_nonsense": "meaningless", "tag_gibberish": "meaningless",
    "tag_empty": "meaningless", "label_nonsense": "meaningless",
    "label_gibberish": "meaningless",
    "tag_untrusted": "negative", "tag_unreliable": "negative",
    "label_untrusted": "negative", "label_unreliable": "negative",
    "inline": "plain", "blankline": "plain", "dashes": "plain", "quotes": "plain",
}
ROLE_COLOUR = {"named": BLUE, "meaningless": ORANGE, "negative": AQUA, "plain": INK_3}
ROLE_MARKER = {"named": "o", "meaningless": "s", "negative": "^", "plain": "D"}
ROLE_LABEL = {
    "named": "names a content type",
    "meaningless": "no meaning",
    "negative": "warns about the source",
    "plain": "layout only / none",
}
# How each wrapper is written in the write-up.
PRETTY = {
    "inline": "none (baseline)", "blankline": "blank lines only",
    "dashes": "--- fence", "quotes": '""" fence',
    "tag_document": "<document>", "tag_passage": "<passage>",
    "tag_search": "<search_result>",
    "tag_empty": "<>", "tag_untrusted": "<untrusted_content>",
    "tag_unreliable": "<unreliable_source>", "tag_trusted": "<trusted_content>",
    "tag_nonsense": "<qzx_block>", "tag_gibberish": "<qzxzxew>",
    "label_nonsense": "Qzx_block:", "label_gibberish": "Qzxzxew:",
    "label_document": "Document:", "label_passage": "Passage:",
    "label_search": "Search result:", "label_untrusted": "Untrusted content:",
    "label_unreliable": "Unreliable source:", "label_trusted": "Trusted content:",
}
if set(ROLE) != set(WRAPPERS) or set(PRETTY) != set(WRAPPERS):
    raise RuntimeError("ROLE and PRETTY must cover exactly E12's WRAPPERS")

# Figure 3: colour is the warning's wording; grey is no warning at all.
GUARD_COLOUR = {"falsehood": BLUE, "instruction": ORANGE, "combined": AQUA}
GUARD_LABEL = {
    "falsehood": "warns of false statements",
    "instruction": "warns of instructions",
    "combined": "warns of both",
}
SLOT_LABEL = {"system": "system prompt", "above": "user turn, above",
              "below": "user turn, below"}
CHANNEL_OF = {spec: channel for channel, spec in GUARD_CHANNELS.items()}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as handle:
        return list(csv.DictReader(handle))


def number(row: Mapping[str, Any] | None, key: str) -> float:
    """A float from a CSV row; NaN when the row or the column is missing."""
    if row is None:
        return float("nan")
    try:
        return float(row.get(key, "nan") or "nan")
    except ValueError:
        return float("nan")


def style_axes(ax: plt.Axes, *, xgrid: bool = True) -> None:
    """Hairline recessive chrome: no box, one solid grid direction."""
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(colors=INK_2, labelsize=8, length=0)
    if xgrid:
        ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
    ax.set_facecolor(SURFACE)


def save(fig: plt.Figure, out: Path, name: str) -> None:
    path = out / f"{name}.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"  wrote {path}")


def skip(name: str, reason: str) -> None:
    print(f"  skipped {name}: {reason}")


# --- figure 1: the headline ----------------------------------------------

def figure_headline(data: Mapping[str, Any], out: Path) -> None:
    """Four prompts, two models, two datasets: the thesis in one picture.

    Colour separates the two things being compared -- a wrapper (blue, two
    strengths) against an explicit instruction (orange) -- with the unwrapped
    baseline in neutral grey, rather than giving every bar its own hue.
    """
    if data["headline"] is None:
        return skip("fig1_headline", "needs E12 (inline, <qzx_block>, <document>) and E8 for both models")
    conditions = [
        ("no wrapper", INK_3),
        ("<qzx_block>", BLUE_RAMP[1]),
        ("<document>", BLUE_RAMP[3]),
        ("explicit instruction", ORANGE),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 5.6), sharex=True)
    for row, (model, model_label) in enumerate(MODELS):
        for col, (relation, relation_label) in enumerate(RELATIONS):
            ax = axes[row][col]
            rates = data["headline"][(model, relation)]
            for y, (label, colour) in enumerate(conditions):
                rate, margin = rates[label]
                ax.barh(y, rate * 100, height=0.62, color=colour, zorder=3)
                if rate == 0:
                    # A zero bar must still read as a measured zero, not as
                    # missing data.
                    ax.plot([0, 0], [y - 0.31, y + 0.31], color=colour,
                            lw=2.4, solid_capstyle="butt", zorder=3)
                ax.text(rate * 100 + 2.5, y,
                        f"{rate * 100:.0f}% ({margin:.1f})",
                        va="center", ha="left", fontsize=7.5, color=INK_2)
            ax.set_yticks(range(len(conditions)))
            ax.set_yticklabels([c[0] for c in conditions] if col == 0 else [])
            ax.set_ylim(len(conditions) - 0.5, -0.5)
            ax.set_xlim(0, 132)
            ax.set_xticks([0, 25, 50, 75, 100])
            ax.set_title(f"{model_label} · {relation_label}",
                         fontsize=9, color=INK, loc="left", pad=6)
            style_axes(ax)
    for ax in axes[1]:
        ax.set_xlabel("paragraph rate (%)", fontsize=8, color=INK_2)
    fig.suptitle("Tags vs explicit instruction",
                 fontsize=11.5, color=INK, x=0.008, ha="left", y=1.005)
    fig.text(0.008, 0.955,
             "The same false claim throughout. Only what surrounds it changes. "
             "Labels are the paragraph rate and M.",
             fontsize=8, color=INK_2, ha="left")
    fig.tight_layout(rect=(0, 0.02, 1, 0.945))
    save(fig, out, "fig1_headline")


# --- figure 2: the wrapper ladder ----------------------------------------

def figure_ladder(data: Mapping[str, Any], out: Path, relation: str,
                  relation_label: str, name: str) -> None:
    """Every wrapper for one dataset, both models, coloured by what it is.

    Margin rather than rate on the x-axis, because Gemma saturates at 0% and
    100% across most of this range and the rate stops resolving anything.
    Whiskers are the 95% bootstrap CI of ΔM against no wrapper, where the CSV
    carries it.

    Row order is always the Gemma element-symbol ranking, whichever dataset is
    being drawn, so the two ladder figures line up row for row.
    """
    if any(data["delimiter"][m] is None for m, _ in MODELS):
        return skip(name, "needs E12 delimiter_cells.csv for both models")
    order = [w for w in data["ladder_order"]
             if all((relation, w, "assert_r1") in data["delimiter"][m] for m, _ in MODELS)]
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 0.33 * len(order) + 1.0), sharey=True)
    drew_ci = False
    for ax, (model, model_label) in zip(axes, MODELS):
        cells = data["delimiter"][model]
        baseline = number(cells[(relation, "inline", "assert_r1")], "mean_margin")
        # Data extent, so a label for a bar ending near the left edge can be
        # moved right of the baseline instead of running into the row names.
        extent = [baseline]
        for wrapper in order:
            row = cells[(relation, wrapper, "assert_r1")]
            extent += [number(row, "mean_margin")] + [
                baseline + number(row, key) for key in ("delta_ci_low", "delta_ci_high")
                if math.isfinite(number(row, key))]
        left, span = min(extent), (max(extent) - min(extent)) or 1.0
        for y, wrapper in enumerate(order):
            row = cells[(relation, wrapper, "assert_r1")]
            margin, rate = number(row, "mean_margin"), number(row, "context_rate")
            colour = ROLE_COLOUR[ROLE[wrapper]]
            ax.barh(y, margin - baseline, left=baseline, height=0.62,
                    color=colour, zorder=3)
            low, high = number(row, "delta_ci_low"), number(row, "delta_ci_high")
            reach = margin
            if wrapper != "inline" and math.isfinite(low) and math.isfinite(high):
                ax.plot([baseline + low, baseline + high], [y, y], color=INK,
                        lw=0.9, solid_capstyle="butt", zorder=4)
                reach = baseline + (high if margin >= baseline else low)
                drew_ci = True
            rightward = margin >= baseline or (reach - left) < 0.15 * span
            anchor = reach if margin >= baseline else (baseline if rightward else reach)
            ax.text(anchor + (0.012 if rightward else -0.012) * span, y,
                    f"{rate * 100:.0f}% ({margin:.1f})",
                    va="center", ha="left" if rightward else "right",
                    fontsize=7, color=INK_2, zorder=4)
        ax.axvline(baseline, color=INK_3, lw=1.0, zorder=2, ymax=0.96)
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels([PRETTY[w] for w in order], fontsize=8)
        ax.set_xlabel("M (logits)", fontsize=8, color=INK_2)
        ax.set_title(model_label, fontsize=9.5, color=INK, loc="left", pad=16)
        style_axes(ax)
    # sharey: one explicit inverted range for both panels.
    axes[0].set_ylim(len(order) - 0.4, -1.5)
    handles = [Line2D([], [], color=ROLE_COLOUR[r], lw=6, label=ROLE_LABEL[r])
               for r in ("named", "meaningless", "negative", "plain")]
    if drew_ci:
        handles.append(Line2D([], [], color=INK, lw=0.9, label="95% CI of ΔM"))
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False,
               fontsize=8, bbox_to_anchor=(0.5, -0.035), labelcolor=INK_2)
    fig.suptitle(
        f"The wrapper ladder — {relation_label}",
        fontsize=11.5, color=INK, x=0.008, ha="left", y=1.012,
    )
    fig.text(
        0.008, 0.963,
        "Bars run from each model's own no-wrapper baseline, so bar length is ΔM. "
        "Labels are the paragraph rate and M. The x-scales differ for the two models.",
        fontsize=8, color=INK_2, ha="left",
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    save(fig, out, name)


# --- figure 3: which warning, where --------------------------------------

def figure_guards(data: Mapping[str, Any], out: Path) -> None:
    """Three warning wordings in three slots, against two document contents.

    Columns separate what the document contains, because that -- not the
    slot -- decided whether the original warning worked. Colour is the
    warning's wording; grey is the same <document> block with no warning.
    """
    if any(data["channel"][m] is None for m, _ in MODELS):
        return skip("fig3_guards", "needs E11 channel_cells.csv for both models")
    contents = (("assert_r1", "a false assertion"), ("explicit_stipulation", "an instruction"))
    columns = [(relation, relation_label, cell, cell_label)
               for relation, relation_label in RELATIONS for cell, cell_label in contents]
    # y layout: the no-warning bar, then one group of three bars per slot.
    bars: list[tuple[str, str | None, float]] = [("delimited", None, 0.0)]
    ticks: list[tuple[float, str]] = [(0.0, "no warning")]
    y = 1.3
    for slot in SLOTS:
        start = y
        for guard in GUARDS:
            bars.append((CHANNEL_OF[(guard, slot)], guard, y))
            y += 0.8
        ticks.append(((start + y - 0.8) / 2, SLOT_LABEL[slot]))
        y += 0.5
    bottom = y - 0.5 + 0.4

    fig, axes = plt.subplots(2, 4, figsize=(12.2, 6.6), sharex=True)
    for row, (model, model_label) in enumerate(MODELS):
        for col, (relation, relation_label, cell, cell_label) in enumerate(columns):
            ax = axes[row][col]
            cells = data["channel"][model]
            for channel, guard, ypos in bars:
                entry = cells.get((relation, cell, channel))
                if entry is None:
                    continue
                rate = number(entry, "context_rate")
                colour = INK_3 if guard is None else GUARD_COLOUR[guard]
                ax.barh(ypos, rate * 100, height=0.66, color=colour, zorder=3)
                if rate == 0:
                    ax.plot([0, 0], [ypos - 0.33, ypos + 0.33], color=colour,
                            lw=2.2, solid_capstyle="butt", zorder=3)
                ax.text(rate * 100 + 3, ypos, f"{rate * 100:.0f}%",
                        va="center", ha="left", fontsize=6.5, color=INK_2)
            ax.set_yticks([t for t, _ in ticks])
            ax.set_yticklabels([label for _, label in ticks] if col == 0 else [])
            ax.set_ylim(bottom, -0.6)
            ax.set_xlim(0, 128)
            ax.set_xticks([0, 50, 100])
            ax.set_title(f"{model_label} · {relation_label}\ndocument holds {cell_label}",
                         fontsize=8, color=INK, loc="left", pad=6)
            style_axes(ax)
    for ax in axes[1]:
        ax.set_xlabel("paragraph rate (%)", fontsize=8, color=INK_2)
    handles = [Line2D([], [], color=INK_3, lw=6, label="no warning")]
    handles += [Line2D([], [], color=GUARD_COLOUR[g], lw=6, label=GUARD_LABEL[g]) for g in GUARDS]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               fontsize=8, bbox_to_anchor=(0.5, -0.04), labelcolor=INK_2)
    fig.suptitle("Which warning undoes a wrapped false claim, and from where",
                 fontsize=11.5, color=INK, x=0.008, ha="left", y=1.005)
    fig.text(0.008, 0.952,
             "The same <document> block throughout; the warning's wording and slot change. "
             "Labels are the paragraph rate; margins are in results/stats.",
             fontsize=8, color=INK_2, ha="left")
    fig.tight_layout(rect=(0, 0.02, 1, 0.94))
    save(fig, out, "fig3_guards")


# --- figure 4: thirty meaningless names -----------------------------------

def spread(values: Sequence[float], minimum_gap: float) -> list[float]:
    """Nudge label positions apart so annotations do not overlap."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    placed = list(values)
    for previous, current in zip(order, order[1:]):
        if placed[current] - placed[previous] < minimum_gap:
            placed[current] = placed[previous] + minimum_gap
    return placed


def figure_nonsense(data: Mapping[str, Any], out: Path) -> None:
    """Every random name twice -- as `Name:` and as `<name>` -- joined by a line.

    Position is the form, so each line's slope is that name's bracket effect.
    Dots are orange because every name here means nothing, as in the ladder.
    The two original strings are drawn as diamonds, and E12's <document> as a
    dashed line for scale.
    """
    if any(data["nonsense_strings"][m] is None for m, _ in MODELS):
        return skip("fig4_nonsense", "needs E13 nonsense_strings.csv for both models")
    fig, axes = plt.subplots(2, 2, figsize=(8.8, 7.4), sharey="row")
    for row, (model, model_label) in enumerate(MODELS):
        for col, (relation, relation_label) in enumerate(RELATIONS):
            ax = axes[row][col]
            strings = [r for r in data["nonsense_strings"][model]
                       if r["relation"] == relation and r["cell"] == "assert_r1"]
            if not strings:
                ax.set_axis_off()
                continue
            label = [number(r, "label_delta") for r in strings]
            tag = [number(r, "tag_delta") for r in strings]
            for a, b in zip(label, tag):
                ax.plot([0, 1], [a, b], color=INK_3, lw=0.7, alpha=0.55, zorder=2)
            for x, values in ((0, label), (1, tag)):
                ax.scatter([x] * len(values), values, s=22, color=ORANGE,
                           edgecolor=SURFACE, linewidth=0.8, zorder=3)
                middle = statistics.median(values)
                ax.plot([x - 0.16, x + 0.16], [middle, middle], color=INK, lw=2.0,
                        solid_capstyle="butt", zorder=4)
            ax.axhline(0, color=INK_3, lw=0.8, zorder=1)
            refs = [r for r in (data["nonsense_cells"][model] or [])
                    if r["relation"] == relation and r["cell"] == "assert_r1"
                    and r.get("wrapper_source") == "reference" and r.get("form") in ("tag", "label")]
            low, high = min(label + tag + [0.0]), max(label + tag + [0.0])
            document = number((data["delimiter"].get(model) or {}).get(
                (relation, "tag_document", "assert_r1")), "delta_vs_inline")
            if math.isfinite(document):
                ax.axhline(document, color=BLUE, lw=1.0, ls=(0, (4, 3)), zorder=1)
                ax.annotate("<document>, E12", (1.62, document), xytext=(0, 2),
                            textcoords="offset points", fontsize=7, color=INK_2,
                            va="bottom", ha="right")
                high = max(high, document)
            gap = 0.045 * (high - low or 1.0)
            for form, x, side in (("label", 0, -1), ("tag", 1, 1)):
                these = [r for r in refs if r["form"] == form]
                ys = [number(r, "delta_vs_inline") for r in these]
                for r, yv, yt in zip(these, ys, spread(ys, gap)):
                    ax.scatter([x], [yv], s=40, marker="D", facecolor=SURFACE,
                               edgecolor=INK, linewidth=1.1, zorder=5)
                    ax.text(x + 0.1 * side, yt, PRETTY.get(r["wrapper"], r["wrapper"]),
                            fontsize=7, color=INK_2, va="center",
                            ha="left" if side > 0 else "right")
            higher = sum(1 for a, b in zip(label, tag) if b > a)
            ax.set_xticks([0, 1])
            ax.set_xticklabels(["as a label  Name:", "as a tag  <name>"], fontsize=8)
            ax.set_xlim(-0.75, 1.65)
            if col == 0:
                ax.set_ylabel("ΔM against no wrapper (logits)", fontsize=8, color=INK_2)
            ax.set_title(f"{model_label} · {relation_label}\n"
                         f"{higher}/{len(strings)} names score higher as a tag",
                         fontsize=8.5, color=INK, loc="left", pad=6)
            style_axes(ax, xgrid=False)
            ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
            ax.set_axisbelow(True)
    handles = [
        Line2D([], [], marker="o", ls="none", color=ORANGE, markersize=6,
               label="random name"),
        Line2D([], [], color=INK_3, lw=0.8, label="same name, both forms"),
        Line2D([], [], color=INK, lw=2.0, label="median"),
        Line2D([], [], marker="D", ls="none", markerfacecolor=SURFACE,
               markeredgecolor=INK, markersize=6, label="the two original strings"),
        Line2D([], [], color=BLUE, lw=1.0, ls=(0, (4, 3)), label="<document> (E12)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False,
               fontsize=8, bbox_to_anchor=(0.5, -0.035), labelcolor=INK_2)
    fig.suptitle("Thirty meaningless names, with and without brackets",
                 fontsize=11.5, color=INK, x=0.008, ha="left", y=1.005)
    fig.text(0.008, 0.955,
             "Each random 8-letter name around the identical false claim, once as a "
             "label and once as a tag. The y-scales differ for the two models.",
             fontsize=8, color=INK_2, ha="left")
    fig.tight_layout(rect=(0, 0.03, 1, 0.945))
    save(fig, out, "fig4_nonsense")


# --- figure 5: claim or salient token? -----------------------------------

def figure_relevance(data: Mapping[str, Any], out: Path) -> None:
    """Each wrapper's effect when the paragraph is about the queried subject (x)
    against its effect when the same sentence names another subject (y).

    On the diagonal, the wrapper's whole effect would survive without the
    claim -- pure priming of the false answer's token. On zero, none of it does.
    """
    needed = [(relation, IRRELEVANT_CELL) for relation, _ in RELATIONS]
    if any(data["delimiter"][m] is None for m, _ in MODELS) or not all(
        any(k[0] == rel and k[2] == cell for k in data["delimiter"][m])
        for m, _ in MODELS for rel, cell in needed
    ):
        return skip("fig5_relevance", f"needs the {IRRELEVANT_CELL} cell in E12 for both models")
    # Label offsets (points). <qzx_block> goes below its marker: the named
    # wrappers cluster just above and to its right.
    annotate = {"tag_document": (4, 6, "left"), "tag_nonsense": (0, -13, "center"),
                "tag_untrusted": (6, 8, "left")}
    fig, axes = plt.subplots(2, 2, figsize=(8.6, 8.4))
    for row, (model, model_label) in enumerate(MODELS):
        for col, (relation, relation_label) in enumerate(RELATIONS):
            ax = axes[row][col]
            cells = data["delimiter"][model]
            points = []
            for wrapper in ROLE:
                if wrapper == "inline":
                    continue
                x = number(cells.get((relation, wrapper, "assert_r1")), "delta_vs_inline")
                y = number(cells.get((relation, wrapper, IRRELEVANT_CELL)), "delta_vs_inline")
                if math.isfinite(x) and math.isfinite(y):
                    points.append((wrapper, x, y))
            values = [v for _, x, y in points for v in (x, y)] + [0.0]
            pad = 0.06 * (max(values) - min(values) or 1.0)
            low, high = min(values) - pad, max(values) + pad
            ax.plot([low, high], [low, high], color=INK_3, lw=0.9, ls=(0, (4, 3)), zorder=1)
            ax.axhline(0, color=INK_3, lw=0.8, zorder=1)
            ax.axvline(0, color=GRID, lw=0.8, zorder=0)
            for wrapper, x, y in points:
                role = ROLE[wrapper]
                ax.scatter([x], [y], s=34, marker=ROLE_MARKER[role], color=ROLE_COLOUR[role],
                           edgecolor=SURFACE, linewidth=1.0, zorder=3)
                if wrapper in annotate:
                    dx, dy, ha = annotate[wrapper]
                    ax.annotate(PRETTY[wrapper], (x, y), xytext=(dx, dy),
                                textcoords="offset points", fontsize=7, color=INK_2,
                                ha=ha, va="center")
            corner = low + 0.92 * (high - low)
            ax.annotate("all priming", (corner, corner), xytext=(-4, 4),
                        textcoords="offset points", fontsize=7, color=INK_3,
                        ha="right", va="bottom", rotation=45, rotation_mode="anchor")
            ax.text(high, 0, "no priming", fontsize=7, color=INK_3, ha="right", va="bottom")
            ax.set_xlim(low, high)
            ax.set_ylim(low, high)
            ax.set_aspect("equal", adjustable="box")
            ax.set_title(f"{model_label} · {relation_label}",
                         fontsize=9, color=INK, loc="left", pad=6)
            style_axes(ax)
            ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
            if row == 1:
                ax.set_xlabel("ΔM, paragraph about the queried subject", fontsize=8, color=INK_2)
            if col == 0:
                ax.set_ylabel("ΔM, same sentence about another subject", fontsize=8, color=INK_2)
    handles = [Line2D([], [], marker=ROLE_MARKER[r], ls="none", color=ROLE_COLOUR[r],
                      markersize=6, label=ROLE_LABEL[r])
               for r in ("named", "meaningless", "negative", "plain")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               fontsize=8, bbox_to_anchor=(0.5, -0.02), labelcolor=INK_2)
    fig.suptitle("Does a wrapper need the claim to be about the question?",
                 fontsize=11.5, color=INK, x=0.008, ha="left", y=1.005)
    fig.text(0.008, 0.962,
             "One point per wrapper: its effect on the false answer when the paragraph is "
             "about the queried subject (x) and when it names another subject (y).",
             fontsize=8, color=INK_2, ha="left")
    fig.tight_layout(rect=(0, 0.03, 1, 0.955))
    save(fig, out, "fig5_relevance")


# --- data loading ---------------------------------------------------------

def optional_csv(path: Path) -> list[dict[str, str]] | None:
    if not path.is_file():
        print(f"  NOTE: missing {path}")
        return None
    return read_csv(path)


def load(args: argparse.Namespace) -> dict[str, Any]:
    data: dict[str, Any] = {key: {} for key in (
        "delimiter", "content", "channel", "nonsense_strings", "nonsense_cells")}
    for model, _ in MODELS:
        base = args.results / MODEL_DIRS[model] / "analysis"
        rows = optional_csv(base / args.delimiter_dir / "delimiter_cells.csv")
        data["delimiter"][model] = None if rows is None else {
            (r["relation"], r["wrapper"], r["cell"]): r for r in rows}
        rows = optional_csv(base / args.conventionality_dir / "conventionality_cells.csv")
        data["content"][model] = None if rows is None else {
            (r["relation"], r["cell"]): r for r in rows}
        # Older channel CSVs carry a `policy` column from a second instruction
        # condition the experiment no longer runs; keep only its neutral rows so
        # both the old and the current CSV layout key the same way.
        rows = optional_csv(base / args.channel_dir / "channel_cells.csv")
        data["channel"][model] = None if rows is None else {
            (r["relation"], r["cell"], r["channel"]): r for r in rows
            if r.get("policy", "neutral") == "neutral"}
        data["nonsense_strings"][model] = optional_csv(
            base / args.nonsense_dir / "nonsense_strings.csv")
        data["nonsense_cells"][model] = optional_csv(
            base / args.nonsense_dir / "nonsense_cells.csv")

    headline: dict[tuple[str, str], dict[str, tuple[float, float]]] | None = {}
    for model, _ in MODELS:
        delimiter, content = data["delimiter"][model], data["content"][model]
        for relation, _ in RELATIONS:
            keys = [(relation, w, "assert_r1") for w in ("inline", "tag_nonsense", "tag_document")]
            if (delimiter is None or content is None or headline is None
                    or any(k not in delimiter for k in keys)
                    or (relation, "explicit_stipulation") not in content):
                headline = None
                continue
            cell = {}
            for label, wrapper in (("no wrapper", "inline"),
                                   ("<qzx_block>", "tag_nonsense"),
                                   ("<document>", "tag_document")):
                row = delimiter[(relation, wrapper, "assert_r1")]
                cell[label] = (number(row, "context_rate"), number(row, "mean_margin"))
            row = content[(relation, "explicit_stipulation")]
            cell["explicit instruction"] = (number(row, "context_rate"),
                                            number(row, "mean_margin"))
            headline[(model, relation)] = cell
    data["headline"] = headline

    # One order for every ladder figure, taken from Gemma on element symbols, so
    # the panels can be read against each other row by row.
    gemma = data["delimiter"].get("gemma") or {}
    data["ladder_order"] = sorted(
        ROLE, key=lambda w: -number(gemma.get(("element_symbol", w, "assert_r1")), "mean_margin")
        if ("element_symbol", w, "assert_r1") in gemma else math.inf,
    )
    return data


def print_spearman(data: Mapping[str, Any], permutations: int, seed: int) -> None:
    """Cross-model rank agreement over wrappers, re-derived on every run so the
    numbers quoted in the text cannot drift from the data."""
    (first, _), (second, _) = MODELS
    x_cells, y_cells = data["delimiter"][first], data["delimiter"][second]
    if x_cells is None or y_cells is None:
        return
    from paired_stats import spearman_permutation

    print("cross-model rank agreement over wrappers (not plotted):")
    for relation, _ in RELATIONS:
        for cell in ("assert_r1", "bare", IRRELEVANT_CELL):
            # WRAPPERS order, as make_tables.py uses, so the Monte Carlo p-value
            # printed here is the same number as the one in the tables.
            shared = [w for w in WRAPPERS
                      if (relation, w, cell) in x_cells and (relation, w, cell) in y_cells]
            if len(shared) < 3:
                continue
            result = spearman_permutation(
                [number(x_cells[(relation, w, cell)], "mean_margin") for w in shared],
                [number(y_cells[(relation, w, cell)], "mean_margin") for w in shared],
                permutations, seed,
            )
            print(f"  {relation:16s} {cell:22s} n={result['n']:2d}  "
                  f"Spearman rho = {result['rho']:.2f}  permutation p = {result['p']:.1e}")


# --- qualitative examples -------------------------------------------------

# One fact per dataset under four surroundings; the claim, false answer and
# question are fixed. Entries are (label, source file, identifying fields).
EXAMPLE_VARIANTS = (
    ("no wrapper", "delimiter",
     {"wrapper": "inline", "cell_id": "assert_r1"}),
    ("wrapped in <document>", "delimiter",
     {"wrapper": "tag_document", "cell_id": "assert_r1"}),
    ("wrapped in <qzx_block>", "delimiter",
     {"wrapper": "tag_nonsense", "cell_id": "assert_r1"}),
    ("an explicit instruction instead, no wrapper", "conventionality",
     {"cell_id": "explicit_stipulation", "policy_id": "neutral"}),
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def matches(row: Mapping[str, Any], spec: Mapping[str, Any]) -> bool:
    return all(row.get(key) == value for key, value in spec.items())


def render_example(label: str, row: Mapping[str, Any]) -> str:
    prompt = textwrap.indent(str(row["raw_prompt"]).strip(), "    ")
    followed = ("the paragraph" if row["observed_knowledge_source"] == "contextual"
                else "its own knowledge")
    return (
        f"**{label}**\n\n"
        f"```\n{prompt}\n```\n\n"
        f"> answered **`{row['generated_answer_stripped']}`** · "
        f"true answer `{row['parametric_answer']}` · "
        f"paragraph's answer `{row['context_answer']}` · "
        f"margin {float(row['context_minus_parametric_logprob_margin']):+.1f} "
        f"→ **followed {followed}**\n"
    )


def write_examples(args: argparse.Namespace, seed: int, per_relation: int) -> None:
    """One randomly chosen fact per dataset, shown under all four variants.

    The fact is drawn once and then looked up in each variant, rather than
    sampled per variant -- otherwise the four prompts would be four different
    facts and nothing about them would be comparable.
    """
    base = args.results / MODEL_DIRS["gemma"] / "analysis"
    source_files = {
        "delimiter": (args.delimiter_dir, "delimiter_results.jsonl"),
        "conventionality": (args.conventionality_dir, "conventionality_results.jsonl"),
    }
    sources: dict[str, list[dict[str, Any]]] = {}
    missing: list[str] = []
    for name, (folder, filename) in source_files.items():
        path = base / folder / filename
        if path.exists():
            sources[name] = read_jsonl(path)
        elif str(path) not in missing:
            missing.append(str(path))

    # label -> relation -> fact_id -> row
    index: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
    for label, source, spec in EXAMPLE_VARIANTS:
        by_relation: dict[str, dict[str, dict[str, Any]]] = {}
        for row in sources.get(source, []):
            if row.get("raw_prompt") and matches(row, spec):
                by_relation.setdefault(str(row["relation_id"]), {})[str(row["fact_id"])] = row
        index[label] = by_relation

    labels = [label for label, _, _ in EXAMPLE_VARIANTS]
    rng = random.Random(seed)
    blocks: list[str] = []
    for relation, relation_label in RELATIONS:
        # Only facts present in every variant, so the four prompts below really
        # are the same fact.
        shared: set[str] | None = None
        for label in labels:
            ids = set(index.get(label, {}).get(relation, {}))
            shared = ids if shared is None else (shared & ids)
        candidates = sorted(shared or ())
        if not candidates:
            continue
        for fact_id in rng.sample(candidates, min(per_relation, len(candidates))):
            rows = [index[label][relation][fact_id] for label in labels]
            false_answers = {str(row["context_answer"]) for row in rows}
            if len(false_answers) > 1:
                print(f"  WARNING: {fact_id} carries different false answers across "
                      f"variants ({sorted(false_answers)}) -- not like-for-like")
            subject = fact_id.split(":", 1)[-1].replace("-", " ").title()
            blocks.append(
                f"### {relation_label}: {subject}\n\n"
                "The same fact and the same false answer in all four prompts; "
                "only the surroundings change.\n\n"
                + "\n".join(render_example(label, row) for label, row in zip(labels, rows))
            )

    path = args.out / "examples.md"
    if blocks:
        header = (
            "<!-- Generated by make_figures.py. The fact is drawn at random with "
            "a fixed seed, then shown under every variant. Paste into Section 0. -->\n\n"
        )
        path.write_text(header + "\n---\n\n".join(blocks))
        print(f"  wrote {path} ({len(blocks)} facts x {len(labels)} variants)")
    if missing:
        print("\n  NOTE: no examples written from:")
        for item in missing:
            print(f"    {item}")
        print("  Those files hold the prompt text and the model's actual output.")
        print("  Run the experiment scripts first, or copy the JSONL over.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--out", type=Path, default=Path("figures"))
    parser.add_argument("--delimiter-dir", default="delimiter_v2")
    parser.add_argument("--channel-dir", default="channel_v2")
    parser.add_argument("--nonsense-dir", default="nonsense_strings")
    parser.add_argument("--conventionality-dir", default="conventionality_random")
    parser.add_argument("--permutations", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--examples-per-dataset", type=int, default=1)
    parser.add_argument("--skip-examples", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    print("inputs:")
    data = load(args)
    print("figures:")
    figure_headline(data, args.out)
    figure_ladder(data, args.out, "element_symbol", "elements", "fig2a_ladder_elements")
    figure_ladder(data, args.out, "country_capital", "capitals", "fig2b_ladder_capitals")
    figure_guards(data, args.out)
    figure_nonsense(data, args.out)
    figure_relevance(data, args.out)
    print_spearman(data, args.permutations, 20260816)
    if not args.skip_examples:
        print("examples:")
        write_examples(args, args.seed, args.examples_per_dataset)


if __name__ == "__main__":
    main()
