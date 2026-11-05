# E7: which property of the claim sentence drives deference?

5481 prompts, 261 facts, neutral policy. Facts, false answers, screening and distractors are the E8 / E12 pipeline's; the frame (filler, question, constraint) is E8's. Only the claim sentence varies.

## Anchor reproduction (byte-identical prompts)

| Source | Relation | E7 cell | n | mean d | mean abs d | max abs d |
|---|---|---|---:|---:|---:|---:|
| E8 | element_symbol | `bare` | 118 | -0.175 | 0.562 | 5.125 |
| E8 | element_symbol | `stipulate_r1_high_absent` | 118 | +0.106 | 0.679 | 3.812 |
| E8 | element_symbol | `stipulate_r2_high_absent` | 118 | -0.192 | 0.554 | 2.344 |
| E8 | element_symbol | `assert_r1_high_absent` | 118 | +0.043 | 0.389 | 2.703 |
| E8 | element_symbol | `assert_r2_high_absent` | 118 | +0.012 | 0.517 | 5.813 |
| E8 | country_capital | `bare` | 142 | -0.225 | 0.834 | 14.551 |
| E8 | country_capital | `stipulate_r1_high_absent` | 142 | +0.004 | 0.424 | 5.573 |
| E8 | country_capital | `stipulate_r2_high_absent` | 142 | +0.042 | 0.330 | 3.172 |
| E8 | country_capital | `assert_r1_high_absent` | 142 | +0.002 | 0.238 | 1.041 |
| E8 | country_capital | `assert_r2_high_absent` | 142 | -0.029 | 0.298 | 1.289 |
| E12 | element_symbol | `assert_r1_high_absent` | 118 | +0.068 | 0.382 | 5.041 |
| E12 | element_symbol | `bare` | 118 | +0.001 | 0.658 | 7.238 |
| E12 | element_symbol | `irrelevant_assert` | 118 | -0.030 | 0.164 | 0.937 |
| E12 | country_capital | `assert_r1_high_absent` | 143 | -0.025 | 0.250 | 1.353 |
| E12 | country_capital | `bare` | 143 | -0.034 | 0.780 | 13.486 |
| E12 | country_capital | `irrelevant_assert` | 143 | -0.020 | 0.215 | 1.307 |

## Main effects (margin, logits)

| Relation | Factor | Contrast | Delta | 95% CI | n |
|---|---|---|---:|---:|---:|
| element_symbol | act | stipulate - assert | 9.37 | [+8.47, +10.31] | 118 |
| element_symbol | realization | r1 - r2 | 2.09 | [+1.68, +2.54] | 118 |
| element_symbol | source | high - low | 3.21 | [+2.27, +4.07] | 118 |
| element_symbol | persistence | present - absent | -5.76 | [-6.30, -5.22] | 118 |
| country_capital | act | stipulate - assert | 2.14 | [+1.40, +2.99] | 143 |
| country_capital | realization | r1 - r2 | 1.24 | [+1.03, +1.44] | 143 |
| country_capital | source | high - low | 3.80 | [+3.39, +4.23] | 143 |
| country_capital | persistence | present - absent | -2.02 | [-2.27, -1.78] | 143 |

## Behaviour per cell

| Relation | Cell | n | Context | Parametric | Other | M > 0 | Mean margin |
|---|---|---:|---:|---:|---:|---:|---:|
| element_symbol | `assert_r1_high_absent` | 118 | 0.0% | 72.9% | 27.1% | 0.0% | -27.06 |
| element_symbol | `assert_r1_high_present` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -26.74 |
| element_symbol | `assert_r1_low_absent` | 118 | 0.0% | 59.3% | 40.7% | 0.0% | -30.30 |
| element_symbol | `assert_r1_low_present` | 118 | 0.0% | 99.2% | 0.8% | 0.0% | -32.44 |
| element_symbol | `assert_r2_high_absent` | 118 | 0.8% | 58.5% | 40.7% | 0.8% | -25.64 |
| element_symbol | `assert_r2_high_present` | 118 | 0.8% | 99.2% | 0.0% | 0.8% | -28.78 |
| element_symbol | `assert_r2_low_absent` | 118 | 0.0% | 81.4% | 18.6% | 0.0% | -30.79 |
| element_symbol | `assert_r2_low_present` | 118 | 0.0% | 100.0% | 0.0% | 0.0% | -33.39 |
| element_symbol | `bare` | 118 | 5.1% | 83.1% | 11.9% | 7.6% | -15.44 |
| element_symbol | `irrelevant_assert` | 118 | 0.0% | 91.5% | 8.5% | 0.0% | -33.40 |
| element_symbol | `irrelevant_stipulate` | 118 | 0.0% | 82.2% | 17.8% | 0.0% | -33.05 |
| element_symbol | `orig_high` | 118 | 57.6% | 42.4% | 0.0% | 56.8% | -0.80 |
| element_symbol | `orig_low` | 118 | 2.5% | 97.5% | 0.0% | 2.5% | -29.48 |
| element_symbol | `stipulate_r1_high_absent` | 118 | 21.2% | 65.3% | 13.6% | 22.0% | -11.47 |
| element_symbol | `stipulate_r1_high_present` | 118 | 3.4% | 87.3% | 9.3% | 3.4% | -23.72 |
| element_symbol | `stipulate_r1_low_absent` | 118 | 10.2% | 79.7% | 10.2% | 10.2% | -16.33 |
| element_symbol | `stipulate_r1_low_present` | 118 | 2.5% | 97.5% | 0.0% | 2.5% | -21.23 |
| element_symbol | `stipulate_r2_high_absent` | 118 | 3.4% | 92.4% | 4.2% | 3.4% | -17.17 |
| element_symbol | `stipulate_r2_high_present` | 118 | 0.0% | 99.2% | 0.8% | 0.0% | -24.26 |
| element_symbol | `stipulate_r2_low_absent` | 118 | 5.1% | 83.9% | 11.0% | 5.9% | -15.87 |
| element_symbol | `stipulate_r2_low_present` | 118 | 0.0% | 81.4% | 18.6% | 0.0% | -30.14 |
| country_capital | `assert_r1_high_absent` | 143 | 0.0% | 86.7% | 13.3% | 0.0% | -28.12 |
| country_capital | `assert_r1_high_present` | 143 | 0.0% | 100.0% | 0.0% | 0.0% | -30.28 |
| country_capital | `assert_r1_low_absent` | 143 | 0.0% | 81.8% | 18.2% | 0.0% | -32.73 |
| country_capital | `assert_r1_low_present` | 143 | 0.0% | 82.5% | 17.5% | 0.0% | -34.16 |
| country_capital | `assert_r2_high_absent` | 143 | 0.0% | 83.2% | 16.8% | 0.0% | -30.52 |
| country_capital | `assert_r2_high_present` | 143 | 0.0% | 100.0% | 0.0% | 0.0% | -32.06 |
| country_capital | `assert_r2_low_absent` | 143 | 0.0% | 90.9% | 9.1% | 0.0% | -35.11 |
| country_capital | `assert_r2_low_present` | 143 | 0.0% | 95.1% | 4.9% | 0.0% | -35.75 |
| country_capital | `bare` | 143 | 22.4% | 69.9% | 7.7% | 23.1% | -9.63 |
| country_capital | `irrelevant_assert` | 143 | 0.7% | 87.4% | 11.9% | 1.4% | -33.01 |
| country_capital | `irrelevant_stipulate` | 143 | 0.7% | 92.3% | 7.0% | 0.7% | -33.05 |
| country_capital | `orig_high` | 143 | 4.9% | 95.1% | 0.0% | 4.9% | -19.33 |
| country_capital | `orig_low` | 143 | 6.3% | 90.9% | 2.8% | 6.3% | -15.71 |
| country_capital | `stipulate_r1_high_absent` | 143 | 1.4% | 81.8% | 16.8% | 2.1% | -27.53 |
| country_capital | `stipulate_r1_high_present` | 143 | 0.7% | 97.2% | 2.1% | 1.4% | -29.60 |
| country_capital | `stipulate_r1_low_absent` | 143 | 2.8% | 80.4% | 16.8% | 3.5% | -29.38 |
| country_capital | `stipulate_r1_low_present` | 143 | 0.7% | 89.5% | 9.8% | 0.7% | -33.41 |
| country_capital | `stipulate_r2_high_absent` | 143 | 0.0% | 84.6% | 15.4% | 1.4% | -27.55 |
| country_capital | `stipulate_r2_high_present` | 143 | 0.7% | 99.3% | 0.0% | 0.7% | -29.30 |
| country_capital | `stipulate_r2_low_absent` | 143 | 0.0% | 86.0% | 14.0% | 0.7% | -31.15 |
| country_capital | `stipulate_r2_low_present` | 143 | 0.0% | 85.3% | 14.7% | 0.0% | -33.68 |

## How to read this

- **`act` is the hypothesis.** A large positive stipulate-minus-assert effect in BOTH relations, surviving the `realization` control, means the model treats a source that ADOPTS a convention differently from one that ASSERTS a fact. That is a claim about pragmatics, and it is the version of this finding worth writing up.
- **`realization` is the killer control.** If swapping one verb for a synonym of the same act moves the margin as much as changing the act, the result is lexical and the pragmatic reading is wrong. Report this number next to `act`, never on its own.
- **`source` and `persistence`** are the two obvious alternative explanations. If either rivals `act`, say so.
- **`bare`** shows where an unattributed assertion sits. If it lands near the assert cells, attribution is not what matters; if it is far from both, the whole effect depends on there being a source at all.
- **A2 must be near zero.** A phrasing that lifts the false answer even when the claim is about another subject is a salience effect, and the conflict-resolution reading would be wrong.
- **Anchors** are cells whose prompts are byte-identical to E8's and E12's. If their margins do not reproduce within batch noise, nothing here is comparable to those experiments.
- `Other` counts answers that are neither the true nor the paragraph's (including Gemma's thought-channel residue); `M > 0` is the residue-free paragraph rate.
