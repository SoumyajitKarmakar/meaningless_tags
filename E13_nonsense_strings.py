#!/usr/bin/env python3
"""E13: is "a meaningless tag works" a distribution or an anecdote?

E12 rests that claim on two strings that disagree, <qzx_block> and <qzxzxew>.
Here thirty random letter strings, length-matched to `document`, are each used
twice around the identical paragraph -- as an XML-style tag

    <splyojax>
    ...paragraph...
    </splyojax>

and as a colon label

    Splyojax:
    ...paragraph...

-- so the effect of an unfamiliar name, and of the brackets around it, becomes
a distribution over strings. Every string is its own tag-versus-label pair, so
the bracket effect is paired within string as well as within fact.

The two original strings run here too, in both forms, so they can be placed in
that distribution within one run; they double as a reproducibility check
against E12. The names live in random_tag_names.json, generated once with
--make-names and committed, so every model reads the same strings.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

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
from E8_conventionality import build_facts
from E12_delimiter import (
    WRAPPERS as E12_WRAPPERS,
    build_prompt,
    claim_sentence,
    evaluate,
    screened_facts,
    screening_records,
)

ANALYSIS_VERSION = "1.0.0"
PREFIX = "e13"
CELLS = ("assert_r1", "bare")
DEFAULT_NAMES_FILE = Path(__file__).resolve().parent / "random_tag_names.json"
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
# A random name may not contain a word any meaningful wrapper uses, the real
# word inside <qzx_block>, or the original nonsense strings' stem.
BLOCKED_SUBSTRINGS = (
    "document", "passage", "search", "result", "trust", "reliable",
    "source", "content", "block", "qzx",
)
# E12 wrappers re-run here as within-run reference points.
DEFAULT_REFERENCES = ("tag_nonsense", "label_nonsense", "tag_gibberish", "label_gibberish")
# Per-wrapper fields copied onto every scored row.
CARRY = ("name", "name_index", "form", "wrapper_source", "marker_text", "marker_num_tokens")
FORMS = ("tag", "label")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--names-file", type=Path, default=DEFAULT_NAMES_FILE)
    parser.add_argument(
        "--make-names",
        action="store_true",
        help="Generate --names-file from --n-names/--name-length/--names-seed and exit.",
    )
    parser.add_argument("--n-names", type=int, default=30)
    parser.add_argument("--name-length", type=int, default=len("document"))
    parser.add_argument("--names-seed", type=int, default=20260816)
    parser.add_argument("--overwrite-names", action="store_true")
    parser.add_argument(
        "--max-names",
        type=int,
        default=None,
        help="Use only the first N names (smoke tests).",
    )
    parser.add_argument(
        "--references",
        default=",".join(DEFAULT_REFERENCES),
        help="E12 wrappers to re-run as reference points; empty for none.",
    )
    parser.add_argument("--relations", default="element_symbol,country_capital")
    parser.add_argument("--cells", default="assert_r1")
    parser.add_argument(
        "--false-answer-mode", choices=("reuse", "rotation", "random"), default="random"
    )
    parser.add_argument("--false-answer-seed", type=int, default=20260816)
    parser.add_argument("--max-facts", type=int, default=None)
    parser.add_argument("--generation-batch-size", type=int, default=None)
    parser.add_argument("--scoring-batch-size", type=int, default=None)
    parser.add_argument("--bootstrap-replicates", type=int, default=2000)
    parser.add_argument("--permutations", type=int, default=20_000)
    parser.add_argument("--skip-screening", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--analyze-only", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Names and wrappers
# ---------------------------------------------------------------------------


def make_names(count: int, length: int, seed: int) -> list[str]:
    """`count` distinct strings drawn uniformly from ALPHABET**length."""
    if count < 1 or length < 1:
        raise ValueError("--n-names and --name-length must be positive")
    rng = random.Random(seed)
    names: list[str] = []
    while len(names) < count:
        name = "".join(rng.choice(ALPHABET) for _ in range(length))
        if name in names or any(word in name for word in BLOCKED_SUBSTRINGS):
            continue
        names.append(name)
    return names


def write_names(path: Path, count: int, length: int, seed: int, overwrite: bool) -> list[str]:
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite {path}; every model must read the same names. "
            "Pass --overwrite-names only before any model has been run."
        )
    names = make_names(count, length, seed)
    write_json_atomic(
        path,
        {
            "description": (
                "Random tag names for E13_nonsense_strings.py, generated once with "
                "--make-names. Every model reads this file; do not regenerate it "
                "between runs."
            ),
            "seed": seed,
            "length": length,
            "count": count,
            "alphabet": ALPHABET,
            "blocked_substrings": list(BLOCKED_SUBSTRINGS),
            "names": names,
        },
    )
    return names


def read_names(path: Path) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(
            f"No names file at {path}. Generate it once with --make-names and commit it."
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    names = [str(name) for name in payload["names"]]
    if not names:
        raise ValueError(f"{path} lists no names")
    if len(set(names)) != len(names):
        raise ValueError(f"{path} repeats a name")
    for name in names:
        if any(character not in ALPHABET for character in name):
            raise ValueError(f"{name!r} in {path} is not lower-case ASCII letters")
    try:
        regenerated = make_names(
            int(payload["count"]), int(payload["length"]), int(payload["seed"])
        )
    except (KeyError, TypeError, ValueError):
        regenerated = None
    if regenerated != names:
        print(f"WARNING: {path} does not match its recorded seed; using the file as-is")
    return names


def wrapper_table(
    names: Sequence[str],
    references: Sequence[str],
) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    """Templates in run order, and the per-wrapper fields carried onto rows."""
    templates: dict[str, str] = {"inline": E12_WRAPPERS["inline"]}
    meta: dict[str, dict[str, Any]] = {
        "inline": {"name": "", "name_index": None, "form": "baseline",
                   "wrapper_source": "baseline"},
    }
    for wrapper in references:
        if wrapper not in E12_WRAPPERS or wrapper == "inline":
            raise ValueError(f"Unknown reference wrapper {wrapper!r}")
        template = E12_WRAPPERS[wrapper]
        form = (
            "tag" if wrapper.startswith("tag_")
            else "label" if wrapper.startswith("label_") else "other"
        )
        templates[wrapper] = template
        meta[wrapper] = {
            "name": template.split("\n", 1)[0].strip("<>:/").lower(),
            "name_index": None, "form": form, "wrapper_source": "reference",
        }
    for index, name in enumerate(names):
        for form, wrapper, template in (
            ("tag", f"rtag_{name}", f"<{name}>\n{{p}}\n</{name}>"),
            ("label", f"rlabel_{name}", f"{name.capitalize()}:\n{{p}}"),
        ):
            if wrapper in templates:
                raise ValueError(f"Duplicate wrapper {wrapper!r}")
            templates[wrapper] = template
            meta[wrapper] = {"name": name, "name_index": index, "form": form,
                             "wrapper_source": "random"}
    for wrapper, template in templates.items():
        meta[wrapper]["marker_text"] = (
            "" if template == "{p}" else template.split("\n", 1)[0]
        )
        meta[wrapper]["marker_num_tokens"] = None
    return templates, meta


def count_tokens(tokenizer: Any, text: str) -> int:
    """Tokens in `text` on its own. In the prompt the count can differ by one
    where a merge crosses the preceding boundary; this is a covariate, not a
    position."""
    if not text:
        return 0
    ids = tokenizer(text, add_special_tokens=False)["input_ids"]
    if ids and isinstance(ids[0], list):
        ids = ids[0]
    return len(ids)


def build_records(
    facts: Sequence[Mapping[str, Any]],
    templates: Mapping[str, str],
    meta: Mapping[str, Mapping[str, Any]],
    cells: Sequence[str],
) -> list[dict[str, Any]]:
    records = []
    for fact in facts:
        relation = str(fact["relation_id"])
        subject, answer = str(fact["query_subject"]), str(fact["claim_answer"])
        for cell in cells:
            claim = claim_sentence(relation, cell, subject, answer)
            for wrapper in templates:
                prompt = build_prompt(relation, wrapper, claim, subject, templates)
                records.append(
                    {
                        "sample_id": f"{PREFIX}-{fact['fact_id']}-{cell}-{wrapper}",
                        "messages": [{"role": "user", "content": prompt}],
                        "fact_id": fact["fact_id"],
                        "relation_id": relation,
                        "cell_id": cell,
                        "wrapper": wrapper,
                        "claim_sentence": claim,
                        "claim_subject": subject,
                        "claim_is_query_relevant": True,
                        "raw_prompt": prompt,
                        "context_candidate_answer": answer,
                        "acceptable_world_true_answers": list(
                            fact["acceptable_world_true_answers"]
                        ),
                        "parametric_candidate_answer": fact["world_true_answer"],
                        **{k: meta[wrapper][k] for k in CARRY},
                    }
                )
    return records


# ---------------------------------------------------------------------------
# Analysis (also used by make_tables.py)
# ---------------------------------------------------------------------------


def analyse(
    rows: Sequence[Mapping[str, Any]],
    relations: Sequence[str],
    cells: Sequence[str],
    replicates: int = 2000,
    permutations: int = 20_000,
    seed: int = 20260816,
) -> dict[str, list[dict[str, Any]]]:
    """Per-wrapper effects and the distribution over random strings.

    Every effect is ΔM against `inline` in the same relation and cell, paired
    within fact. Across strings, the grand mean gets a crossed bootstrap
    (strings and facts resampled together), and the tag-minus-label gap is
    also tested across strings with a Wilcoxon signed-rank test, each string
    being one pair.
    """
    import numpy as np

    from paired_stats import (
        bootstrap_mean_ci,
        crossed_bootstrap_mean_ci,
        sign_counts,
        sign_test_p,
        spearman_permutation,
        wilcoxon_p,
    )

    margins: dict[tuple[str, str, str, str], float] = {}
    contextual: dict[tuple[str, str, str, str], bool] = {}
    info: dict[str, dict[str, Any]] = {}
    for r in rows:
        if r["cell_id"] == "screen":
            continue
        key = (str(r["relation_id"]), str(r["cell_id"]), str(r["wrapper"]), str(r["fact_id"]))
        margins[key] = float(r["context_minus_parametric_logprob_margin"])
        contextual[key] = r["observed_knowledge_source"] == "contextual"
        info.setdefault(str(r["wrapper"]), {k: r.get(k) for k in CARRY})

    per_wrapper: list[dict[str, Any]] = []
    distribution: list[dict[str, Any]] = []
    per_string: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    covariate: list[dict[str, Any]] = []
    for relation in relations:
        for cell in cells:
            facts = sorted({k[3] for k in margins
                            if k[0] == relation and k[1] == cell and k[2] == "inline"})
            if not facts:
                continue
            here = {k[2] for k in margins if k[0] == relation and k[1] == cell}
            order = sorted(
                here,
                key=lambda w: (
                    {"baseline": 0, "reference": 1, "random": 2}.get(
                        str(info[w].get("wrapper_source")), 3),
                    info[w].get("name_index") if info[w].get("name_index") is not None else -1,
                    str(info[w].get("form")), w,
                ),
            )
            delta: dict[str, np.ndarray] = {}
            rate: dict[str, float] = {}
            for wrapper in order:
                present = [f for f in facts if (relation, cell, wrapper, f) in margins]
                if not present:
                    continue
                values = np.asarray([margins[(relation, cell, wrapper, f)] for f in present])
                inline = np.asarray([margins[(relation, cell, "inline", f)] for f in present])
                deltas = values - inline
                low, high = bootstrap_mean_ci(deltas, replicates, seed)
                positive, negative, _ = sign_counts(deltas)
                rate[wrapper] = float(np.mean([contextual[(relation, cell, wrapper, f)]
                                               for f in present]))
                if len(present) == len(facts):
                    delta[wrapper] = deltas
                per_wrapper.append({
                    "relation": relation, "cell": cell, "wrapper": wrapper,
                    **{k: info[wrapper].get(k) for k in CARRY},
                    "n": len(present), "context_rate": rate[wrapper],
                    "mean_margin": float(values.mean()),
                    "delta_vs_inline": float(deltas.mean()),
                    "delta_ci_low": low, "delta_ci_high": high,
                    "n_positive": positive, "n_negative": negative,
                    "complete": len(present) == len(facts),
                })

            # Random strings that ran completely in both forms.
            pairs: dict[str, dict[str, str]] = {}
            for wrapper in order:
                if info[wrapper].get("wrapper_source") != "random" or wrapper not in delta:
                    continue
                pairs.setdefault(str(info[wrapper]["name"]), {})[str(info[wrapper]["form"])] = wrapper
            names = [n for n, forms in pairs.items() if all(f in forms for f in FORMS)]
            if not names:
                continue
            matrices = {
                form: np.vstack([delta[pairs[n][form]] for n in names]) for form in FORMS
            }
            string_mean = {form: matrices[form].mean(axis=1) for form in FORMS}
            for form in FORMS:
                values = string_mean[form]
                rates = np.asarray([rate[pairs[n][form]] for n in names])
                low, high = crossed_bootstrap_mean_ci(matrices[form], replicates, seed)
                above = 0
                for row in matrices[form]:
                    row_low, _ = bootstrap_mean_ci(row, replicates, seed)
                    above += int(row_low > 0)
                distribution.append({
                    "relation": relation, "cell": cell, "form": form,
                    "n_strings": len(names), "n_facts": len(facts),
                    "mean_delta": float(values.mean()),
                    "crossed_ci_low": low, "crossed_ci_high": high,
                    "median_delta": float(np.median(values)),
                    "q25_delta": float(np.quantile(values, 0.25)),
                    "q75_delta": float(np.quantile(values, 0.75)),
                    "min_delta": float(values.min()), "max_delta": float(values.max()),
                    "n_strings_delta_positive": int(np.sum(values > 0)),
                    "n_strings_ci_above_zero": above,
                    "mean_rate": float(rates.mean()),
                    "median_rate": float(np.median(rates)),
                    "n_strings_rate_above_half": int(np.sum(rates > 0.5)),
                })
            gap_matrix = matrices["tag"] - matrices["label"]
            gaps = gap_matrix.mean(axis=1)
            low, high = crossed_bootstrap_mean_ci(gap_matrix, replicates, seed)
            positive, negative, _ = sign_counts(gaps)
            distribution.append({
                "relation": relation, "cell": cell, "form": "tag_minus_label",
                "n_strings": len(names), "n_facts": len(facts),
                "mean_delta": float(gaps.mean()),
                "crossed_ci_low": low, "crossed_ci_high": high,
                "median_delta": float(np.median(gaps)),
                "q25_delta": float(np.quantile(gaps, 0.25)),
                "q75_delta": float(np.quantile(gaps, 0.75)),
                "min_delta": float(gaps.min()), "max_delta": float(gaps.max()),
                "n_strings_delta_positive": positive,
                "n_strings_ci_above_zero": None,
                "mean_rate": None, "median_rate": None, "n_strings_rate_above_half": None,
                "wilcoxon_p_across_strings": wilcoxon_p(gaps),
                "sign_test_p_across_strings": sign_test_p(positive, negative),
            })
            for index, name in enumerate(names):
                tag, label = pairs[name]["tag"], pairs[name]["label"]
                per_string.append({
                    "relation": relation, "cell": cell, "name": name,
                    "name_index": info[tag].get("name_index"),
                    "tag_delta": float(string_mean["tag"][index]),
                    "label_delta": float(string_mean["label"][index]),
                    "gap": float(gaps[index]),
                    "tag_rate": rate[tag], "label_rate": rate[label],
                    "tag_tokens": info[tag].get("marker_num_tokens"),
                    "label_tokens": info[label].get("marker_num_tokens"),
                })
            # Where the original strings fall among the random ones.
            for wrapper in order:
                if info[wrapper].get("wrapper_source") != "reference" or wrapper not in delta:
                    continue
                form = str(info[wrapper].get("form"))
                if form not in FORMS:
                    continue
                value = float(delta[wrapper].mean())
                references.append({
                    "relation": relation, "cell": cell, "wrapper": wrapper,
                    "name": info[wrapper].get("name"), "form": form,
                    "delta_vs_inline": value, "context_rate": rate[wrapper],
                    "percentile_among_random": float(np.mean(string_mean[form] <= value)),
                })
            # Exploratory: does the effect track how many tokens the marker takes?
            for form in FORMS:
                tokens = [info[pairs[n][form]].get("marker_num_tokens") for n in names]
                if any(t is None for t in tokens) or len(set(tokens)) < 2:
                    continue
                result = spearman_permutation(tokens, string_mean[form], permutations, seed)
                covariate.append({
                    "relation": relation, "cell": cell, "form": form,
                    "n_strings": result["n"], "spearman_rho": result["rho"],
                    "permutation_p": result["p"],
                    "min_tokens": int(min(tokens)), "max_tokens": int(max(tokens)),
                })
    return {
        "per_wrapper": per_wrapper,
        "distribution": distribution,
        "per_string": per_string,
        "references": references,
        "token_covariate": covariate,
    }


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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    from paired_stats import format_p

    started = time.time()
    args = parse_args()
    if args.make_names:
        names = write_names(
            args.names_file, args.n_names, args.name_length, args.names_seed,
            args.overwrite_names,
        )
        print(f"wrote {len(names)} names to {args.names_file}:")
        for name in names:
            print(f"  <{name}>   {name.capitalize()}:")
        return
    if args.out is None:
        raise ValueError("--out is required unless --make-names is given")
    args.out.mkdir(parents=True, exist_ok=True)
    results_path = args.out / "nonsense_results.jsonl"
    partial_path = args.out / "nonsense_results.jsonl.partial"
    report_path = args.out / "nonsense_report.md"
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
    cells = [c.strip() for c in args.cells.split(",") if c.strip()]
    for cell in cells:
        if cell not in CELLS:
            raise ValueError(f"Unknown cell {cell!r}; expected one of {CELLS}")
    references = [w.strip() for w in args.references.split(",") if w.strip()]
    names = read_names(args.names_file)
    if args.max_names is not None:
        names = names[: args.max_names]
    templates, meta = wrapper_table(names, references)

    facts = build_facts(
        relations, None, args.max_facts,
        mode=args.false_answer_mode, seed=args.false_answer_seed,
    )
    print(f"model: {config['model']['id']}")
    print(f"facts before screening: {len(facts)}   mode {args.false_answer_mode}")
    print(f"wrappers: {len(templates)} = inline + {len(references)} references + "
          f"{len(names)} random names x 2 forms")

    if args.validate_only:
        example = facts[0]
        relation = str(example["relation_id"])
        subject, answer = str(example["query_subject"]), str(example["claim_answer"])
        shown = ["inline", *references, f"rtag_{names[0]}", f"rlabel_{names[0]}"]
        for wrapper in shown:
            print(f"\n{'=' * 78}\n{wrapper}  ({meta[wrapper]['wrapper_source']}, "
                  f"{meta[wrapper]['form']})\n{'=' * 78}")
            print(build_prompt(
                relation, wrapper, claim_sentence(relation, cells[0], subject, answer),
                subject, templates,
            ))
        print(f"\nnames ({len(names)}): {', '.join(names)}")
        print(
            f"\nvalidate-only: {len(facts)} screening + "
            f"{len(build_records(facts, templates, meta, cells))} experimental prompts"
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
        fingerprint = runtime_fingerprint(config, bundle, {"names_file": args.names_file})
        for wrapper in meta:
            meta[wrapper]["marker_num_tokens"] = count_tokens(
                bundle.tokenizer, str(meta[wrapper]["marker_text"])
            )
        generation_batch = args.generation_batch_size or int(
            config["collection"]["generation_batch_size"]
        )
        scoring_batch = args.scoring_batch_size or int(
            config["collection"]["scoring_batch_size"]
        )

        if not args.skip_screening:
            print("\nscreening (context-free)")
            screen = [
                r for r in screening_records(facts, prefix=PREFIX)
                if r["sample_id"] not in done
            ]
            evaluate(screen, bundle, config, partial_path, generation_batch,
                     scoring_batch, started, analysis_version=ANALYSIS_VERSION)
            kept = screened_facts(facts, read_jsonl(partial_path), prefix=PREFIX)
            print(f"  kept {len(kept)}/{len(facts)} facts")
            facts = list(kept)
            if not facts:
                raise RuntimeError("No facts survived screening")

        experiment = [
            r for r in build_records(facts, templates, meta, cells)
            if r["sample_id"] not in done
        ]
        print(f"\nscoring {len(experiment)} experimental prompts")
        evaluate(experiment, bundle, config, partial_path, generation_batch,
                 scoring_batch, started, carry=CARRY, analysis_version=ANALYSIS_VERSION)
        rows = read_jsonl(partial_path)
        finalize_jsonl(partial_path, results_path)
        print(f"\nscored {len(rows)} prompts total")

    # ---- analysis ----------------------------------------------------------
    seed = int(config["project"]["seed"])
    result = analyse(rows, relations, cells, args.bootstrap_replicates,
                     args.permutations, seed)

    print("\n" + "=" * 78)
    print("distribution over random names (ΔM vs inline, paired within fact)")
    print("=" * 78)
    for entry in result["distribution"]:
        print(
            f"  {entry['relation']:16s} {entry['cell']:10s} {entry['form']:16s} "
            f"mean {entry['mean_delta']:+7.2f} [{entry['crossed_ci_low']:+.2f}, "
            f"{entry['crossed_ci_high']:+.2f}]  median {entry['median_delta']:+7.2f}  "
            f"range [{entry['min_delta']:+.1f}, {entry['max_delta']:+.1f}]  "
            f"{entry['n_strings_delta_positive']}/{entry['n_strings']} strings > 0"
            + (f"  Wilcoxon p={format_p(entry['wilcoxon_p_across_strings'])}"
               if entry["form"] == "tag_minus_label" else "")
        )
    for entry in result["references"]:
        print(
            f"  {entry['relation']:16s} {entry['cell']:10s} {entry['wrapper']:16s} "
            f"ΔM {entry['delta_vs_inline']:+7.2f}  rate {100 * entry['context_rate']:5.1f}%  "
            f"percentile among random {entry['form']}s: "
            f"{100 * entry['percentile_among_random']:.0f}"
        )

    write_json_atomic(
        args.out / "nonsense_summary.json",
        json_safe({
            "analysis_version": ANALYSIS_VERSION,
            "runtime": fingerprint,
            "model": config["model"]["id"],
            "names": names,
            "references": references,
            "templates": templates,
            **result,
        }),
    )
    write_csv(args.out / "nonsense_cells.csv", result["per_wrapper"])
    write_csv(args.out / "nonsense_strings.csv", result["per_string"])

    lines = [f"# E13: thirty meaningless names — {config['model']['id']}\n"]
    lines.append(
        f"{len(names)} random lower-case names of {len(names[0])} letters, each as "
        "`<name>` and `Name:` around the identical paragraph. ΔM is paired within "
        "fact against `inline`. Across strings, CIs are a crossed bootstrap over "
        "strings and facts; the tag − label gap is also tested across strings "
        "(Wilcoxon signed-rank, one pair per string).\n"
    )
    lines.append("## Distribution over strings\n")
    lines.append("| Relation | Cell | Form | Mean ΔM | 95% CI (crossed) | Median | Range "
                 "| Strings > 0 | Strings, CI > 0 | Median rate | Strings > 50% | p (across strings) |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for entry in result["distribution"]:
        tested = entry["form"] == "tag_minus_label"
        lines.append(
            f"| {entry['relation']} | `{entry['cell']}` | {entry['form']} | "
            f"{entry['mean_delta']:+.2f} | [{entry['crossed_ci_low']:+.2f}, "
            f"{entry['crossed_ci_high']:+.2f}] | {entry['median_delta']:+.2f} | "
            f"[{entry['min_delta']:+.1f}, {entry['max_delta']:+.1f}] | "
            f"{entry['n_strings_delta_positive']}/{entry['n_strings']} | "
            + ("– | – | – | " if tested else
               f"{entry['n_strings_ci_above_zero']}/{entry['n_strings']} | "
               f"{100 * entry['median_rate']:.1f}% | "
               f"{entry['n_strings_rate_above_half']}/{entry['n_strings']} | ")
            + (f"{format_p(entry['wilcoxon_p_across_strings'])} |" if tested else "– |")
        )
    if result["references"]:
        lines.append("\n## The original strings, placed in the distribution\n")
        lines.append("| Relation | Cell | Wrapper | ΔM | Rate | Percentile among random |")
        lines.append("|---|---|---|---:|---:|---:|")
        for entry in result["references"]:
            lines.append(
                f"| {entry['relation']} | `{entry['cell']}` | `{entry['wrapper']}` | "
                f"{entry['delta_vs_inline']:+.2f} | {100 * entry['context_rate']:.1f}% | "
                f"{100 * entry['percentile_among_random']:.0f} |"
            )
    if result["token_covariate"]:
        lines.append("\n## Exploratory: ΔM against the marker's token count\n")
        lines.append("| Relation | Cell | Form | Strings | Tokens | Spearman ρ | Permutation p |")
        lines.append("|---|---|---|---:|---:|---:|---:|")
        for entry in result["token_covariate"]:
            lines.append(
                f"| {entry['relation']} | `{entry['cell']}` | {entry['form']} | "
                f"{entry['n_strings']} | {entry['min_tokens']}–{entry['max_tokens']} | "
                f"{entry['spearman_rho']:+.2f} | {format_p(entry['permutation_p'])} |"
            )
    lines.append("\n## Per string\n")
    lines.append("| Relation | Cell | Name | Tag ΔM | Label ΔM | Gap | Tag rate | Label rate |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|")
    for entry in result["per_string"]:
        lines.append(
            f"| {entry['relation']} | `{entry['cell']}` | `{entry['name']}` | "
            f"{entry['tag_delta']:+.2f} | {entry['label_delta']:+.2f} | {entry['gap']:+.2f} | "
            f"{100 * entry['tag_rate']:.1f}% | {100 * entry['label_rate']:.1f}% |"
        )
    lines.append("\n## How to read this\n")
    lines.append(
        "- **The tag row is the claim.** If most strings lift the margin as a tag, "
        "\"a meaningless tag works\" is a property of the bracket syntax around an "
        "unfamiliar name, not of `qzx_block`.\n"
        "- **The gap row is the interaction.** Each string is its own tag/label "
        "pair, so a positive gap in most strings means the brackets, not the "
        "name, carry the effect for meaningless names. Compare with E12's "
        "factorial, where meaningful names barely care about brackets.\n"
        "- **The references** place `<qzx_block>` and `<qzxzxew>` in the "
        "distribution, and should reproduce E12 within run-to-run noise.\n"
        "- **The token-count table** is exploratory: random letters split into "
        "several subword tokens, a word like `document` into one.\n"
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {report_path}")
    print(f"elapsed {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
