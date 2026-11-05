#!/usr/bin/env python3
"""E7: which PROPERTY of the claim sentence drives deference?

Four properties of the claim sentence are crossed (2^4 = 16 cells per fact):

    act          stipulate ("uses B as the symbol for X") vs assert ("states that ... is B")
    realization  two verbs for the same act (r1 / r2)
    source       a high-authority source (textbook) vs a low one (poster / brochure)
    persistence  without vs with the hedge "consistently"

plus the unattributed `bare` claim, the dataset's two original claim sentences
(`orig_high`, `orig_low`, the claim templates of the high- and low-deference
bundles in Gemma's E6 run; descriptive only), and a specificity control: the
stipulate and assert sentences about a DIFFERENT subject of the same relation.

Facts, false answers, screening and distractors are the E8 / E12 pipeline's, so
E7 shares one fact set and one false-answer assignment with E8, E11, E12 and
E13 for each model. The frame (filler, question, constraint) is E8's, so:

    assert_r1_high_absent, assert_r2_high_absent,
    stipulate_r1_high_absent, stipulate_r2_high_absent, bare
        rebuild E8's cells of the same name byte for byte, and
    irrelevant_assert
        rebuilds E12's irrelevant_assert_r1 cell with no wrapper.

Pass --e8-results / --e12-results to check those prompts before scoring and the
margins after.
"""

from __future__ import annotations

import argparse
import collections
import csv
import itertools
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from build_conflict_awareness_dataset import relation_specs, stable_digest
from common import (
    finalize_jsonl,
    json_safe,
    load_config,
    load_model_bundle,
    read_jsonl,
    runtime_fingerprint,
    seed_everything,
    write_json_atomic,
)
from E8_conventionality import BARE, assemble, build_facts
from E12_delimiter import (
    IRRELEVANT_CELL,
    assign_distractors,
    evaluate,
    first_per_relation,
    mentions,
    screened_facts,
    screening_records,
)


ANALYSIS_VERSION = "2.0.0"
PREFIX = "e7"

FACTORS = ("act", "realization", "source", "persistence")

# Claim sentences. Written here rather than in the generator because they are a
# new manipulation, not a new dataset. `{s}` = subject, `{a}` = claim answer.
# The high sources and the predicates are E8's SOURCE and PREDICATES.
SOURCES = {
    "element_symbol": {"high": "A university chemistry textbook", "low": "A classroom wall poster"},
    "country_capital": {"high": "A national geography textbook", "low": "A tourist brochure"},
}
PREDICATES = {
    # act -> realization -> verb phrase completing "{source} {adverb}<phrase>."
    "element_symbol": {
        "stipulate": {
            "r1": "uses {a} as the chemical symbol for {s}",
            "r2": "treats {a} as the chemical symbol for {s}",
        },
        "assert": {
            "r1": "states that the chemical symbol for {s} is {a}",
            "r2": "reports the chemical symbol for {s} to be {a}",
        },
    },
    "country_capital": {
        "stipulate": {
            "r1": "refers to {a} as the capital of {s}",
            "r2": "treats {a} as the capital of {s}",
        },
        "assert": {
            "r1": "states that the capital of {s} is {a}",
            "r2": "reports the capital of {s} to be {a}",
        },
    },
}
ADVERB = {"absent": "", "present": "consistently "}
# The dataset's original claim sentences: the claim templates of the high- and
# low-deference bundles in Gemma's E6 run. Kept as descriptive anchors.
ORIGINAL_CLAIM_INDEX = {
    "element_symbol": {"orig_high": 1, "orig_low": 2},
    "country_capital": {"orig_high": 2, "orig_low": 1},
}
# E7 cells that rebuild another experiment's prompt exactly.
E8_ANCHORS = {
    "bare": "bare",
    **{f"{act}_{real}_high_absent": f"{act}_{real}"
       for act in ("stipulate", "assert") for real in ("r1", "r2")},
}
E12_ANCHORS = {
    "assert_r1_high_absent": ("assert_r1", "inline"),
    "bare": ("bare", "inline"),
    "irrelevant_assert": (IRRELEVANT_CELL, "inline"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--relations", default="element_symbol,country_capital")
    parser.add_argument(
        "--false-answer-mode", choices=("reuse", "rotation", "random"), default="random"
    )
    parser.add_argument("--false-answer-seed", type=int, default=20260816)
    parser.add_argument("--distractor-seed", type=int, default=20260816)
    parser.add_argument(
        "--e8-results",
        type=Path,
        default=None,
        help="conventionality_results.jsonl from E8 (same model, --false-answer-mode "
        "random). Enables the anchor checks against E8.",
    )
    parser.add_argument(
        "--e12-results",
        type=Path,
        default=None,
        help="delimiter_results.jsonl from E12 (same model). Enables the anchor "
        "checks against E12.",
    )
    parser.add_argument("--max-facts", type=int, default=None)
    parser.add_argument("--generation-batch-size", type=int, default=None)
    parser.add_argument("--scoring-batch-size", type=int, default=None)
    parser.add_argument("--bootstrap-replicates", type=int, default=2000)
    parser.add_argument("--skip-screening", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--analyze-only", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Cells and records
# ---------------------------------------------------------------------------


def claim_cells(relation: str) -> list[tuple[str, dict[str, str], str]]:
    """(cell_id, factor levels, claim template) for every relevant cell."""
    spec = relation_specs()[relation]
    cells: list[tuple[str, dict[str, str], str]] = []
    for act, realization, source, persistence in itertools.product(
        ("stipulate", "assert"), ("r1", "r2"), ("high", "low"), ("absent", "present")
    ):
        phrase = PREDICATES[relation][act][realization]
        template = f"{SOURCES[relation][source]} {ADVERB[persistence]}{phrase}."
        cells.append(
            (
                f"{act}_{realization}_{source}_{persistence}",
                {"act": act, "realization": realization,
                 "source": source, "persistence": persistence},
                template,
            )
        )
    for name, index in ORIGINAL_CLAIM_INDEX[relation].items():
        cells.append(
            (name, {}, spec.claim_templates[index].replace(
                "{claim_answer}", "{a}").replace("{claim_subject}", "{s}"))
        )
    cells.append(("bare", {}, BARE[relation]))
    return cells


def _record(
    fact: Mapping[str, Any],
    cell_id: str,
    levels: Mapping[str, str],
    claim: str,
    claim_subject: str,
    relevant: bool,
) -> dict[str, Any]:
    relation, subject = str(fact["relation_id"]), str(fact["query_subject"])
    prompt = assemble(relation, claim, subject)
    return {
        "sample_id": "phr-" + stable_digest(fact["fact_id"], cell_id, prompt),
        "raw_prompt": prompt,
        "messages": [{"role": "user", "content": prompt}],
        "fact_id": fact["fact_id"],
        "relation_id": relation,
        "cell_id": cell_id,
        "wrapper": "inline",
        "levels": dict(levels),
        "claim_sentence": claim,
        "claim_subject": claim_subject,
        "claim_is_query_relevant": relevant,
        # The paragraph's false answer is scored in every cell, the irrelevant
        # ones included, so their margins are directly comparable.
        "context_candidate_answer": fact["claim_answer"],
        "acceptable_world_true_answers": list(fact["acceptable_world_true_answers"]),
        "parametric_candidate_answer": fact["world_true_answer"],
    }


def build_records(facts: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for fact in facts:
        relation = str(fact["relation_id"])
        subject, answer = str(fact["query_subject"]), str(fact["claim_answer"])
        for cell_id, levels, template in claim_cells(relation):
            records.append(_record(
                fact, cell_id, levels, template.format(s=subject, a=answer), subject, True,
            ))
        # Specificity control: the same sentences and the same false answer,
        # about E12's distractor subject. A lift here is priming of the token,
        # not conflict resolution.
        distractor = str(fact["distractor_subject"])
        for act in ("stipulate", "assert"):
            template = f"{SOURCES[relation]['high']} {PREDICATES[relation][act]['r1']}."
            claim = template.format(s=distractor, a=answer)
            if any(mentions(claim, str(t)) for t in fact["acceptable_world_true_answers"]):
                raise ValueError(f"{fact['fact_id']}: {claim!r} names the true answer")
            records.append(_record(
                fact, f"irrelevant_{act}", {"act": act}, claim, distractor, False,
            ))
    return records


# ---------------------------------------------------------------------------
# Anchors
# ---------------------------------------------------------------------------


def load_anchors(e8_path: Path | None, e12_path: Path | None) -> dict[str, dict[tuple[str, str], Mapping[str, Any]]]:
    """source -> (fact_id, E7 cell) -> the other experiment's scored row."""
    anchors: dict[str, dict[tuple[str, str], Mapping[str, Any]]] = {}
    if e8_path is not None:
        inverse = {v: k for k, v in E8_ANCHORS.items()}
        anchors["E8"] = {
            (str(r["fact_id"]), inverse[str(r["cell_id"])]): r
            for r in read_jsonl(e8_path)
            if str(r["cell_id"]) in inverse and str(r.get("policy_id", "neutral")) == "neutral"
        }
    if e12_path is not None:
        inverse = {v: k for k, v in E12_ANCHORS.items()}
        anchors["E12"] = {
            (str(r["fact_id"]), inverse[(str(r["cell_id"]), str(r["wrapper"]))]): r
            for r in read_jsonl(e12_path)
            if (str(r["cell_id"]), str(r["wrapper"])) in inverse
        }
    return anchors


def check_anchor_prompts(
    records: Sequence[Mapping[str, Any]],
    anchors: Mapping[str, Mapping[tuple[str, str], Mapping[str, Any]]],
) -> None:
    """Every anchored prompt must be byte-identical to the other experiment's."""
    for name, table in anchors.items():
        checked = mismatched = 0
        for record in records:
            other = table.get((str(record["fact_id"]), str(record["cell_id"])))
            if other is None:
                continue
            checked += 1
            if other["raw_prompt"] != record["raw_prompt"]:
                mismatched += 1
                if mismatched <= 2:
                    print(f"\nANCHOR MISMATCH ({record['cell_id']} vs {name})")
                    print(f"  {name}: {other['raw_prompt']!r}")
                    print(f"  E7 : {record['raw_prompt']!r}")
        print(f"anchor prompts vs {name}: {checked - mismatched}/{checked} identical")
        if checked == 0:
            raise RuntimeError(
                f"No anchored prompts shared with {name}: is it the same model, "
                "--false-answer-mode random, and the same seeds?"
            )
        if mismatched:
            raise RuntimeError(
                f"Anchor prompts differ from {name}. The facts, false answers or "
                "frame have drifted; the experiments would no longer be comparable."
            )


def paired_mean_delta(
    values: Mapping[tuple[str, str], float],
    facts: Sequence[str],
    cells_a: Sequence[str],
    cells_b: Sequence[str],
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    """mean(values over cells_a) - mean(over cells_b), paired within fact.

    Averaging over the other factors' levels before differencing is what makes
    this a main effect rather than one arbitrary slice.
    """
    import numpy as np

    from paired_stats import bootstrap_mean_ci

    usable, deltas = [], []
    for fact in facts:
        a = [values[(fact, c)] for c in cells_a if (fact, c) in values]
        b = [values[(fact, c)] for c in cells_b if (fact, c) in values]
        if not a or not b:
            continue
        usable.append(fact)
        deltas.append(float(np.mean(a) - np.mean(b)))
    if not usable:
        return {"delta": float("nan"), "ci95": [float("nan"), float("nan")], "n": 0}
    array = np.asarray(deltas)
    low, high = bootstrap_mean_ci(array, replicates, seed)
    return {"delta": float(array.mean()), "ci95": [low, high], "n": len(usable)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    import numpy as np

    started = time.time()
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results_path = args.out / "phrasing_results.jsonl"
    partial_path = args.out / "phrasing_results.jsonl.partial"
    report_path = args.out / "phrasing_report.md"
    if args.analyze_only and args.validate_only:
        raise ValueError("--analyze-only and --validate-only are mutually exclusive")
    if (
        results_path.exists()
        and not args.overwrite
        and not args.validate_only
        and not args.analyze_only
    ):
        raise FileExistsError(f"Refusing to overwrite {results_path}; pass --overwrite")

    config = load_config(args.config)
    relations = [r.strip() for r in args.relations.split(",") if r.strip()]
    for relation in relations:
        if relation not in SOURCES:
            raise ValueError(f"Unknown relation {relation!r}; expected {sorted(SOURCES)}")

    # The same facts, false answers and distractors as E12: assigned over the
    # full relation, then truncated, then screened.
    facts = assign_distractors(
        build_facts(relations, None, None,
                    mode=args.false_answer_mode, seed=args.false_answer_seed),
        args.distractor_seed,
    )
    facts = first_per_relation(facts, args.max_facts)
    print(f"model: {config['model']['id']}")
    print(f"facts before screening: {dict(collections.Counter(f['relation_id'] for f in facts))}"
          f"   mode {args.false_answer_mode}")

    anchors = load_anchors(args.e8_results, args.e12_results)
    records = build_records(facts)
    print(f"cells/fact: {len(records) / len(facts):.1f}   prompts: {len(records)}")
    if anchors:
        check_anchor_prompts(records, anchors)
    else:
        print("anchor prompts: SKIPPED (pass --e8-results / --e12-results to enable)")

    if args.validate_only:
        for relation in relations:
            example = next(f for f in facts if f["relation_id"] == relation)
            print(f"\n{'=' * 78}\n{relation}: all claim sentences for "
                  f"{example['query_subject']}\n{'=' * 78}")
            for record in records:
                if record["fact_id"] == example["fact_id"]:
                    print(f"  [{record['cell_id']:34s}] {record['claim_sentence']}")
            print("\n  full prompt for one cell:\n")
            print(next(r["raw_prompt"] for r in records if r["fact_id"] == example["fact_id"]))
        print(f"\nvalidate-only: {len(facts)} screening + {len(records)} experimental prompts")
        return

    # ---- run ---------------------------------------------------------------
    if args.analyze_only:
        if not results_path.is_file():
            raise FileNotFoundError(f"--analyze-only needs an existing {results_path}")
        rows = read_jsonl(results_path)
        fingerprint: Any = {"note": "analyze-only; the model was not loaded"}
        print(f"analyze-only: reusing {len(rows)} scored prompts")
    else:
        seed_everything(int(config["project"]["seed"]))
        done: set[str] = set()
        if partial_path.exists() and not args.overwrite:
            done = {str(r["sample_id"]) for r in read_jsonl(partial_path)}
            print(f"resuming: {len(done)} prompts already scored")
        elif partial_path.exists():
            partial_path.unlink()

        bundle = load_model_bundle(config)
        dataset_files: dict[str, Any] = {}
        if args.e8_results:
            dataset_files["e8_results"] = args.e8_results
        if args.e12_results:
            dataset_files["e12_results"] = args.e12_results
        fingerprint = runtime_fingerprint(config, bundle, dataset_files)
        generation_batch = args.generation_batch_size or int(
            config["collection"]["generation_batch_size"]
        )
        scoring_batch = args.scoring_batch_size or int(
            config["collection"]["scoring_batch_size"]
        )

        if not args.skip_screening:
            print("\nscreening (context-free)")
            screen = [r for r in screening_records(facts, prefix=PREFIX)
                      if r["sample_id"] not in done]
            evaluate(screen, bundle, config, partial_path, generation_batch,
                     scoring_batch, started, analysis_version=ANALYSIS_VERSION)
            kept = screened_facts(facts, read_jsonl(partial_path), prefix=PREFIX)
            print(f"  kept {len(kept)}/{len(facts)} facts")
            facts = list(kept)
            if not facts:
                raise RuntimeError("No facts survived screening")

        pending = [r for r in build_records(facts) if r["sample_id"] not in done]
        print(f"\nscoring {len(pending)} experimental prompts")
        evaluate(pending, bundle, config, partial_path, generation_batch,
                 scoring_batch, started, carry=("levels",),
                 analysis_version=ANALYSIS_VERSION)
        rows = read_jsonl(partial_path)
        finalize_jsonl(partial_path, results_path)
        print(f"\nscored {len(rows)} prompts")

    # ---- analysis ----------------------------------------------------------
    rows = [r for r in rows if r["cell_id"] != "screen"]
    n_facts = len({str(r["fact_id"]) for r in rows})
    report: dict[str, Any] = {
        "analysis_version": ANALYSIS_VERSION,
        "runtime": fingerprint,
        "false_answer_mode": args.false_answer_mode,
        "false_answer_seed": args.false_answer_seed,
        "distractor_seed": args.distractor_seed,
        "factors": list(FACTORS),
    }
    relevant = [r for r in rows if r.get("claim_is_query_relevant", True)]
    margins = {
        (str(r["fact_id"]), str(r["cell_id"])): float(
            r["context_minus_parametric_logprob_margin"]
        )
        for r in relevant
    }
    seed = int(config["project"]["seed"])

    print("\n" + "=" * 78)
    print("A0  anchor reproduction against E8 / E12 (byte-identical prompts)")
    print("=" * 78)
    anchor_report: list[dict[str, Any]] = []
    all_margins = {
        (str(r["fact_id"]), str(r["cell_id"])): float(r["context_minus_parametric_logprob_margin"])
        for r in rows
    }
    for name, table in anchors.items():
        for relation in relations:
            for e7_cell in (E8_ANCHORS if name == "E8" else E12_ANCHORS):
                deltas = [
                    all_margins[(fact, cell)] - float(other["context_minus_parametric_logprob_margin"])
                    for (fact, cell), other in table.items()
                    if cell == e7_cell and (fact, cell) in all_margins
                    and fact.split(":", 1)[0] == relation
                ]
                if not deltas:
                    continue
                entry = {
                    "source": name, "relation": relation, "cell": e7_cell, "n": len(deltas),
                    "mean_delta": float(np.mean(deltas)),
                    "mean_abs_delta": float(np.mean(np.abs(deltas))),
                    "max_abs_delta": float(np.max(np.abs(deltas))),
                }
                anchor_report.append(entry)
                print(f"  {name:4s} {relation:17s} {e7_cell:26s} n={entry['n']:3d} "
                      f"mean d={entry['mean_delta']:+6.3f}  mean|d|={entry['mean_abs_delta']:6.3f}  "
                      f"max|d|={entry['max_abs_delta']:6.3f}")
    if not anchors:
        print("  skipped (no --e8-results / --e12-results)")
    report["anchor_reproduction"] = anchor_report
    print("  (BF16 batch composition alone moves single rows by up to a few logits)")

    print("\n" + "=" * 78)
    print("A1  main effect of each claim property (margin, logits)")
    print("    Each is averaged over all levels of the other three factors.")
    print("=" * 78)
    effects: list[dict[str, Any]] = []
    contrasts = {
        "act": ("stipulate", "assert"),
        "realization": ("r1", "r2"),
        "source": ("high", "low"),
        "persistence": ("present", "absent"),
    }
    for relation in relations:
        relation_facts = sorted({str(r["fact_id"]) for r in relevant if r["relation_id"] == relation})
        cells = [(c, lv) for c, lv, _ in claim_cells(relation) if lv]
        print(f"\n--- {relation} ---")
        print(f"  {'factor':14s}{'contrast':26s}{'delta':>9s}{'95% CI':>22s}")
        for factor, (plus, minus) in contrasts.items():
            a = [c for c, lv in cells if lv[factor] == plus]
            b = [c for c, lv in cells if lv[factor] == minus]
            result = paired_mean_delta(
                margins, relation_facts, a, b, args.bootstrap_replicates, seed
            )
            low, high = result["ci95"]
            star = "***" if (low > 0 or high < 0) else "   "
            effects.append({"relation": relation, "factor": factor,
                            "contrast": f"{plus} - {minus}", **result})
            print(
                f"  {factor:14s}{plus + ' - ' + minus:26s}{result['delta']:>9.2f}"
                f"{f'[{low:+.2f}, {high:+.2f}]':>22} {star}"
            )
        for anchor in ("orig_high", "orig_low", "bare"):
            values = [margins[(f, anchor)] for f in relation_facts if (f, anchor) in margins]
            if values:
                print(f"  {'anchor':14s}{anchor:26s}{float(np.mean(values)):>9.2f}")
    report["main_effects"] = effects

    print("\n" + "=" * 78)
    print("A2  specificity control: the same sentences about a DIFFERENT subject")
    print("    A phrasing effect here would mean copying, not conflict resolution.")
    print("=" * 78)
    control: list[dict[str, Any]] = []
    irrelevant = [r for r in rows if not r.get("claim_is_query_relevant", True)]
    control_margins = {
        (str(r["fact_id"]), str(r["cell_id"])): float(
            r["context_minus_parametric_logprob_margin"]
        )
        for r in irrelevant
    }
    for relation in relations:
        relation_facts = sorted({str(r["fact_id"]) for r in irrelevant if r["relation_id"] == relation})
        if not relation_facts:
            continue
        result = paired_mean_delta(
            control_margins, relation_facts, ["irrelevant_stipulate"],
            ["irrelevant_assert"], args.bootstrap_replicates, seed,
        )
        low, high = result["ci95"]
        control.append({"relation": relation, **result})
        print(
            f"  {relation:17s} stipulate - assert (irrelevant claim) "
            f"{result['delta']:7.2f} [{low:+.2f}, {high:+.2f}]  n={result['n']}"
        )
    report["specificity_control"] = control

    cell_summary: list[dict[str, Any]] = []
    for relation in relations:
        for cell in sorted({str(r["cell_id"]) for r in rows}):
            subset = [r for r in rows if r["relation_id"] == relation and r["cell_id"] == cell]
            if not subset:
                continue
            counts = collections.Counter(r["observed_knowledge_source"] for r in subset)
            n = len(subset)
            cell_summary.append({
                "relation": relation, "cell": cell, "n": n,
                "context_rate": counts.get("contextual", 0) / n,
                "parametric_rate": counts.get("parametric", 0) / n,
                "other_rate": (counts.get("other", 0) + counts.get("unparseable", 0)) / n,
                "margin_positive_rate": float(np.mean(
                    [r["context_minus_parametric_logprob_margin"] > 0 for r in subset]
                )),
                "mean_margin": float(
                    np.mean([r["context_minus_parametric_logprob_margin"] for r in subset])
                ),
            })
    report["cell_summary"] = cell_summary

    write_json_atomic(args.out / "phrasing_summary.json", json_safe(report))
    if cell_summary:
        with (args.out / "phrasing_cells.csv").open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(cell_summary[0].keys()))
            writer.writeheader()
            writer.writerows(cell_summary)

    lines = ["# E7: which property of the claim sentence drives deference?\n"]
    lines.append(
        f"{len(rows)} prompts, {n_facts} facts, neutral policy. Facts, false answers, "
        "screening and distractors are the E8 / E12 pipeline's; the frame (filler, "
        "question, constraint) is E8's. Only the claim sentence varies.\n"
    )
    if anchor_report:
        lines.append("## Anchor reproduction (byte-identical prompts)\n")
        lines.append("| Source | Relation | E7 cell | n | mean d | mean abs d | max abs d |")
        lines.append("|---|---|---|---:|---:|---:|---:|")
        for entry in anchor_report:
            lines.append(
                f"| {entry['source']} | {entry['relation']} | `{entry['cell']}` | {entry['n']} | "
                f"{entry['mean_delta']:+.3f} | {entry['mean_abs_delta']:.3f} | "
                f"{entry['max_abs_delta']:.3f} |"
            )
    lines.append("\n## Main effects (margin, logits)\n")
    lines.append("| Relation | Factor | Contrast | Delta | 95% CI | n |")
    lines.append("|---|---|---|---:|---:|---:|")
    for entry in effects:
        low, high = entry["ci95"]
        lines.append(
            f"| {entry['relation']} | {entry['factor']} | {entry['contrast']} | "
            f"{entry['delta']:.2f} | [{low:+.2f}, {high:+.2f}] | {entry['n']} |"
        )
    lines.append("\n## Behaviour per cell\n")
    lines.append("| Relation | Cell | n | Context | Parametric | Other | M > 0 | Mean margin |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for entry in cell_summary:
        lines.append(
            f"| {entry['relation']} | `{entry['cell']}` | {entry['n']} | "
            f"{100 * entry['context_rate']:.1f}% | {100 * entry['parametric_rate']:.1f}% | "
            f"{100 * entry['other_rate']:.1f}% | {100 * entry['margin_positive_rate']:.1f}% | "
            f"{entry['mean_margin']:.2f} |"
        )
    lines.append("\n## How to read this\n")
    lines.append(
        "- **`act` is the hypothesis.** A large positive stipulate-minus-assert "
        "effect in BOTH relations, surviving the `realization` control, means the "
        "model treats a source that ADOPTS a convention differently from one that "
        "ASSERTS a fact. That is a claim about pragmatics, and it is the version "
        "of this finding worth writing up.\n"
        "- **`realization` is the killer control.** If swapping one verb for a "
        "synonym of the same act moves the margin as much as changing the act, "
        "the result is lexical and the pragmatic reading is wrong. Report this "
        "number next to `act`, never on its own.\n"
        "- **`source` and `persistence`** are the two obvious alternative "
        "explanations. If either rivals `act`, say so.\n"
        "- **`bare`** shows where an unattributed assertion sits. If it lands "
        "near the assert cells, attribution is not what matters; if it is far "
        "from both, the whole effect depends on there being a source at all.\n"
        "- **A2 must be near zero.** A phrasing that lifts the false answer even "
        "when the claim is about another subject is a salience effect, and the "
        "conflict-resolution reading would be wrong.\n"
        "- **Anchors** are cells whose prompts are byte-identical to E8's and "
        "E12's. If their margins do not reproduce within batch noise, nothing "
        "here is comparable to those experiments.\n"
        "- `Other` counts answers that are neither the true nor the paragraph's "
        "(including Gemma's thought-channel residue); `M > 0` is the "
        "residue-free paragraph rate.\n"
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {args.out / 'phrasing_summary.json'}")
    print(f"wrote {report_path}")
    print(f"elapsed {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
