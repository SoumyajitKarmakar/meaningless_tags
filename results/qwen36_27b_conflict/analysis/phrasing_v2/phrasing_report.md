# E7: which property of the claim sentence drives deference?

5544 prompts, 264 facts, neutral policy. Facts, false answers, screening and distractors are the E8 / E12 pipeline's; the frame (filler, question, constraint) is E8's. Only the claim sentence varies.

## Anchor reproduction (byte-identical prompts)

| Source | Relation | E7 cell | n | mean d | mean abs d | max abs d |
|---|---|---|---:|---:|---:|---:|
| E8 | element_symbol | `bare` | 118 | -0.008 | 0.064 | 0.250 |
| E8 | element_symbol | `stipulate_r1_high_absent` | 118 | +0.011 | 0.152 | 1.241 |
| E8 | element_symbol | `stipulate_r2_high_absent` | 118 | +0.023 | 0.158 | 0.625 |
| E8 | element_symbol | `assert_r1_high_absent` | 118 | +0.032 | 0.121 | 2.312 |
| E8 | element_symbol | `assert_r2_high_absent` | 118 | +0.012 | 0.133 | 0.436 |
| E8 | country_capital | `bare` | 146 | +0.003 | 0.094 | 0.501 |
| E8 | country_capital | `stipulate_r1_high_absent` | 146 | +0.006 | 0.097 | 0.500 |
| E8 | country_capital | `stipulate_r2_high_absent` | 146 | +0.025 | 0.130 | 1.038 |
| E8 | country_capital | `assert_r1_high_absent` | 146 | -0.017 | 0.198 | 1.875 |
| E8 | country_capital | `assert_r2_high_absent` | 146 | -0.025 | 0.164 | 0.875 |
| E12 | element_symbol | `assert_r1_high_absent` | 118 | +0.031 | 0.116 | 1.812 |
| E12 | element_symbol | `bare` | 118 | -0.018 | 0.065 | 0.250 |
| E12 | element_symbol | `irrelevant_assert` | 118 | +0.018 | 0.132 | 0.625 |
| E12 | country_capital | `assert_r1_high_absent` | 146 | -0.004 | 0.209 | 1.875 |
| E12 | country_capital | `bare` | 146 | +0.004 | 0.069 | 0.250 |
| E12 | country_capital | `irrelevant_assert` | 146 | +0.011 | 0.126 | 0.812 |

## Main effects (margin, logits)

| Relation | Factor | Contrast | Delta | 95% CI | n |
|---|---|---|---:|---:|---:|
| element_symbol | act | stipulate - assert | -0.65 | [-0.98, -0.34] | 118 |
| element_symbol | realization | r1 - r2 | 1.11 | [+0.97, +1.24] | 118 |
| element_symbol | source | high - low | 4.59 | [+4.35, +4.84] | 118 |
| element_symbol | persistence | present - absent | 1.46 | [+1.30, +1.61] | 118 |
| country_capital | act | stipulate - assert | -4.25 | [-4.61, -3.88] | 146 |
| country_capital | realization | r1 - r2 | 0.64 | [+0.54, +0.74] | 146 |
| country_capital | source | high - low | 1.55 | [+1.42, +1.69] | 146 |
| country_capital | persistence | present - absent | 0.21 | [+0.12, +0.32] | 146 |

## Behaviour per cell

| Relation | Cell | n | Context | Parametric | Other | M > 0 | Mean margin |
|---|---|---:|---:|---:|---:|---:|---:|
| element_symbol | `assert_r1_high_absent` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -7.21 |
| element_symbol | `assert_r1_high_present` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -5.37 |
| element_symbol | `assert_r1_low_absent` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -11.70 |
| element_symbol | `assert_r1_low_present` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -10.80 |
| element_symbol | `assert_r2_high_absent` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -8.89 |
| element_symbol | `assert_r2_high_present` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -7.03 |
| element_symbol | `assert_r2_low_absent` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -12.92 |
| element_symbol | `assert_r2_low_present` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -13.47 |
| element_symbol | `bare` | 118 | 37.3% | 62.7% | 0.0% | 34.7% | -0.44 |
| element_symbol | `irrelevant_assert` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -10.05 |
| element_symbol | `irrelevant_stipulate` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -11.50 |
| element_symbol | `orig_high` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -7.19 |
| element_symbol | `orig_low` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -13.84 |
| element_symbol | `stipulate_r1_high_absent` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -8.42 |
| element_symbol | `stipulate_r1_high_present` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -7.28 |
| element_symbol | `stipulate_r1_low_absent` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -13.18 |
| element_symbol | `stipulate_r1_low_present` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -11.61 |
| element_symbol | `stipulate_r2_high_absent` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -9.88 |
| element_symbol | `stipulate_r2_high_present` | 118 | 0.8% | 99.2% | 0.0% | 1.7% | -7.56 |
| element_symbol | `stipulate_r2_low_absent` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -13.63 |
| element_symbol | `stipulate_r2_low_present` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -11.07 |
| country_capital | `assert_r1_high_absent` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -11.08 |
| country_capital | `assert_r1_high_present` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -10.59 |
| country_capital | `assert_r1_low_absent` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -13.62 |
| country_capital | `assert_r1_low_present` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -12.99 |
| country_capital | `assert_r2_high_absent` | 146 | 0.0% | 99.3% | 0.7% | 0.0% | -11.85 |
| country_capital | `assert_r2_high_present` | 146 | 0.0% | 98.6% | 1.4% | 0.0% | -12.06 |
| country_capital | `assert_r2_low_absent` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -14.27 |
| country_capital | `assert_r2_low_present` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -14.57 |
| country_capital | `bare` | 146 | 3.4% | 95.9% | 0.7% | 3.4% | -4.27 |
| country_capital | `irrelevant_assert` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -9.57 |
| country_capital | `irrelevant_stipulate` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -15.01 |
| country_capital | `orig_high` | 146 | 2.1% | 96.6% | 1.4% | 2.7% | -5.91 |
| country_capital | `orig_low` | 146 | 1.4% | 97.3% | 1.4% | 2.1% | -6.23 |
| country_capital | `stipulate_r1_high_absent` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -16.91 |
| country_capital | `stipulate_r1_high_present` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -16.46 |
| country_capital | `stipulate_r1_low_absent` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -16.80 |
| country_capital | `stipulate_r1_low_present` | 146 | 0.7% | 99.3% | 0.0% | 0.7% | -17.02 |
| country_capital | `stipulate_r2_high_absent` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -16.73 |
| country_capital | `stipulate_r2_high_present` | 146 | 0.0% | 99.3% | 0.7% | 0.0% | -16.14 |
| country_capital | `stipulate_r2_low_absent` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -17.63 |
| country_capital | `stipulate_r2_low_present` | 146 | 0.0% | 100.0% | 0.0% | 0.0% | -17.32 |

## How to read this

- **`act` is the hypothesis.** A large positive stipulate-minus-assert effect in BOTH relations, surviving the `realization` control, means the model treats a source that ADOPTS a convention differently from one that ASSERTS a fact. That is a claim about pragmatics, and it is the version of this finding worth writing up.
- **`realization` is the killer control.** If swapping one verb for a synonym of the same act moves the margin as much as changing the act, the result is lexical and the pragmatic reading is wrong. Report this number next to `act`, never on its own.
- **`source` and `persistence`** are the two obvious alternative explanations. If either rivals `act`, say so.
- **`bare`** shows where an unattributed assertion sits. If it lands near the assert cells, attribution is not what matters; if it is far from both, the whole effect depends on there being a source at all.
- **A2 must be near zero.** A phrasing that lifts the false answer even when the claim is about another subject is a salience effect, and the conflict-resolution reading would be wrong.
- **Anchors** are cells whose prompts are byte-identical to E8's and E12's. If their margins do not reproduce within batch noise, nothing here is comparable to those experiments.
- `Other` counts answers that are neither the true nor the paragraph's (including Gemma's thought-channel residue); `M > 0` is the residue-free paragraph rate.
