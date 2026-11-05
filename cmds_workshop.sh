#!/usr/bin/env bash
#
# Workshop-paper additions, in order. Run from the repository root.
#
#   1  statistics        make_tables.py: CIs, exact McNemar, Wilcoxon, sign counts,
#                        Holm, permutation p for the cross-model Spearman
#   2  30 random names   E13_nonsense_strings.py, each name as <x> and X:
#   3  guard wordings    E11 v2: falsehood / instruction / combined x 3 slots
#   4  irrelevant para.  E12 v2: irrelevant_assert_r1, same false answer, other subject
#   5  full factorial    E12 v2: + <search_result>, Passage:, Trusted content:,
#                        Unreliable source:
#
# E11 and E12 are re-run in full, so every number in the paper comes from one
# run per model; their new outputs go to channel_v2/ and delimiter_v2/ and the
# original runs stay where they are for the reproducibility checks in step 6.
# Nothing here regenerates the dataset or reruns 01/02/E6/E7/E8/E10: E8's and
# E7's committed results are reused as they are.
#
# Before you start: same environment as cmds.sh (transformers==5.15.0), and
# paths.hf_cache_dir set in config.yaml and config_qwen36.yaml.
#
# Every long run resumes: if one dies, run the same command again (WITHOUT
# --overwrite, which would discard the partial file).
#
# GPU time below is scaled from the original runs on an A100 40GB.

set -euo pipefail

G=results/gemma4_12b_conflict
Q=results/qwen36_27b_conflict
export R=results   # read by the checkpoint snippets below


# ===========================================================================
# 0. PREFLIGHT                                              (~1 min, no GPU)
# ===========================================================================
# random_tag_names.json is committed. Do NOT regenerate it: both models must
# read the same thirty names. (It was made with
#   python E13_nonsense_strings.py --make-names )

for CFG in config.yaml config_qwen36.yaml; do
  python E11_source_channel.py   --config $CFG --out /tmp/e11_check --validate-only | tail -1
  python E12_delimiter.py        --config $CFG --out /tmp/e12_check --validate-only | tail -1
  python E13_nonsense_strings.py --config $CFG --out /tmp/e13_check --validate-only | tail -1
done
rm -rf /tmp/e11_check /tmp/e12_check /tmp/e13_check

# Expect, for each config:
#   validate-only: 271 screening + 6504 experimental prompts    (E11: 12 channels x 2 cells)
#   validate-only: 271 screening + 17073 experimental prompts   (E12: 21 wrappers x 3 cells)
#   validate-only: 271 screening + 17615 experimental prompts   (E13: 65 wrappers x 1 cell)


# ===========================================================================
# 1. SMOKE TEST ON THE GPU                                  (~10 min, Gemma)
# ===========================================================================
# Two facts per relation through every script, end to end, before committing
# hours. Throwaway output.

S=results/_smoke
python E11_source_channel.py   --config config.yaml --out $S/channel   --max-facts 2
python E12_delimiter.py        --config config.yaml --out $S/delimiter --max-facts 2
python E13_nonsense_strings.py --config config.yaml --out $S/nonsense  --max-facts 2 --max-names 2
rm -rf $S

# Expect each to finish with "wrote .../*_report.md". Screening keeps <= 4 facts.


# ===========================================================================
# 2. E11 v2 -- three guard wordings in three slots    (~75 min Gemma, ~60 Qwen)
# ===========================================================================

python E11_source_channel.py --config config.yaml        --out $G/analysis/channel_v2
python E11_source_channel.py --config config_qwen36.yaml --out $Q/analysis/channel_v2

# Expect 12 channels x 2 cells per fact. The three *_falsehood channels are
# the original guard, byte for byte, and should reproduce channel/ (step 6).


# ===========================================================================
# 3. E12 v2 -- 21 wrappers x {assert_r1, bare, irrelevant}   (~2.5 h per model)
# ===========================================================================

python E12_delimiter.py --config config.yaml        --out $G/analysis/delimiter_v2
python E12_delimiter.py --config config_qwen36.yaml --out $Q/analysis/delimiter_v2

# To save ~50 min per model you could drop the bare cell
# (--cells assert_r1,irrelevant_assert_r1), but the bare-sentence Spearman and
# tag/label rows then disappear from the tables. The full run is recommended.


# ===========================================================================
# 4. E13 -- thirty random names as <name> and Name:          (~2.5 h per model)
# ===========================================================================

python E13_nonsense_strings.py --config config.yaml        --out $G/analysis/nonsense_strings
python E13_nonsense_strings.py --config config_qwen36.yaml --out $Q/analysis/nonsense_strings

# Only assert_r1 by default. Adding --cells assert_r1,bare doubles the cost.


# ===========================================================================
# 5. CHECKPOINTS                                            (~1 min, no GPU)
# ===========================================================================

# 5a. Same prompts. Every condition that also ran in the original E11/E12 must
#     have been rebuilt byte-for-byte (E12 compares the user message; E11 the
#     templated prompt, which also checks the chat template has not changed).
python - <<'PY'
import json, os
R = os.environ.get("R", "results")
# Keyed on (fact, cell, condition), not sample_id: the original E11 ids carry
# a "-neutral" suffix from an older version of the script.
def rows(path, condition):
    with open(path) as f:
        return {(r["fact_id"], r["cell_id"], r[condition]): r for r in map(json.loads, f)
                if r["cell_id"] != "screen" and r.get("policy_id", "neutral") == "neutral"}
for model in ("gemma4_12b_conflict", "qwen36_27b_conflict"):
    base = f"{R}/{model}/analysis"
    for name, condition, field in (("delimiter", "wrapper", "raw_prompt"),
                                   ("channel", "channel", "rendered_prompt")):
        a = rows(f"{base}/{name}/{name}_results.jsonl", condition)
        b = rows(f"{base}/{name}_v2/{name}_results.jsonl", condition)
        shared = sorted(set(a) & set(b))
        same = sum(a[k][field] == b[k][field] for k in shared)
        print(f"{model:22s} {name + '_v2':13s} {same}/{len(shared)} shared prompts identical")
PY
# Expect "N/N shared prompts identical" on all four lines.

# gemma4_12b_conflict    delimiter_v2  8874/8874 shared prompts identical
# gemma4_12b_conflict    channel_v2    3132/3132 shared prompts identical
# qwen36_27b_conflict    delimiter_v2  8976/8976 shared prompts identical
# qwen36_27b_conflict    channel_v2    3168/3168 shared prompts identical

# 5b. Same numbers, within run-to-run noise. Shared conditions, v1 vs v2, and
#     the unwrapped baseline across E8 / E11 / E12 / E13.
python - <<'PY'
import collections, json, os, statistics
R = os.environ.get("R", "results")
def means(path, fields, keep=lambda r: True):
    groups = collections.defaultdict(list)
    with open(path) as f:
        for r in map(json.loads, f):
            if r["cell_id"] != "screen" and r.get("policy_id", "neutral") == "neutral" and keep(r):
                groups[tuple(r[k] for k in fields)].append(r["context_minus_parametric_logprob_margin"])
    return {k: statistics.mean(v) for k, v in groups.items()}
for model in ("gemma4_12b_conflict", "qwen36_27b_conflict"):
    base = f"{R}/{model}/analysis"
    for old, new, name, key in (("delimiter", "delimiter_v2", "delimiter", "wrapper"),
                                ("channel", "channel_v2", "channel", "channel")):
        a = means(f"{base}/{old}/{name}_results.jsonl", ("relation_id", "cell_id", key))
        b = means(f"{base}/{new}/{name}_results.jsonl", ("relation_id", "cell_id", key))
        gaps = sorted((abs(a[k] - b[k]), k) for k in set(a) & set(b))
        print(f"{model:22s} {old:9s} v1 vs v2: {len(gaps)} shared cells, mean |d| "
              f"{statistics.mean(g for g, _ in gaps):.2f}, max |d| {gaps[-1][0]:.2f} at {gaps[-1][1]}")
    e12 = means(f"{base}/delimiter_v2/delimiter_results.jsonl", ("relation_id", "cell_id", "wrapper"))
    e13 = means(f"{base}/nonsense_strings/nonsense_results.jsonl", ("relation_id", "cell_id", "wrapper"))
    for k in sorted(set(e12) & set(e13)):
        print(f"{model:22s} E12 v2 vs E13  {'/'.join(k):45s} {e12[k]:7.2f} vs {e13[k]:7.2f}")
    inline = {
        "E8 ": means(f"{base}/conventionality_random/conventionality_results.jsonl",
                     ("relation_id", "cell_id")).get(("element_symbol", "assert_r1")),
        "E11": means(f"{base}/channel_v2/channel_results.jsonl",
                     ("relation_id", "cell_id", "channel")).get(("element_symbol", "assert_r1", "inline")),
        "E12": e12.get(("element_symbol", "assert_r1", "inline")),
        "E13": e13.get(("element_symbol", "assert_r1", "inline")),
    }
    print(f"{model:22s} unwrapped element baseline: "
          + "  ".join(f"{k} {v:.2f}" for k, v in inline.items() if v is not None))
PY
# Expect mean |d| well under a logit and every cell within ~1 logit; the
# original three runs agreed on the baseline to 0.10 logits. A larger gap
# means something other than batching changed -- find it before writing it up.

# gemma4_12b_conflict    delimiter v1 vs v2: 68 shared cells, mean |d| 0.03, max |d| 0.48 at ('element_symbol', 'bare', 'label_untrusted')
# gemma4_12b_conflict    channel   v1 vs v2: 24 shared cells, mean |d| 0.10, max |d| 0.50 at ('element_symbol', 'explicit_stipulation', 'user_guard_falsehood_above')
# gemma4_12b_conflict    E12 v2 vs E13  country_capital/assert_r1/inline               -28.10 vs  -28.12
# gemma4_12b_conflict    E12 v2 vs E13  country_capital/assert_r1/label_gibberish      -24.02 vs  -24.05
# gemma4_12b_conflict    E12 v2 vs E13  country_capital/assert_r1/label_nonsense       -20.30 vs  -20.36
# gemma4_12b_conflict    E12 v2 vs E13  country_capital/assert_r1/tag_gibberish         -4.44 vs   -4.44
# gemma4_12b_conflict    E12 v2 vs E13  country_capital/assert_r1/tag_nonsense           2.88 vs    2.88
# gemma4_12b_conflict    E12 v2 vs E13  element_symbol/assert_r1/inline                -27.13 vs  -27.04
# gemma4_12b_conflict    E12 v2 vs E13  element_symbol/assert_r1/label_gibberish       -19.09 vs  -19.08
# gemma4_12b_conflict    E12 v2 vs E13  element_symbol/assert_r1/label_nonsense         -6.04 vs   -6.03
# gemma4_12b_conflict    E12 v2 vs E13  element_symbol/assert_r1/tag_gibberish          -2.96 vs   -2.96
# gemma4_12b_conflict    E12 v2 vs E13  element_symbol/assert_r1/tag_nonsense            4.11 vs    4.10
# gemma4_12b_conflict    unwrapped element baseline: E8  -27.11  E11 -27.03  E12 -27.13  E13 -27.04
# qwen36_27b_conflict    delimiter v1 vs v2: 68 shared cells, mean |d| 0.01, max |d| 0.06 at ('element_symbol', 'assert_r1', 'inline')
# qwen36_27b_conflict    channel   v1 vs v2: 24 shared cells, mean |d| 0.02, max |d| 0.08 at ('element_symbol', 'explicit_stipulation', 'system_guard_falsehood')
# qwen36_27b_conflict    E12 v2 vs E13  country_capital/assert_r1/inline               -11.08 vs  -11.07
# qwen36_27b_conflict    E12 v2 vs E13  country_capital/assert_r1/label_gibberish       -7.91 vs   -7.88
# qwen36_27b_conflict    E12 v2 vs E13  country_capital/assert_r1/label_nonsense        -7.71 vs   -7.71
# qwen36_27b_conflict    E12 v2 vs E13  country_capital/assert_r1/tag_gibberish         -7.49 vs   -7.49
# qwen36_27b_conflict    E12 v2 vs E13  country_capital/assert_r1/tag_nonsense          -7.10 vs   -7.10
# qwen36_27b_conflict    E12 v2 vs E13  element_symbol/assert_r1/inline                 -7.24 vs   -7.22
# qwen36_27b_conflict    E12 v2 vs E13  element_symbol/assert_r1/label_gibberish        -4.16 vs   -4.15
# qwen36_27b_conflict    E12 v2 vs E13  element_symbol/assert_r1/label_nonsense         -4.23 vs   -4.24
# qwen36_27b_conflict    E12 v2 vs E13  element_symbol/assert_r1/tag_gibberish          -3.73 vs   -3.73
# qwen36_27b_conflict    E12 v2 vs E13  element_symbol/assert_r1/tag_nonsense           -2.50 vs   -2.49
# qwen36_27b_conflict    unwrapped element baseline: E8  -7.24  E11 -7.23  E12 -7.24  E13 -7.22



# 5c. Facts kept after screening, per run (originally Gemma 118 + 143,
#     Qwen 118 + 146; a fact sitting on the threshold may flip).
python - <<'PY'
import collections, json, os
R = os.environ.get("R", "results")
for model in ("gemma4_12b_conflict", "qwen36_27b_conflict"):
    for run in ("channel_v2/channel", "delimiter_v2/delimiter", "nonsense_strings/nonsense"):
        with open(f"{R}/{model}/analysis/{run}_results.jsonl") as f:
            facts = {(r["relation_id"], r["fact_id"]) for r in map(json.loads, f) if r["cell_id"] != "screen"}
        print(f"{model:22s} {run.split('/')[0]:17s} {dict(collections.Counter(r for r, _ in facts))}")
PY

# gemma4_12b_conflict    channel_v2        {'element_symbol': 118, 'country_capital': 143}
# gemma4_12b_conflict    delimiter_v2      {'element_symbol': 118, 'country_capital': 143}
# gemma4_12b_conflict    nonsense_strings  {'element_symbol': 118, 'country_capital': 143}
# qwen36_27b_conflict    channel_v2        {'element_symbol': 118, 'country_capital': 146}
# qwen36_27b_conflict    delimiter_v2      {'element_symbol': 118, 'country_capital': 146}
# qwen36_27b_conflict    nonsense_strings  {'element_symbol': 118, 'country_capital': 146}

# ===========================================================================
# 6. TABLES AND FIGURES                                     (~1 min, no GPU)
# ===========================================================================

python make_tables.py  --results results --out results/stats
python make_figures.py --results results --out figures

# make_tables writes results/stats/stats_report.md (every table, in paper
# order, Holm-adjusted p within each family) plus the CSVs and JSON behind it.
# make_figures overwrites figures/fig1-3 with the v2 runs and adds
# fig4_nonsense.png and fig5_relevance.png. To redraw the original write-up's
# figures instead:
#   python make_figures.py --delimiter-dir delimiter --channel-dir channel --out figures_v1

echo
echo "Done. Start from results/stats/stats_report.md."
