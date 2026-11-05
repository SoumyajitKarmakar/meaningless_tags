#!/usr/bin/env python3
"""E12: what exactly is the <document> wrapper doing?

The paragraph, claim sentence, question and response constraint are held
byte-identical in every row; only the block that encloses the paragraph
changes. Every wrapper is crossed with three cells:

    assert_r1              an attributed false claim about the queried subject
    bare                   the same false answer, unattributed
    irrelevant_assert_r1   the assert_r1 sentence with the SAME false answer,
                           but about a different subject of the same relation

The irrelevant cell asks whether a wrapper lifts the false answer even when
the paragraph claims nothing about the queried subject. If it does, part of
the wrapper effect is priming of a salient token rather than adoption of the
claim. The scored strings are identical in the relevant and irrelevant cells,
so the two are paired within fact and within this run.
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from common import (
    answer_matches,
    append_jsonl,
    CODE_VERSION,
    finalize_jsonl,
    generate_batch,
    is_one_orthographic_word,
    json_safe,
    load_config,
    load_model_bundle,
    normalize_answer,
    read_jsonl,
    render_messages,
    runtime_fingerprint,
    score_continuations,
    seed_everything,
    write_json_atomic,
)

from E8_conventionality import (
    CONSTRAINT,
    FILLER,
    PREDICATES,
    QUESTION,
    SOURCE,
    BARE,
    build_facts,
    stable_seed,
)

ANALYSIS_VERSION = "1.2.0"

IRRELEVANT_PREFIX = "irrelevant_"
IRRELEVANT_CELL = IRRELEVANT_PREFIX + "assert_r1"
CELLS = ("assert_r1", "bare", IRRELEVANT_CELL)

# Each wrapper takes the paragraph and returns the block that replaces it.
# `inline` is the identity, and reproduces E11's baseline exactly.
WRAPPERS: dict[str, str] = {
    "inline": "{p}",
    "blankline": "\n{p}\n",
    "dashes": "---\n{p}\n---",
    "quotes": '"""\n{p}\n"""',
    "tag_document": "<document>\n{p}\n</document>",
    "tag_passage": "<passage>\n{p}\n</passage>",
    "tag_search": "<search_result>\n{p}\n</search_result>",
    "tag_empty": "<>\n{p}\n</>",
    "tag_untrusted": "<untrusted_content>\n{p}\n</untrusted_content>",
    "tag_unreliable": "<unreliable_source>\n{p}\n</unreliable_source>",
    "tag_trusted": "<trusted_content>\n{p}\n</trusted_content>",
    "tag_nonsense": "<qzx_block>\n{p}\n</qzx_block>",
    "tag_gibberish": "<qzxzxew>\n{p}\n</qzxzxew>",
    "label_nonsense": "Qzx_block:\n{p}",
    "label_gibberish": "Qzxzxew:\n{p}",
    "label_document": "Document:\n{p}",
    "label_passage": "Passage:\n{p}",
    "label_search": "Search result:\n{p}",
    "label_untrusted": "Untrusted content:\n{p}",
    "label_unreliable": "Unreliable source:\n{p}",
    "label_trusted": "Trusted content:\n{p}",
}
# What each wrapper is there to rule out, carried into the report so the table
# cannot be read without the reason for each row.
WRAPPER_ROLE = {
    "inline": "baseline",
    "blankline": "layout only",
    "dashes": "layout + fence",
    "quotes": "layout + fence",
    "tag_document": "E11's condition",
    "tag_passage": "same syntax, different word",
    "tag_search": "the RAG framing, as a tag",
    "tag_empty": "bracket syntax, no name at all",
    "tag_untrusted": "same syntax, opposite valence",
    "tag_unreliable": "opposite valence, different words",
    "tag_trusted": "same syntax, positive valence",
    "tag_nonsense": "same syntax, no meaning at all",
    "tag_gibberish": "no meaning at all",
    "label_nonsense": "nonsense label",
    "label_gibberish": "gibberish label",
    "label_document": "same word, no markup",
    "label_passage": "<passage>'s word, no markup",
    "label_search": "the RAG framing",
    "label_untrusted": "opposite valence, no markup",
    "label_unreliable": "<unreliable_source>'s words, no markup",
    "label_trusted": "<trusted_content>'s words, no markup",
}
# The tag x label factorial. Every name appears once as an XML-style tag and
# once as a colon label, so "does the bracket matter?" can be asked of each
# name on its own. The last two names mean nothing.
FACTORIAL: dict[str, tuple[str, str]] = {
    "document": ("tag_document", "label_document"),
    "passage": ("tag_passage", "label_passage"),
    "search_result": ("tag_search", "label_search"),
    "trusted_content": ("tag_trusted", "label_trusted"),
    "untrusted_content": ("tag_untrusted", "label_untrusted"),
    "unreliable_source": ("tag_unreliable", "label_unreliable"),
    "qzx_block": ("tag_nonsense", "label_nonsense"),
    "qzxzxew": ("tag_gibberish", "label_gibberish"),
}
MEANINGLESS_NAMES = ("qzx_block", "qzxzxew")

if set(WRAPPER_ROLE) != set(WRAPPERS):
    raise RuntimeError("Every wrapper needs exactly one WRAPPER_ROLE entry")
if any(w not in WRAPPERS for pair in FACTORIAL.values() for w in pair):
    raise RuntimeError("FACTORIAL names a wrapper that is not in WRAPPERS")

# Fields every scored row copies from its record. The optional ones are absent
# from screening records; scripts reusing evaluate() may add their own.
ROW_FIELDS = (
    "sample_id", "fact_id", "relation_id", "cell_id",
    "wrapper", "claim_sentence", "raw_prompt",
)
OPTIONAL_ROW_FIELDS = ("claim_subject", "claim_is_query_relevant")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--relations", default="element_symbol,country_capital")
    parser.add_argument("--wrappers", default=",".join(WRAPPERS))
    parser.add_argument("--cells", default=",".join(CELLS))
    parser.add_argument(
        "--false-answer-mode", choices=("reuse", "rotation", "random"), default="random"
    )
    parser.add_argument("--false-answer-seed", type=int, default=20260816)
    parser.add_argument(
        "--distractor-seed",
        type=int,
        default=20260816,
        help="Seed for the irrelevant cell's distractor subjects. Assigned over "
        "the full relation before screening, so both models see the same mapping.",
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
# Prompts
# ---------------------------------------------------------------------------


def is_irrelevant(cell: str) -> bool:
    return cell.startswith(IRRELEVANT_PREFIX)


def validate_cell(cell: str) -> None:
    base = cell[len(IRRELEVANT_PREFIX):] if is_irrelevant(cell) else cell
    if base == "bare":
        return
    act, _, realization = base.rpartition("_")
    if not all(act in PREDICATES[r] and realization in PREDICATES[r][act] for r in PREDICATES):
        raise ValueError(
            f"Unknown cell {cell!r}: expected bare, <act>_<realization> from E8's "
            f"PREDICATES, or either with the {IRRELEVANT_PREFIX!r} prefix"
        )


def claim_sentence(
    relation: str,
    cell: str,
    subject: str,
    answer: str,
    distractor: str | None = None,
) -> str:
    """The paragraph's first sentence.

    An ``irrelevant_`` cell is its base cell with the queried subject replaced
    by the fact's distractor. The false answer is unchanged.
    """
    if is_irrelevant(cell):
        if not distractor:
            raise ValueError(f"Cell {cell!r} needs a distractor subject")
        return claim_sentence(relation, cell[len(IRRELEVANT_PREFIX):], distractor, answer)
    if cell == "bare":
        return BARE[relation].format(s=subject, a=answer)
    act, realization = cell.rsplit("_", 1)
    return f"{SOURCE[relation]} {PREDICATES[relation][act][realization]}.".format(
        s=subject, a=answer
    )


def build_prompt(
    relation: str,
    wrapper: str,
    claim: str,
    subject: str,
    templates: Mapping[str, str] = WRAPPERS,
) -> str:
    """Only the wrapper changes. The paragraph, question and constraint do not."""
    paragraph = f"{claim} {FILLER[relation]}"
    block = templates[wrapper].format(p=paragraph)
    question = QUESTION[relation].format(s=subject)
    return f"{block}\n\n{question}\n{CONSTRAINT[relation]}"


def mentions(text: str, answer: str) -> bool:
    """Whether `answer` occurs in `text` as a whole word (case-sensitive,
    because element symbols are: "As" is arsenic, "as" is not)."""
    return re.search(rf"(?<!\w){re.escape(answer)}(?!\w)", text) is not None


# ---------------------------------------------------------------------------
# Facts
# ---------------------------------------------------------------------------


def assign_distractors(
    facts: Sequence[Mapping[str, Any]],
    seed: int,
) -> list[dict[str, Any]]:
    """Give every fact a distractor subject from its own relation.

    Within each relation the distractors are a seeded permutation, so every
    subject is used exactly once as a distractor. Two constraints keep the
    irrelevant paragraph a false claim about a different subject:

      * the distractor is never the queried subject itself;
      * the distractor is never the subject whose TRUE answer is the fact's
        false answer, because "the symbol for Boron is B" would be true.

    Call this on the full relation, before truncation and screening, so a
    pilot, a full run and both models all see the same mapping.
    """
    out = [dict(fact) for fact in facts]
    by_relation: dict[str, list[dict[str, Any]]] = {}
    for fact in out:
        by_relation.setdefault(str(fact["relation_id"]), []).append(fact)
    for relation, group in by_relation.items():
        size = len(group)
        forbidden: list[set[int]] = []
        for index, fact in enumerate(group):
            false_answer = normalize_answer(fact["claim_answer"])
            banned = {index}
            banned.update(
                other_index
                for other_index, other in enumerate(group)
                if any(
                    normalize_answer(answer) == false_answer
                    for answer in other["acceptable_world_true_answers"]
                )
            )
            forbidden.append(banned)
        rng = random.Random(stable_seed(seed, relation, "distractor"))
        order = list(range(size))
        for _ in range(100_000):
            rng.shuffle(order)
            if all(order[index] not in forbidden[index] for index in range(size)):
                break
        else:
            raise RuntimeError(f"Could not assign distractors for {relation} ({size} facts)")
        for index, fact in enumerate(group):
            other = group[order[index]]
            fact["distractor_subject"] = other["query_subject"]
            fact["distractor_fact_id"] = other["fact_id"]
            fact["distractor_world_true_answer"] = other["world_true_answer"]
    return out


def first_per_relation(
    facts: Sequence[dict[str, Any]],
    max_facts: int | None,
) -> list[dict[str, Any]]:
    """The first `max_facts` facts of each relation, in order -- the same
    truncation build_facts applies, done after distractor assignment."""
    if max_facts is None:
        return list(facts)
    taken: dict[str, int] = {}
    kept = []
    for fact in facts:
        relation = str(fact["relation_id"])
        if taken.get(relation, 0) < max_facts:
            kept.append(fact)
            taken[relation] = taken.get(relation, 0) + 1
    return kept


# ---------------------------------------------------------------------------
# Records, classification, evaluation
# ---------------------------------------------------------------------------


def classify(record: Mapping[str, Any], text: str) -> str:
    if not is_one_orthographic_word(text):
        return "unparseable"
    parametric = answer_matches(text, list(record["acceptable_world_true_answers"]))
    contextual = normalize_answer(text) == normalize_answer(record["context_candidate_answer"])
    if parametric and contextual:
        return "shared_parametric_and_context"
    if parametric:
        return "parametric"
    if contextual:
        return "contextual"
    return "other"


def build_records(
    facts: Sequence[Mapping[str, Any]],
    wrappers: Sequence[str],
    cells: Sequence[str],
    templates: Mapping[str, str] = WRAPPERS,
    prefix: str = "e12",
) -> list[dict[str, Any]]:
    records = []
    for fact in facts:
        relation = str(fact["relation_id"])
        subject, answer = str(fact["query_subject"]), str(fact["claim_answer"])
        for cell in cells:
            irrelevant = is_irrelevant(cell)
            distractor = fact.get("distractor_subject")
            claim = claim_sentence(relation, cell, subject, answer, distractor)
            if irrelevant:
                if normalize_answer(str(distractor)) == normalize_answer(subject):
                    raise ValueError(f"{fact['fact_id']}: distractor is the queried subject")
                if any(
                    mentions(claim, str(true_answer))
                    for true_answer in fact["acceptable_world_true_answers"]
                ):
                    raise ValueError(
                        f"{fact['fact_id']}: the irrelevant claim {claim!r} names the "
                        "queried subject's true answer"
                    )
            for wrapper in wrappers:
                prompt = build_prompt(relation, wrapper, claim, subject, templates)
                records.append(
                    {
                        "sample_id": f"{prefix}-{fact['fact_id']}-{cell}-{wrapper}",
                        "messages": [{"role": "user", "content": prompt}],
                        "fact_id": fact["fact_id"],
                        "relation_id": relation,
                        "cell_id": cell,
                        "wrapper": wrapper,
                        "claim_sentence": claim,
                        "claim_subject": str(distractor) if irrelevant else subject,
                        "claim_is_query_relevant": not irrelevant,
                        "raw_prompt": prompt,
                        "context_candidate_answer": answer,
                        "acceptable_world_true_answers": list(
                            fact["acceptable_world_true_answers"]
                        ),
                        "parametric_candidate_answer": fact["world_true_answer"],
                    }
                )
    return records


def screening_records(
    facts: Sequence[Mapping[str, Any]],
    prefix: str = "e12",
) -> list[dict[str, Any]]:
    records = []
    for fact in facts:
        relation = str(fact["relation_id"])
        prompt = (
            f"{QUESTION[relation].format(s=fact['query_subject'])}\n{CONSTRAINT[relation]}"
        )
        records.append(
            {
                "sample_id": f"{prefix}screen-{fact['fact_id']}",
                "messages": [{"role": "user", "content": prompt}],
                "fact_id": fact["fact_id"],
                "relation_id": relation,
                "cell_id": "screen",
                "wrapper": "inline",
                "claim_sentence": "",
                "raw_prompt": prompt,
                "context_candidate_answer": fact["claim_answer"],
                "acceptable_world_true_answers": list(fact["acceptable_world_true_answers"]),
                "parametric_candidate_answer": fact["world_true_answer"],
            }
        )
    return records


def screened_facts(
    facts: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
    prefix: str = "e12",
) -> list[Mapping[str, Any]]:
    """Facts whose context-free answer is the true one AND preferred over the
    false one -- the same gate as 01_screen_knowledge.py."""
    scored = {str(r["sample_id"]): r for r in rows if str(r["cell_id"]) == "screen"}
    return [
        fact for fact in facts
        if (row := scored.get(f"{prefix}screen-{fact['fact_id']}")) is not None
        and row["observed_knowledge_source"] == "parametric"
        and float(row["context_minus_parametric_logprob_margin"]) < 0
    ]


def evaluate(
    records: Sequence[Mapping[str, Any]],
    bundle: Any,
    config: Mapping[str, Any],
    partial_path: Path,
    generation_batch: int,
    scoring_batch: int,
    started: float,
    carry: Sequence[str] = (),
    analysis_version: str = ANALYSIS_VERSION,
) -> None:
    """Greedy answer plus teacher-forced margin for every record.

    `carry` names extra record fields to copy onto each row unchanged; scripts
    reusing this loop pass their own `analysis_version`.
    """
    max_input = int(config["chat"]["max_input_tokens"])
    for start in range(0, len(records), generation_batch):
        chunk = records[start : start + generation_batch]
        rendered = [render_messages(bundle.processor, r["messages"], config) for r in chunk]
        generations = generate_batch(bundle.model, bundle.tokenizer, rendered, config)

        requests: list[dict[str, str]] = []
        for index, record in enumerate(chunk):
            requests.append(
                {
                    "key": f"{index}|context",
                    "rendered_text": rendered[index],
                    "continuation": str(record["context_candidate_answer"]),
                }
            )
            for alias, answer in enumerate(record["acceptable_world_true_answers"]):
                requests.append(
                    {
                        "key": f"{index}|parametric|{alias}",
                        "rendered_text": rendered[index],
                        "continuation": str(answer),
                    }
                )
        scores = score_continuations(
            bundle.model, bundle.tokenizer, requests, scoring_batch, max_input
        )
        by_key = {s.key: s for s in scores}

        output = []
        for index, record in enumerate(chunk):
            context_score = by_key[f"{index}|context"]
            best = max(
                (
                    by_key[f"{index}|parametric|{alias}"]
                    for alias in range(len(record["acceptable_world_true_answers"]))
                ),
                key=lambda s: s.sum_logprob,
            )
            generation = generations[index]
            answer = str(generation.get("answer_text") or generation["text"])
            output.append(
                {
                    "code_version": CODE_VERSION,
                    "analysis_version": analysis_version,
                    **{k: record[k] for k in ROW_FIELDS},
                    **{k: record.get(k) for k in (*OPTIONAL_ROW_FIELDS, *carry)},
                    "generated_answer": generation["text"],
                    "generated_answer_stripped": answer,
                    "had_reasoning_preamble": bool(
                        generation.get("had_reasoning_preamble", False)
                    ),
                    "format_compliant": is_one_orthographic_word(generation["text"]),
                    "observed_knowledge_source": classify(record, answer),
                    "context_answer": record["context_candidate_answer"],
                    "parametric_answer": best.continuation,
                    "context_answer_sequence_logprob": context_score.sum_logprob,
                    "parametric_answer_sequence_logprob": best.sum_logprob,
                    "context_minus_parametric_logprob_margin": (
                        context_score.sum_logprob - best.sum_logprob
                    ),
                }
            )
        append_jsonl(partial_path, output)
        if (start // generation_batch) % 20 == 0:
            print(f"  {start + len(chunk)}/{len(records)} ({time.time() - started:7.1f}s)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    import numpy as np

    from paired_stats import bootstrap_mean_ci

    started = time.time()
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results_path = args.out / "delimiter_results.jsonl"
    partial_path = args.out / "delimiter_results.jsonl.partial"
    report_path = args.out / "delimiter_report.md"
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
    wrappers = [w.strip() for w in args.wrappers.split(",") if w.strip()]
    cells = [c.strip() for c in args.cells.split(",") if c.strip()]
    for wrapper in wrappers:
        if wrapper not in WRAPPERS:
            raise ValueError(f"Unknown wrapper {wrapper!r}; expected {sorted(WRAPPERS)}")
    if "inline" not in wrappers:
        raise ValueError("`inline` is the baseline that reproduces E11; keep it in")
    for cell in cells:
        validate_cell(cell)
    if len(set(wrappers)) != len(wrappers) or len(set(cells)) != len(cells):
        raise ValueError("--wrappers and --cells must not repeat an entry")

    # Distractors are assigned over the full relation, then truncated, so a
    # pilot's mapping matches the full run's.
    facts = assign_distractors(
        build_facts(
            relations, None, None,
            mode=args.false_answer_mode, seed=args.false_answer_seed,
        ),
        args.distractor_seed,
    )
    facts = first_per_relation(facts, args.max_facts)
    print(f"model: {config['model']['id']}")
    print(f"facts before screening: {len(facts)}   mode {args.false_answer_mode}")

    if args.validate_only:
        example = facts[0]
        relation = str(example["relation_id"])
        subject, answer = str(example["query_subject"]), str(example["claim_answer"])
        for wrapper in wrappers:
            print(f"\n{'=' * 78}\n{wrapper}  ({WRAPPER_ROLE.get(wrapper, '')})\n{'=' * 78}")
            print(
                build_prompt(
                    relation, wrapper,
                    claim_sentence(relation, "assert_r1", subject, answer),
                    subject,
                )
            )
        print(f"\n{'=' * 78}\nclaim sentence per cell, for {subject}\n{'=' * 78}")
        for cell in cells:
            claim = claim_sentence(
                relation, cell, subject, answer, example.get("distractor_subject")
            )
            print(f"  [{cell:22s}] {claim}")
        irrelevant_cells = [c for c in cells if is_irrelevant(c)]
        if irrelevant_cells:
            cell = irrelevant_cells[0]
            print(f"\nfull prompt, {cell}, inline:\n")
            print(
                build_prompt(
                    relation, "inline",
                    claim_sentence(relation, cell, subject, answer, example["distractor_subject"]),
                    subject,
                )
            )
            print("\ndistractors (first five per relation):")
            for name in relations:
                for fact in [f for f in facts if f["relation_id"] == name][:5]:
                    print(
                        f"  {name:16s} asks about {fact['query_subject']!r:24s} "
                        f"paragraph about {fact['distractor_subject']!r:24s} "
                        f"false answer {fact['claim_answer']!r}"
                    )
        print(
            f"\nvalidate-only: {len(facts)} screening + "
            f"{len(build_records(facts, wrappers, cells))} experimental prompts"
        )
        return

    if args.analyze_only:
        if not results_path.is_file():
            raise FileNotFoundError(f"--analyze-only needs an existing {results_path}")
        rows = read_jsonl(results_path)
        fingerprint: Any = {"note": "analyze-only; the model was not loaded"}
    else:
        seed_everything(int(config["project"]["seed"]))
        done: set[str] = set()
        if partial_path.exists() and not args.overwrite:
            done = {str(r["sample_id"]) for r in read_jsonl(partial_path)}
            print(f"resuming: {len(done)} prompts already scored")
        elif partial_path.exists():
            partial_path.unlink()

        bundle = load_model_bundle(config)
        fingerprint = runtime_fingerprint(config, bundle, {})
        generation_batch = args.generation_batch_size or int(
            config["collection"]["generation_batch_size"]
        )
        scoring_batch = args.scoring_batch_size or int(
            config["collection"]["scoring_batch_size"]
        )

        if not args.skip_screening:
            print("\nscreening (context-free)")
            screen = [r for r in screening_records(facts) if r["sample_id"] not in done]
            evaluate(screen, bundle, config, partial_path, generation_batch,
                     scoring_batch, started)
            kept = screened_facts(facts, read_jsonl(partial_path))
            print(f"  kept {len(kept)}/{len(facts)} facts")
            facts = list(kept)
            if not facts:
                raise RuntimeError("No facts survived screening")

        experiment = [
            r for r in build_records(facts, wrappers, cells)
            if r["sample_id"] not in done
        ]
        print(f"\nscoring {len(experiment)} experimental prompts")
        evaluate(experiment, bundle, config, partial_path, generation_batch,
                 scoring_batch, started)
        rows = read_jsonl(partial_path)
        finalize_jsonl(partial_path, results_path)
        print(f"\nscored {len(rows)} prompts total")

    # ---- analysis ----------------------------------------------------------
    seed = int(config["project"]["seed"])
    live = [r for r in rows if r["cell_id"] != "screen"]
    margins: dict[tuple[str, str, str], float] = {}
    contextual: dict[tuple[str, str, str], bool] = {}
    for r in live:
        key = (str(r["fact_id"]), str(r["cell_id"]), str(r["wrapper"]))
        margins[key] = float(r["context_minus_parametric_logprob_margin"])
        contextual[key] = r["observed_knowledge_source"] == "contextual"
    wrappers_seen = [w for w in wrappers if any(k[2] == w for k in margins)]
    cells_seen = [c for c in cells if any(k[1] == c for k in margins)]
    skipped = sorted(set(wrappers) - set(wrappers_seen)) + sorted(set(cells) - set(cells_seen))
    if skipped:
        print(f"\nNOTE: no rows for {skipped}; analysing what the results file holds")

    summary, contrasts = [], []
    print("\n" + "=" * 78)
    print("wrapper effect, paired within fact against `inline` (same cell)")
    print("=" * 78)
    for relation in relations:
        print(f"\n{relation}")
        print(f"  {'wrapper':18s}{'role':40s}{'cell':22s}"
              f"{'context':>9s}{'margin':>9s}{'vs inline':>11s}{'95% CI':>18s}{'d>0':>9s}")
        fact_ids = sorted({str(r["fact_id"]) for r in live if r["relation_id"] == relation})
        for wrapper in wrappers_seen:
            for cell in cells_seen:
                present = [f for f in fact_ids if (f, cell, wrapper) in margins]
                if not present:
                    continue
                rate = float(np.mean([contextual[(f, cell, wrapper)] for f in present]))
                margin = float(np.mean([margins[(f, cell, wrapper)] for f in present]))
                paired = [f for f in present if (f, cell, "inline") in margins]
                deltas = np.asarray(
                    [margins[(f, cell, wrapper)] - margins[(f, cell, "inline")] for f in paired]
                )
                if paired:
                    delta = float(deltas.mean())
                    low, high = bootstrap_mean_ci(deltas, args.bootstrap_replicates, seed)
                    positive = int(np.sum(deltas > 0))
                else:
                    delta, low, high, positive = float("nan"), float("nan"), float("nan"), 0
                print(
                    f"  {wrapper:18s}{WRAPPER_ROLE.get(wrapper, ''):40s}{cell:22s}"
                    f"{100 * rate:>8.1f}%{margin:>9.2f}{delta:>11.2f}"
                    f"{f'[{low:+.1f}, {high:+.1f}]':>18}{f'{positive}/{len(paired)}':>9s}"
                )
                summary.append({
                    "relation": relation, "wrapper": wrapper, "cell": cell,
                    "role": WRAPPER_ROLE.get(wrapper, ""), "n": len(present),
                    "context_rate": rate, "mean_margin": margin,
                    "delta_vs_inline": delta, "delta_ci_low": low, "delta_ci_high": high,
                    "n_positive": positive, "n_paired": len(paired),
                })
                contrasts.append({
                    "relation": relation, "wrapper": wrapper, "cell": cell,
                    "delta_vs_inline": delta, "ci95": [low, high], "n": len(paired),
                    "n_positive": positive,
                })

    # ---- relevance: is part of the wrapper effect token priming? ----------
    relevance: list[dict[str, Any]] = []
    baseline_relevance: list[dict[str, Any]] = []
    if "assert_r1" in cells_seen and IRRELEVANT_CELL in cells_seen:
        print("\n" + "=" * 78)
        print("relevance: the wrapper effect on a paragraph about ANOTHER subject")
        print("  interaction = (wrapper - inline | relevant) - (wrapper - inline | irrelevant)")
        print("=" * 78)
        for relation in relations:
            fact_ids = sorted({str(r["fact_id"]) for r in live if r["relation_id"] == relation})
            usable = [
                f for f in fact_ids
                if (f, "assert_r1", "inline") in margins
                and (f, IRRELEVANT_CELL, "inline") in margins
            ]
            if usable:
                gap = np.asarray([
                    margins[(f, "assert_r1", "inline")] - margins[(f, IRRELEVANT_CELL, "inline")]
                    for f in usable
                ])
                low, high = bootstrap_mean_ci(gap, args.bootstrap_replicates, seed)
                baseline_relevance.append({
                    "relation": relation, "n": len(usable),
                    "relevant_minus_irrelevant_inline": float(gap.mean()),
                    "ci95": [low, high], "n_positive": int(np.sum(gap > 0)),
                })
                print(f"\n{relation}: unwrapped, relevant - irrelevant = "
                      f"{gap.mean():+.2f} [{low:+.2f}, {high:+.2f}]  "
                      f"({int(np.sum(gap > 0))}/{len(usable)} facts > 0)")
            print(f"  {'wrapper':18s}{'d relevant':>12s}{'d irrelevant':>14s}"
                  f"{'interaction':>13s}{'95% CI':>18s}{'irr/rel':>9s}")
            for wrapper in wrappers_seen:
                if wrapper == "inline":
                    continue
                paired = [
                    f for f in usable
                    if (f, "assert_r1", wrapper) in margins
                    and (f, IRRELEVANT_CELL, wrapper) in margins
                ]
                if not paired:
                    continue
                relevant = np.asarray([
                    margins[(f, "assert_r1", wrapper)] - margins[(f, "assert_r1", "inline")]
                    for f in paired
                ])
                irrelevant = np.asarray([
                    margins[(f, IRRELEVANT_CELL, wrapper)] - margins[(f, IRRELEVANT_CELL, "inline")]
                    for f in paired
                ])
                interaction = relevant - irrelevant
                low, high = bootstrap_mean_ci(interaction, args.bootstrap_replicates, seed)
                share = (
                    float(irrelevant.mean() / relevant.mean())
                    if relevant.mean() != 0 else float("nan")
                )
                relevance.append({
                    "relation": relation, "wrapper": wrapper, "n": len(paired),
                    "delta_relevant": float(relevant.mean()),
                    "delta_irrelevant": float(irrelevant.mean()),
                    "interaction": float(interaction.mean()),
                    "ci95": [low, high],
                    "irrelevant_share": share,
                })
                print(
                    f"  {wrapper:18s}{relevant.mean():>12.2f}{irrelevant.mean():>14.2f}"
                    f"{interaction.mean():>13.2f}{f'[{low:+.1f}, {high:+.1f}]':>18}"
                    f"{share:>9.2f}"
                )

    report = {
        "analysis_version": ANALYSIS_VERSION,
        "runtime": fingerprint,
        "model": config["model"]["id"],
        "false_answer_mode": args.false_answer_mode,
        "false_answer_seed": args.false_answer_seed,
        "distractor_seed": args.distractor_seed,
        "wrappers": {w: WRAPPERS[w] for w in wrappers_seen},
        "wrapper_roles": WRAPPER_ROLE,
        "factorial": {name: list(pair) for name, pair in FACTORIAL.items()},
        "cells": summary,
        "contrasts_vs_inline": contrasts,
        "relevance_baseline": baseline_relevance,
        "relevance_by_wrapper": relevance,
    }
    write_json_atomic(args.out / "delimiter_summary.json", json_safe(report))
    if summary:
        with (args.out / "delimiter_cells.csv").open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(summary[0].keys()))
            writer.writeheader()
            writer.writerows(summary)

    lines = [f"# E12: what the wrapper is doing — {config['model']['id']}\n"]
    lines.append(
        "The paragraph, claim sentence, question and response constraint are "
        "byte-identical in every row. Only the block that encloses the paragraph "
        "changes. `delta vs inline` is paired within fact and cell, and "
        "bootstrapped over facts. `d>0` counts facts whose margin rose.\n"
    )
    lines.append(
        "\n| Relation | Wrapper | What it rules out | Cell | n | Context | Margin "
        "| Δ vs inline | 95% CI | d>0 |"
    )
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|")
    for entry in summary:
        lines.append(
            f"| {entry['relation']} | `{entry['wrapper']}` | {entry['role']} | "
            f"`{entry['cell']}` | {entry['n']} | {100 * entry['context_rate']:.1f}% | "
            f"{entry['mean_margin']:.2f} | {entry['delta_vs_inline']:+.2f} | "
            f"[{entry['delta_ci_low']:+.2f}, {entry['delta_ci_high']:+.2f}] | "
            f"{entry['n_positive']}/{entry['n_paired']} |"
        )
    if relevance:
        lines.append("\n## Relevance: the same wrapper around a paragraph about another subject\n")
        for entry in baseline_relevance:
            low, high = entry["ci95"]
            lines.append(
                f"- {entry['relation']}, unwrapped: relevant − irrelevant = "
                f"{entry['relevant_minus_irrelevant_inline']:+.2f} [{low:+.2f}, {high:+.2f}], "
                f"{entry['n_positive']}/{entry['n']} facts > 0."
            )
        lines.append(
            "\n| Relation | Wrapper | n | Δ relevant | Δ irrelevant | Interaction | 95% CI "
            "| Irrelevant / relevant |"
        )
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
        for entry in relevance:
            low, high = entry["ci95"]
            lines.append(
                f"| {entry['relation']} | `{entry['wrapper']}` | {entry['n']} | "
                f"{entry['delta_relevant']:+.2f} | {entry['delta_irrelevant']:+.2f} | "
                f"{entry['interaction']:+.2f} | [{low:+.2f}, {high:+.2f}] | "
                f"{entry['irrelevant_share']:.2f} |"
            )
    lines.append("\n## How to read this\n")
    lines.append(
        "- **`blankline` is the layout control.** If it moves the margin as much "
        "as `tag_document`, E11's effect was whitespace and the document framing "
        "is a red herring. If it does not, the markup is doing real work.\n"
        "- **`tag_passage` versus `tag_document`** separates the syntax from the "
        "word. **`label_document`** separates the word from the syntax.\n"
        "- **The tag × label factorial.** Every name -- document, passage, "
        "search_result, trusted_content, untrusted_content, unreliable_source, "
        "qzx_block, qzxzxew -- appears once as `<name>` and once as `Name:`, so "
        "the bracket's contribution can be read off per name. If brackets matter "
        "only for the meaningless names, the bracket and the word are two routes "
        "to the same place.\n"
        "- **`tag_untrusted` is the one to report.** It is the tag whose entire "
        "purpose is to mark text as not-to-be-trusted. If deference under it "
        "matches `tag_document`, the wrapper is read as *this is source "
        "material* and its stated valence is ignored. If it does NOT -- if the "
        "tag suppresses deference -- then the model is reading the label's "
        "meaning, and the question becomes why the same words fail when they "
        "are put in the system prompt instead.\n"
        "- **`tag_nonsense` is the control for that reading.** `<qzx_block>` "
        "carries the same syntax and no meaning. If it behaves like "
        "`<document>`, an unfamiliar tag is not inherently suppressive and a "
        "low score for `<untrusted_content>` really is about the word. If it "
        "behaves like `<untrusted_content>`, then any out-of-distribution tag "
        "suppresses deference and the semantic reading is wrong. "
        "`tag_trusted` and `tag_unreliable` place the same contrast on a scale. "
        "E13 replaces these two strings with a sample of thirty.\n"
        "- **`tag_empty` splits the structure term itself.** `<qzx_block>` still "
        "has a name; `<>` has only the brackets. If `<>` matches `<qzx_block>`, "
        "the name contributes nothing and the structural effect is the bracket "
        "syntax. If `<>` falls back toward `dashes`, then a tag needs to NAME "
        "something -- anything -- and `<qzx_block>`'s +31 was already partly "
        "semantic.\n"
        "- **`bare` versus `assert_r1`** asks whether the wrapper confers source "
        "authority or changes the task. `bare` has no source to trust, so if it "
        "swings too, the model is switching into reading-comprehension mode "
        "rather than deciding whom to believe.\n"
        f"- **`{IRRELEVANT_CELL}` is the priming control.** The same sentence and "
        "the same false answer, about a different subject, so the paragraph "
        "never claims anything about the queried one. A wrapper that lifts the "
        "false answer here is priming a salient token, not getting a claim "
        "adopted. The interaction column is the part of the wrapper effect that "
        "needs the claim to be about the queried subject.\n"
        "- Margins are teacher-forced. Rates classify the answer with any "
        "reasoning preamble stripped.\n"
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {report_path}")
    print(f"elapsed {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
