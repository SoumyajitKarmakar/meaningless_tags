#!/usr/bin/env python3
"""Statistical tables for the paper, built from the raw per-fact results. No GPU.

    python make_tables.py --results results --out results/stats

Every comparison is paired within fact (see paired_stats.py):

    rate     bootstrap 95% CI over facts, plus an exact Clopper-Pearson CI
             (the bootstrap collapses to a point at 0% and 100%)
    mean M   bootstrap 95% CI over facts
    Δrate    paired bootstrap CI; exact McNemar test on the discordant facts
    ΔM       paired bootstrap CI; Wilcoxon signed-rank test; per-fact sign
             counts (d>0) with an exact sign test
    ρ        cross-model Spearman over wrappers; permutation p-value
    strings  crossed bootstrap over strings x facts (E13)

p-values are also Holm-adjusted within each family: one section, one model,
one relation, one cell.

Sections, in paper order:

    claims     §3    E8   the claim sentence, unwrapped
    phrasing   §3    E7   source and hedge main effects (only where E7 ran)
    headline   §4.1  E12  wrappers against an explicit instruction (E8)
    ladder     §4.2  E12  every wrapper against no wrapper, per cell
    factorial  §4.2  E12  <name> against Name: for every name
    named      §4.2  E12  specific contrasts quoted in the text
    spearman   §4.2  E12  cross-model rank agreement over wrappers
    relevance  §4.3  E12  the same wrappers around a paragraph about another subject
    nonsense   §4.4  E13  thirty random names as tag and label (+ E12's names)
    guards     §5    E11  three guard wordings in three slots
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np

import paired_stats as ps
from common import json_safe, write_json_atomic
from E11_source_channel import CELLS as E11_CELLS, CHANNELS as E11_CHANNELS, GUARD_CHANNELS, GUARDS, SLOTS
from E12_delimiter import (
    FACTORIAL,
    IRRELEVANT_CELL,
    MEANINGLESS_NAMES,
    WRAPPER_ROLE,
    WRAPPERS,
)
import E13_nonsense_strings as e13


MODELS = (
    ("gemma", "Gemma 4 12B", "gemma4_12b_conflict"),
    ("qwen", "Qwen 3.6 27B", "qwen36_27b_conflict"),
)
RELATIONS = (("element_symbol", "elements"), ("country_capital", "capitals"))
SECTIONS = (
    "claims", "phrasing", "headline", "ladder", "factorial", "named",
    "spearman", "relevance", "nonsense", "guards",
)

# §3: E8 cell -> the name the write-up uses.
CLAIM_CELLS = (
    ("bare", "neutral"),
    ("stipulate_r1", "suggestion-type1"),
    ("stipulate_r2", "suggestion-type2"),
    ("assert_r1", "assertion-type1"),
    ("assert_r2", "assertion-type2"),
    ("explicit_stipulation", "instruction"),
)
CLAIM_NAME = dict(CLAIM_CELLS)
CLAIM_CONTRASTS = (
    ("bare", "assert_r1"),
    ("bare", "assert_r2"),
    ("bare", "stipulate_r1"),
    ("bare", "stipulate_r2"),
    ("explicit_stipulation", "assert_r1"),
    ("explicit_stipulation", "bare"),
)
# §3: E7's four factors, each averaged over the other three within fact.
PHRASING_FACTORS = {
    "act": ("stipulate", "assert"),
    "realization": ("r1", "r2"),
    "source": ("high", "low"),
    "persistence": ("present", "absent"),
}
# §4.2: contrasts the text quotes directly.
NAMED_CONTRASTS = (
    ("tag_trusted", "tag_untrusted", "valence, same syntax"),
    ("tag_document", "tag_nonsense", "a meaningful name against a meaningless one"),
    ("tag_nonsense", "tag_gibberish", "the two nonsense tags"),
    ("tag_unreliable", "tag_untrusted", "the two warning tags"),
    ("tag_empty", "dashes", "bare brackets against a punctuation fence"),
)
PRETTY = {
    "inline": "none", "blankline": "blank lines", "dashes": "--- fence",
    "quotes": '""" fence',
    **{w: WRAPPERS[w].split("\n", 1)[0] for w in WRAPPERS if w.startswith(("tag_", "label_"))},
}
CHANNEL_PRETTY = {
    "inline": "no wrapper", "delimited": "<document>, no warning",
    "retrieved_turn": "retrieved turn",
    **{c: f"{g} guard, {'system prompt' if s == 'system' else 'user turn ' + s}"
       for c, (g, s) in GUARD_CHANNELS.items()},
}
CHANNEL_OF = {spec: channel for channel, spec in GUARD_CHANNELS.items()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--out", type=Path, default=Path("results/stats"))
    parser.add_argument("--replicates", type=int, default=ps.DEFAULT_REPLICATES)
    parser.add_argument("--permutations", type=int, default=ps.DEFAULT_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=ps.DEFAULT_SEED)
    parser.add_argument("--conventionality-dir", default="conventionality_random")
    parser.add_argument("--phrasing-dir", default="phrasing_v2")
    parser.add_argument("--delimiter-dir", default="delimiter_v2")
    parser.add_argument("--channel-dir", default="channel_v2")
    parser.add_argument("--nonsense-dir", default="nonsense_strings")
    parser.add_argument("--sections", default=",".join(SECTIONS))
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


@dataclass
class Condition:
    """One condition's per-fact outcomes."""

    contextual: dict[str, bool] = field(default_factory=dict)
    margin: dict[str, float] = field(default_factory=dict)


def read_rows(path: Path, keep: Callable[[Mapping[str, Any]], bool]) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                if row.get("cell_id") != "screen" and keep(row):
                    rows.append(row)
    return rows


def conditions(rows: Iterable[Mapping[str, Any]], fields: Sequence[str]) -> dict[tuple, Condition]:
    """(relation, *fields) -> Condition. Two rows for one fact is an error."""
    table: dict[tuple, Condition] = collections.defaultdict(Condition)
    for row in rows:
        key = (str(row["relation_id"]), *(str(row[f]) for f in fields))
        fact = str(row["fact_id"])
        condition = table[key]
        if fact in condition.margin:
            raise ValueError(f"Two rows for {key} and fact {fact}")
        condition.contextual[fact] = row["observed_knowledge_source"] == "contextual"
        condition.margin[fact] = float(row["context_minus_parametric_logprob_margin"])
    return dict(table)


def neutral(row: Mapping[str, Any]) -> bool:
    # E8 also ran a `context` policy; E11's older files carry a `parametric`
    # one. The paper reports the neutral prompt only.
    return str(row.get("policy_id", "neutral")) == "neutral"


@dataclass
class Sources:
    """Every input this script reads, per model; None where a file is absent."""

    e7: dict[str, list[dict[str, Any]] | None] = field(default_factory=dict)
    e8: dict[str, dict[tuple, Condition] | None] = field(default_factory=dict)
    e11: dict[str, dict[tuple, Condition] | None] = field(default_factory=dict)
    e12: dict[str, dict[tuple, Condition] | None] = field(default_factory=dict)
    e13: dict[str, list[dict[str, Any]] | None] = field(default_factory=dict)
    paths: dict[str, str] = field(default_factory=dict)


def load_sources(args: argparse.Namespace) -> Sources:
    sources = Sources()
    files = {
        "e7": (args.phrasing_dir, "phrasing_results.jsonl"),
        "e8": (args.conventionality_dir, "conventionality_results.jsonl"),
        "e11": (args.channel_dir, "channel_results.jsonl"),
        "e12": (args.delimiter_dir, "delimiter_results.jsonl"),
        "e13": (args.nonsense_dir, "nonsense_results.jsonl"),
    }
    for model, _, folder in MODELS:
        for name, (subdir, filename) in files.items():
            path = args.results / folder / "analysis" / subdir / filename
            sources.paths[f"{model}/{name}"] = str(path)
            if not path.is_file():
                print(f"  NOTE: {model}: no {name.upper()} results at {path}")
                getattr(sources, name)[model] = None
                continue
            if name == "e7":
                rows = read_rows(path, lambda r: bool(r.get("claim_is_query_relevant", True)))
                getattr(sources, name)[model] = rows
            elif name == "e13":
                getattr(sources, name)[model] = read_rows(path, lambda r: True)
            elif name == "e12":
                getattr(sources, name)[model] = conditions(
                    read_rows(path, lambda r: True), ("cell_id", "wrapper")
                )
            elif name == "e11":
                getattr(sources, name)[model] = conditions(
                    read_rows(path, neutral), ("cell_id", "channel")
                )
            else:
                getattr(sources, name)[model] = conditions(read_rows(path, neutral), ("cell_id",))
            print(f"  read {path}")
    return sources


# ---------------------------------------------------------------------------
# Collecting
# ---------------------------------------------------------------------------


class Collector:
    def __init__(self, replicates: int, permutations: int, seed: int) -> None:
        self.replicates = replicates
        self.permutations = permutations
        self.seed = seed
        self.cells: list[dict[str, Any]] = []
        self.contrasts: list[dict[str, Any]] = []
        self.deltas: list[dict[str, Any]] = []
        self.spearman: list[dict[str, Any]] = []
        self.nonsense: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)

    def cell(self, section: str, model: str, relation: str, cell: str,
             condition: str, data: Condition, source: str) -> dict[str, Any]:
        facts = sorted(data.margin)
        entry = {
            "section": section, "model": model, "relation": relation, "cell": cell,
            "condition": condition, "source": source,
            **ps.describe_cell([data.contextual[f] for f in facts],
                               [data.margin[f] for f in facts],
                               self.replicates, self.seed),
        }
        self.cells.append(entry)
        return entry

    def contrast(self, section: str, model: str, relation: str, cell: str,
                 a: str, data_a: Condition, source_a: str,
                 b: str, data_b: Condition, source_b: str,
                 note: str = "") -> dict[str, Any] | None:
        facts = sorted(set(data_a.margin) & set(data_b.margin))
        if not facts:
            return None
        entry = {
            "section": section, "family": f"{section}/{model}/{relation}/{cell}",
            "model": model, "relation": relation, "cell": cell,
            "a": a, "b": b, "note": note,
            "source_a": source_a, "source_b": source_b,
            "cross_run": source_a != source_b,
            "n_a": len(data_a.margin), "n_b": len(data_b.margin),
            **ps.paired_contrast(
                [data_a.contextual[f] for f in facts], [data_a.margin[f] for f in facts],
                [data_b.contextual[f] for f in facts], [data_b.margin[f] for f in facts],
                self.replicates, self.seed,
            ),
        }
        self.contrasts.append(entry)
        return entry

    def delta(self, section: str, model: str, relation: str, cell: str,
              label: str, values: Sequence[float], **extra: Any) -> dict[str, Any] | None:
        if len(values) == 0:
            return None
        entry = {
            "section": section, "family": f"{section}/{model}/{relation}/{cell}",
            "model": model, "relation": relation, "cell": cell, "contrast": label,
            **extra,
            **ps.paired_delta_summary(values, self.replicates, self.seed),
        }
        self.deltas.append(entry)
        return entry

    def adjust(self) -> None:
        """Holm within each family, separately for each test."""
        for entries, columns in (
            (self.contrasts, ("wilcoxon_p", "mcnemar_p", "sign_test_p")),
            (self.deltas, ("wilcoxon_p", "sign_test_p")),
        ):
            families: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
            for entry in entries:
                families[entry["family"]].append(entry)
            for members in families.values():
                for column in columns:
                    for entry, value in zip(members, ps.holm([m[column] for m in members])):
                        entry[f"{column}_holm"] = value


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------


def section_claims(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    source = f"E8:{args.conventionality_dir}"
    for model, _, _ in MODELS:
        e8 = s.e8.get(model)
        if e8 is None:
            continue
        for relation, _ in RELATIONS:
            for cell, name in CLAIM_CELLS:
                if (relation, cell) in e8:
                    c.cell("claims", model, relation, "unwrapped", name, e8[(relation, cell)], source)
            for a, b in CLAIM_CONTRASTS:
                if (relation, a) in e8 and (relation, b) in e8:
                    c.contrast("claims", model, relation, "unwrapped",
                               CLAIM_NAME[a], e8[(relation, a)], source,
                               CLAIM_NAME[b], e8[(relation, b)], source)


def section_phrasing(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    for model, _, _ in MODELS:
        rows = s.e7.get(model)
        if not rows:
            continue
        # (relation, fact) -> list of (levels, margin) over the 16 factorial cells
        cells: dict[tuple[str, str], list[tuple[Mapping[str, str], float]]] = collections.defaultdict(list)
        for row in rows:
            levels = row.get("levels") or {}
            if len(levels) == len(PHRASING_FACTORS):
                cells[(str(row["relation_id"]), str(row["fact_id"]))].append(
                    (levels, float(row["context_minus_parametric_logprob_margin"]))
                )
        for relation, _ in RELATIONS:
            facts = sorted(f for (r, f) in cells if r == relation)
            for factor, (plus, minus) in PHRASING_FACTORS.items():
                values = []
                for fact in facts:
                    a = [m for lv, m in cells[(relation, fact)] if lv[factor] == plus]
                    b = [m for lv, m in cells[(relation, fact)] if lv[factor] == minus]
                    if a and b:
                        values.append(float(np.mean(a) - np.mean(b)))
                c.delta("phrasing", model, relation, "unwrapped", f"{factor}: {plus} − {minus}",
                        values, source=f"E7:{args.phrasing_dir}")


def section_headline(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    e12_source = f"E12:{args.delimiter_dir}"
    e8_source = f"E8:{args.conventionality_dir}"
    for model, _, _ in MODELS:
        e12, e8 = s.e12.get(model), s.e8.get(model)
        if e12 is None:
            continue
        for relation, _ in RELATIONS:
            wrapped = {w: e12.get((relation, "assert_r1", w))
                       for w in ("inline", "tag_nonsense", "tag_document")}
            if any(v is None for v in wrapped.values()):
                continue
            for wrapper, data in wrapped.items():
                c.cell("headline", model, relation, "assert_r1", PRETTY[wrapper], data, e12_source)
            instruction = e8.get((relation, "explicit_stipulation")) if e8 else None
            if instruction is not None:
                c.cell("headline", model, relation, "assert_r1",
                       "instruction, no wrapper", instruction, e8_source)
            for wrapper in ("tag_document", "tag_nonsense"):
                c.contrast("headline", model, relation, "assert_r1",
                           PRETTY[wrapper], wrapped[wrapper], e12_source,
                           "none", wrapped["inline"], e12_source)
            if instruction is not None:
                c.contrast("headline", model, relation, "assert_r1",
                           "instruction, no wrapper", instruction, e8_source,
                           "none", wrapped["inline"], e12_source,
                           note="different runs; paired on shared facts")
                c.contrast("headline", model, relation, "assert_r1",
                           PRETTY["tag_document"], wrapped["tag_document"], e12_source,
                           "instruction, no wrapper", instruction, e8_source,
                           note="different runs; paired on shared facts")


def e12_cells(e12: Mapping[tuple, Condition], relation: str) -> list[str]:
    seen = {k[1] for k in e12 if k[0] == relation}
    ordered = ["assert_r1", "bare", IRRELEVANT_CELL]
    return [cell for cell in ordered if cell in seen] + sorted(seen - set(ordered))


def section_ladder(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    source = f"E12:{args.delimiter_dir}"
    for model, _, _ in MODELS:
        e12 = s.e12.get(model)
        if e12 is None:
            continue
        for relation, _ in RELATIONS:
            for cell in e12_cells(e12, relation):
                baseline = e12.get((relation, cell, "inline"))
                for wrapper in WRAPPERS:
                    data = e12.get((relation, cell, wrapper))
                    if data is None:
                        continue
                    c.cell("ladder", model, relation, cell, wrapper, data, source)
                    if wrapper != "inline" and baseline is not None:
                        c.contrast("ladder", model, relation, cell,
                                   wrapper, data, source, "inline", baseline, source,
                                   note=WRAPPER_ROLE[wrapper])


def section_factorial(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    source = f"E12:{args.delimiter_dir}"
    for model, _, _ in MODELS:
        e12 = s.e12.get(model)
        if e12 is None:
            continue
        for relation, _ in RELATIONS:
            for cell in e12_cells(e12, relation):
                for name, (tag, label) in FACTORIAL.items():
                    a, b = e12.get((relation, cell, tag)), e12.get((relation, cell, label))
                    if a is not None and b is not None:
                        c.contrast("factorial", model, relation, cell,
                                   tag, a, source, label, b, source,
                                   note="meaningless" if name in MEANINGLESS_NAMES else name)


def section_named(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    source = f"E12:{args.delimiter_dir}"
    for model, _, _ in MODELS:
        e12 = s.e12.get(model)
        if e12 is None:
            continue
        for relation, _ in RELATIONS:
            for cell in ("assert_r1", "bare"):
                for a, b, note in NAMED_CONTRASTS:
                    data_a, data_b = e12.get((relation, cell, a)), e12.get((relation, cell, b))
                    if data_a is not None and data_b is not None:
                        c.contrast("named", model, relation, cell,
                                   a, data_a, source, b, data_b, source, note=note)


def section_spearman(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    (first, _, _), (second, _, _) = MODELS[0], MODELS[1]
    x_data, y_data = s.e12.get(first), s.e12.get(second)
    if x_data is None or y_data is None:
        return
    for relation, _ in RELATIONS:
        for cell in e12_cells(x_data, relation):
            shared = [w for w in WRAPPERS
                      if (relation, cell, w) in x_data and (relation, cell, w) in y_data]
            for include_baseline in (True, False):
                wrappers = shared if include_baseline else [w for w in shared if w != "inline"]
                if len(wrappers) < 3:
                    continue
                x = [float(np.mean(list(x_data[(relation, cell, w)].margin.values()))) for w in wrappers]
                y = [float(np.mean(list(y_data[(relation, cell, w)].margin.values()))) for w in wrappers]
                result = ps.spearman_permutation(x, y, c.permutations, c.seed)
                c.spearman.append({
                    "relation": relation, "cell": cell, "models": f"{first} vs {second}",
                    "includes_baseline": include_baseline, "n_wrappers": result["n"],
                    "rho": result["rho"], "permutation_p": result["p"],
                    "permutations": result["permutations"],
                })


def section_relevance(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    source = f"E12:{args.delimiter_dir}"
    for model, _, _ in MODELS:
        e12 = s.e12.get(model)
        if e12 is None:
            continue
        for relation, _ in RELATIONS:
            rel0 = e12.get((relation, "assert_r1", "inline"))
            irr0 = e12.get((relation, IRRELEVANT_CELL, "inline"))
            if rel0 is None or irr0 is None:
                continue
            c.contrast("relevance", model, relation, "inline",
                       "about the queried subject", rel0, source,
                       "about another subject", irr0, source,
                       note="no wrapper; same sentence and false answer")
            for wrapper in WRAPPERS:
                if wrapper == "inline":
                    continue
                rel = e12.get((relation, "assert_r1", wrapper))
                irr = e12.get((relation, IRRELEVANT_CELL, wrapper))
                if rel is None or irr is None:
                    continue
                facts = sorted(set(rel.margin) & set(irr.margin) & set(rel0.margin) & set(irr0.margin))
                if not facts:
                    continue
                relevant = np.asarray([rel.margin[f] - rel0.margin[f] for f in facts])
                irrelevant = np.asarray([irr.margin[f] - irr0.margin[f] for f in facts])
                irrelevant_ci = ps.bootstrap_mean_ci(irrelevant, c.replicates, c.seed)
                c.delta(
                    "relevance", model, relation, "interaction",
                    f"{wrapper}: (relevant − irrelevant) wrapper effect",
                    relevant - irrelevant,
                    wrapper=wrapper, source=source,
                    delta_relevant=float(relevant.mean()),
                    delta_irrelevant=float(irrelevant.mean()),
                    delta_irrelevant_ci_low=irrelevant_ci[0],
                    delta_irrelevant_ci_high=irrelevant_ci[1],
                    irrelevant_share=(float(irrelevant.mean() / relevant.mean())
                                      if relevant.mean() != 0 else float("nan")),
                    rate_relevant=float(np.mean([rel.contextual[f] for f in facts])),
                    rate_irrelevant=float(np.mean([irr.contextual[f] for f in facts])),
                )


def section_nonsense(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    relations = [r for r, _ in RELATIONS]
    for model, _, _ in MODELS:
        rows = s.e13.get(model)
        if not rows:
            continue
        cells = sorted({str(r["cell_id"]) for r in rows})
        result = e13.analyse(rows, relations, cells, c.replicates, c.permutations, c.seed)
        for key, entries in result.items():
            for entry in entries:
                c.nonsense[key].append({"model": model, **entry})
        # The bracket x meaning interaction: are tag-minus-label gaps larger for
        # random names (E13) than for E12's meaningful names?
        e12 = s.e12.get(model)
        if e12 is None:
            continue
        for relation in relations:
            for cell in cells:
                random_gaps = [e["gap"] for e in result["per_string"]
                               if e["relation"] == relation and e["cell"] == cell]
                meaningful, original = {}, {}
                for name, (tag, label) in FACTORIAL.items():
                    a, b = e12.get((relation, cell, tag)), e12.get((relation, cell, label))
                    if a is None or b is None:
                        continue
                    facts = sorted(set(a.margin) & set(b.margin))
                    gap = float(np.mean([a.margin[f] - b.margin[f] for f in facts]))
                    (original if name in MEANINGLESS_NAMES else meaningful)[name] = gap
                if not random_gaps or not meaningful:
                    continue
                test = ps.permutation_mean_difference(
                    random_gaps, list(meaningful.values()), c.permutations, c.seed
                )
                c.nonsense["interaction"].append({
                    "model": model, "relation": relation, "cell": cell,
                    "n_random": len(random_gaps),
                    "mean_gap_random": float(np.mean(random_gaps)),
                    "n_meaningful": len(meaningful),
                    "mean_gap_meaningful": float(np.mean(list(meaningful.values()))),
                    "difference": test["difference"], "permutation_p": test["p"],
                    "meaningful_gaps": json.dumps({k: round(v, 3) for k, v in meaningful.items()}),
                    "original_nonsense_gaps": json.dumps({k: round(v, 3) for k, v in original.items()}),
                })


def section_guards(c: Collector, s: Sources, args: argparse.Namespace) -> None:
    source = f"E11:{args.channel_dir}"
    for model, _, _ in MODELS:
        e11 = s.e11.get(model)
        if e11 is None:
            continue
        for relation, _ in RELATIONS:
            for cell in E11_CELLS:
                data = {ch: e11[(relation, cell, ch)] for ch in E11_CHANNELS
                        if (relation, cell, ch) in e11}
                for channel, condition in data.items():
                    c.cell("guards", model, relation, cell, channel, condition, source)

                def add(a: str, b: str, note: str) -> None:
                    if a in data and b in data:
                        c.contrast("guards", model, relation, cell,
                                   a, data[a], source, b, data[b], source, note=note)

                add("delimited", "inline", "the <document> wrapper, no warning")
                add("retrieved_turn", "delimited", "a simulated retrieval turn")
                for channel in GUARD_CHANNELS:
                    add(channel, "delimited", "the guard's effect")
                for guard in GUARDS:
                    add(CHANNEL_OF[(guard, "below")], CHANNEL_OF[(guard, "above")],
                        "position, same text")
                    add(CHANNEL_OF[(guard, "system")], CHANNEL_OF[(guard, "below")],
                        "system prompt against the best user slot")
                for slot in SLOTS:
                    add(CHANNEL_OF[("instruction", slot)], CHANNEL_OF[("falsehood", slot)],
                        "naming the right threat")
                    add(CHANNEL_OF[("combined", slot)], CHANNEL_OF[("falsehood", slot)],
                        "adding the instruction warning")
                    add(CHANNEL_OF[("combined", slot)], CHANNEL_OF[("instruction", slot)],
                        "adding the falsehood warning")


SECTION_FUNCTIONS = {
    "claims": section_claims,
    "phrasing": section_phrasing,
    "headline": section_headline,
    "ladder": section_ladder,
    "factorial": section_factorial,
    "named": section_named,
    "spearman": section_spearman,
    "relevance": section_relevance,
    "nonsense": section_nonsense,
    "guards": section_guards,
}


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def show(name: Any) -> str:
    """A wrapper or channel name, safe in a markdown table: `<document>` would
    otherwise be swallowed as an HTML tag."""
    text = str(name)
    return f"`{text}`" if any(mark in text for mark in ("<", ">", ":", '"', "---")) else text


def pretty(wrapper: str) -> str:
    return show(PRETTY.get(wrapper, wrapper))


def channel_pretty(channel: str) -> str:
    return show(CHANNEL_PRETTY.get(channel, channel))


def pct(value: Any, signed: bool = False) -> str:
    if not finite(value):
        return "–"
    return f"{100 * float(value):+.1f}" if signed else f"{100 * float(value):.1f}%"


def num(value: Any, digits: int = 1, signed: bool = False) -> str:
    if not finite(value):
        return "–"
    return f"{float(value):+.{digits}f}" if signed else f"{float(value):.{digits}f}"


def rate_text(e: Mapping[str, Any]) -> str:
    return (f"{pct(e['rate'])} "
            f"{ps.format_ci(e['rate_exact_low'], e['rate_exact_high'], 1, 100, False)}")


def margin_text(e: Mapping[str, Any]) -> str:
    return f"{num(e['mean_margin'])} {ps.format_ci(e['margin_ci_low'], e['margin_ci_high'])}"


def delta_margin_text(e: Mapping[str, Any]) -> str:
    return (f"{num(e['delta_margin'], signed=True)} "
            f"{ps.format_ci(e['delta_margin_ci_low'], e['delta_margin_ci_high'])}")


def mcnemar_text(e: Mapping[str, Any]) -> str:
    return (f"{e['mcnemar_only_a']}/{e['mcnemar_only_b']}, "
            f"p={ps.format_p(e['mcnemar_p_holm'])}")


def table(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return lines + [""]


def contrast_rows(entries: Iterable[Mapping[str, Any]], label: Callable[[Mapping[str, Any]], str]) -> list[list[str]]:
    return [
        [
            label(e), str(e["n"]),
            f"{pct(e['rate_a'])} vs {pct(e['rate_b'])}",
            f"{pct(e['delta_rate'], signed=True)} "
            f"{ps.format_ci(e['delta_rate_ci_low'], e['delta_rate_ci_high'], 1, 100)}",
            mcnemar_text(e),
            delta_margin_text(e),
            ps.format_p(e["wilcoxon_p_holm"]),
            f"{e['n_positive']}/{e['n']}",
        ]
        for e in entries
    ]


CONTRAST_HEADERS = ("Contrast (A − B)", "n", "Rate A vs B", "Δrate (pts)",
                    "McNemar A-only/B-only, p", "ΔM", "p (Wilcoxon)", "d>0")


def write_report(c: Collector, s: Sources, args: argparse.Namespace, path: Path) -> None:
    model_name = {m: label for m, label, _ in MODELS}
    relation_name = dict(RELATIONS)
    lines = [
        "# Statistics for the paper\n",
        "Generated by `make_tables.py` from the raw per-fact results. Every "
        "comparison is paired within fact. Rates show an exact Clopper–Pearson "
        "95% CI; margins and differences a bootstrap 95% CI over facts "
        f"({args.replicates} replicates). Δrate is tested with an exact McNemar "
        "test (A-only/B-only = discordant facts), ΔM with a Wilcoxon signed-rank "
        "test; `d>0` counts facts whose margin is higher under A. All p-values "
        "in the tables are Holm-adjusted within their family (section × model "
        "× relation × cell); unadjusted values are in `contrasts.csv`.\n",
    ]

    def cells_of(section: str, model: str, relation: str, cell: str | None = None):
        return [e for e in c.cells if e["section"] == section and e["model"] == model
                and e["relation"] == relation and (cell is None or e["cell"] == cell)]

    def contrasts_of(section: str, model: str, relation: str, cell: str | None = None):
        return [e for e in c.contrasts if e["section"] == section and e["model"] == model
                and e["relation"] == relation and (cell is None or e["cell"] == cell)]

    # §3 claims
    if any(e["section"] == "claims" for e in c.cells):
        lines.append("## §3 The claim sentence, unwrapped (E8)\n")
        for model, _, _ in MODELS:
            for relation, _ in RELATIONS:
                entries = cells_of("claims", model, relation)
                if not entries:
                    continue
                lines.append(f"**{model_name[model]} · {relation_name[relation]}**\n")
                lines.extend(table(("Claim", "n", "Rate [exact CI]", "M [CI]"),
                                   [[e["condition"], e["n"], rate_text(e), margin_text(e)]
                                    for e in entries]))
                lines.extend(table(CONTRAST_HEADERS, contrast_rows(
                    contrasts_of("claims", model, relation), lambda e: f"{e['a']} − {e['b']}")))
    phrasing = [e for e in c.deltas if e["section"] == "phrasing"]
    if phrasing:
        lines.append("## §3 Claim properties (E7 main effects, margin)\n")
        lines.extend(table(
            ("Model", "Relation", "Factor", "n", "ΔM [CI]", "p (Wilcoxon)", "d>0"),
            [[model_name[e["model"]], relation_name[e["relation"]], e["contrast"], e["n"],
              f"{num(e['delta'], signed=True)} {ps.format_ci(e['ci_low'], e['ci_high'])}",
              ps.format_p(e["wilcoxon_p_holm"]), f"{e['n_positive']}/{e['n']}"]
             for e in phrasing]))

    # §4.1 headline
    if any(e["section"] == "headline" for e in c.cells):
        lines.append("## §4.1 A wrapper against an explicit instruction\n")
        for model, _, _ in MODELS:
            for relation, _ in RELATIONS:
                entries = cells_of("headline", model, relation)
                if not entries:
                    continue
                lines.append(f"**{model_name[model]} · {relation_name[relation]}** "
                             "(assertion-type1 sentence)\n")
                lines.extend(table(("Prompt", "n", "Rate [exact CI]", "M [CI]"),
                                   [[show(e["condition"]), e["n"], rate_text(e), margin_text(e)]
                                    for e in entries]))
                lines.extend(table(CONTRAST_HEADERS, contrast_rows(
                    contrasts_of("headline", model, relation),
                    lambda e: f"{show(e['a'])} − {show(e['b'])}"
                    + (" †" if e["cross_run"] else ""))))
        lines.append("† A and B come from different runs (E12 and E8) and are paired "
                     "on the facts both kept after screening.\n")

    # §4.2 ladder
    if any(e["section"] == "ladder" for e in c.cells):
        lines.append("## §4.2 The wrapper ladder (E12, every wrapper − no wrapper)\n")
        for model, _, _ in MODELS:
            for relation, _ in RELATIONS:
                for cell in sorted({e["cell"] for e in cells_of("ladder", model, relation)},
                                   key=lambda x: ("assert_r1", "bare", IRRELEVANT_CELL).index(x)
                                   if x in ("assert_r1", "bare", IRRELEVANT_CELL) else 9):
                    entries = cells_of("ladder", model, relation, cell)
                    against = {e["a"]: e for e in contrasts_of("ladder", model, relation, cell)}
                    lines.append(f"**{model_name[model]} · {relation_name[relation]} · `{cell}`**\n")
                    rows = []
                    for e in entries:
                        k = against.get(e["condition"])
                        rows.append([
                            pretty(e["condition"]), e["n"],
                            rate_text(e), margin_text(e),
                            delta_margin_text(k) if k else "–",
                            ps.format_p(k["wilcoxon_p_holm"]) if k else "–",
                            f"{k['n_positive']}/{k['n']}" if k else "–",
                            mcnemar_text(k) if k else "–",
                        ])
                    lines.extend(table(("Wrapper", "n", "Rate [exact CI]", "M [CI]",
                                        "ΔM vs none [CI]", "p (Wilcoxon)", "d>0",
                                        "McNemar wrapper-only/none-only, p"), rows))

    # §4.2 factorial and named contrasts
    for section, title in (("factorial", "## §4.2 Tag against label, name held fixed (E12)\n"),
                           ("named", "## §4.2 Contrasts quoted in the text (E12)\n")):
        if not any(e["section"] == section for e in c.contrasts):
            continue
        lines.append(title)
        for model, _, _ in MODELS:
            for relation, _ in RELATIONS:
                entries = contrasts_of(section, model, relation)
                for cell in sorted({e["cell"] for e in entries}):
                    lines.append(f"**{model_name[model]} · {relation_name[relation]} · `{cell}`**\n")
                    lines.extend(table(CONTRAST_HEADERS, contrast_rows(
                        [e for e in entries if e["cell"] == cell],
                        lambda e: f"{pretty(e['a'])} − {pretty(e['b'])}")))

    if c.spearman:
        lines.append("## §4.2 Cross-model rank agreement over wrappers (E12)\n")
        lines.extend(table(
            ("Relation", "Cell", "Baseline included", "Wrappers", "Spearman ρ", "Permutation p"),
            [[relation_name.get(e["relation"], e["relation"]), f"`{e['cell']}`",
              "yes" if e["includes_baseline"] else "no", e["n_wrappers"],
              num(e["rho"], 2), ps.format_p(e["permutation_p"])] for e in c.spearman]))

    # §4.3 relevance
    relevance = [e for e in c.deltas if e["section"] == "relevance"]
    if relevance or any(e["section"] == "relevance" for e in c.contrasts):
        lines.append("## §4.3 The same wrapper, around a paragraph about another subject (E12)\n")
        lines.append(
            "`irrelevant_assert_r1` keeps the sentence and the false answer but names "
            "a different subject of the same relation. Interaction = wrapper effect "
            "on the relevant paragraph minus wrapper effect on the irrelevant one, per "
            "fact. Share = irrelevant / relevant wrapper effect; it is only "
            "interpretable where the relevant effect is clearly non-zero.\n")
        base = [e for e in c.contrasts if e["section"] == "relevance"]
        if base:
            lines.extend(table(("Model", "Relation") + CONTRAST_HEADERS, [
                [model_name[e["model"]], relation_name[e["relation"]], *row]
                for e, row in zip(base, contrast_rows(base, lambda e: f"{e['a']} − {e['b']}"))]))
        for model, _, _ in MODELS:
            for relation, _ in RELATIONS:
                entries = [e for e in relevance if e["model"] == model and e["relation"] == relation]
                if not entries:
                    continue
                lines.append(f"**{model_name[model]} · {relation_name[relation]}**\n")
                lines.extend(table(
                    ("Wrapper", "n", "ΔM relevant", "ΔM irrelevant [CI]", "Interaction [CI]",
                     "p (Wilcoxon)", "d>0", "Share", "Rate rel / irr"),
                    [[pretty(e["wrapper"]), e["n"],
                      num(e["delta_relevant"], signed=True),
                      f"{num(e['delta_irrelevant'], signed=True)} "
                      f"{ps.format_ci(e['delta_irrelevant_ci_low'], e['delta_irrelevant_ci_high'])}",
                      f"{num(e['delta'], signed=True)} {ps.format_ci(e['ci_low'], e['ci_high'])}",
                      ps.format_p(e["wilcoxon_p_holm"]), f"{e['n_positive']}/{e['n']}",
                      num(e["irrelevant_share"], 2),
                      f"{pct(e['rate_relevant'])} / {pct(e['rate_irrelevant'])}"]
                     for e in entries]))

    # §4.4 nonsense
    if c.nonsense.get("distribution"):
        lines.append("## §4.4 Thirty random names (E13)\n")
        lines.append(
            "ΔM against no wrapper, paired within fact. CIs over strings are a "
            "crossed bootstrap (strings × facts). The tag − label row is also "
            "tested across strings (Wilcoxon, one pair per string).\n")
        lines.extend(table(
            ("Model", "Relation", "Cell", "Form", "Strings", "Mean ΔM [crossed CI]", "Median",
             "Range", "Strings > 0", "Median rate", "p across strings"),
            [[model_name[e["model"]], relation_name.get(e["relation"], e["relation"]),
              f"`{e['cell']}`", e["form"], e["n_strings"],
              f"{num(e['mean_delta'], signed=True)} "
              f"{ps.format_ci(e['crossed_ci_low'], e['crossed_ci_high'])}",
              num(e["median_delta"], signed=True),
              f"[{num(e['min_delta'], signed=True)}, {num(e['max_delta'], signed=True)}]",
              f"{e['n_strings_delta_positive']}/{e['n_strings']}",
              pct(e.get("median_rate")),
              ps.format_p(e.get("wilcoxon_p_across_strings"))]
             for e in c.nonsense["distribution"]]))
        if c.nonsense.get("references"):
            lines.extend(table(
                ("Model", "Relation", "Cell", "Original string", "ΔM", "Rate",
                 "Percentile among random"),
                [[model_name[e["model"]], relation_name.get(e["relation"], e["relation"]),
                  f"`{e['cell']}`", pretty(e["wrapper"]),
                  num(e["delta_vs_inline"], signed=True), pct(e["context_rate"]),
                  f"{100 * e['percentile_among_random']:.0f}"]
                 for e in c.nonsense["references"]]))
        if c.nonsense.get("interaction"):
            lines.append("**Bracket × meaning.** Mean tag − label gap for the random names "
                         "(E13) against E12's six meaningful names; permutation test over "
                         "names.\n")
            lines.extend(table(
                ("Model", "Relation", "Cell", "Random names", "Mean gap", "Meaningful names",
                 "Mean gap", "Difference", "Permutation p"),
                [[model_name[e["model"]], relation_name.get(e["relation"], e["relation"]),
                  f"`{e['cell']}`", e["n_random"], num(e["mean_gap_random"], signed=True),
                  e["n_meaningful"], num(e["mean_gap_meaningful"], signed=True),
                  num(e["difference"], signed=True), ps.format_p(e["permutation_p"])]
                 for e in c.nonsense["interaction"]]))

    # §5 guards
    if any(e["section"] == "guards" for e in c.cells):
        lines.append("## §5 Guards: three wordings in three slots (E11)\n")
        for model, _, _ in MODELS:
            for relation, _ in RELATIONS:
                for cell in E11_CELLS:
                    entries = {e["condition"]: e for e in cells_of("guards", model, relation, cell)}
                    if not entries:
                        continue
                    lines.append(f"**{model_name[model]} · {relation_name[relation]} · `{cell}`** "
                                 "— rate (M)\n")
                    grid = []
                    for guard in ("none", *GUARDS):
                        row = [guard]
                        for slot in SLOTS:
                            channel = "delimited" if guard == "none" else CHANNEL_OF[(guard, slot)]
                            e = entries.get(channel)
                            row.append(f"{pct(e['rate'])} ({num(e['mean_margin'])})" if e else "–")
                        grid.append(row)
                    lines.extend(table(("Wording", "system prompt", "user, above", "user, below"),
                                       grid))
                    lines.extend(table(CONTRAST_HEADERS, contrast_rows(
                        contrasts_of("guards", model, relation, cell),
                        lambda e: f"{channel_pretty(e['a'])} − {channel_pretty(e['b'])}")))

    lines.append("## Inputs\n")
    lines.extend(f"- `{key}`: `{value}`" for key, value in sorted(s.paths.items()))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, entries: Sequence[Mapping[str, Any]]) -> None:
    if not entries:
        return
    fields: list[str] = []
    for entry in entries:
        for key in entry:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(entries)


def main() -> None:
    args = parse_args()
    sections = [x.strip() for x in args.sections.split(",") if x.strip()]
    unknown = sorted(set(sections) - set(SECTIONS))
    if unknown:
        raise ValueError(f"Unknown sections {unknown}; expected {SECTIONS}")
    args.out.mkdir(parents=True, exist_ok=True)
    print("inputs:")
    sources = load_sources(args)
    collector = Collector(args.replicates, args.permutations, args.seed)
    for name in sections:
        print(f"section {name}")
        SECTION_FUNCTIONS[name](collector, sources, args)
    collector.adjust()

    write_csv(args.out / "cells.csv", collector.cells)
    write_csv(args.out / "contrasts.csv", collector.contrasts)
    write_csv(args.out / "deltas.csv", collector.deltas)
    write_csv(args.out / "spearman.csv", collector.spearman)
    for key, entries in collector.nonsense.items():
        write_csv(args.out / f"nonsense_{key}.csv", entries)
    write_json_atomic(
        args.out / "stats_summary.json",
        json_safe({
            "settings": {"replicates": args.replicates, "permutations": args.permutations,
                         "seed": args.seed, "sections": sections},
            "inputs": sources.paths,
            "cells": collector.cells,
            "contrasts": collector.contrasts,
            "deltas": collector.deltas,
            "spearman": collector.spearman,
            "nonsense": dict(collector.nonsense),
        }),
    )
    write_report(collector, sources, args, args.out / "stats_report.md")
    print(f"\n{len(collector.cells)} cells, {len(collector.contrasts)} contrasts, "
          f"{len(collector.deltas)} difference summaries, "
          f"{len(collector.spearman)} rank correlations")
    for entry in collector.spearman:
        print(f"  Spearman {entry['relation']:16s} {entry['cell']:22s} "
              f"baseline={'in ' if entry['includes_baseline'] else 'out'} "
              f"n={entry['n_wrappers']:2d}  rho={entry['rho']:+.2f}  "
              f"p={ps.format_p(entry['permutation_p'])}")
    print(f"wrote {args.out / 'stats_report.md'}")


if __name__ == "__main__":
    main()
