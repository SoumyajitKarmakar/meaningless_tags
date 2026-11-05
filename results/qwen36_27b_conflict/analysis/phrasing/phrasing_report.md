# E7: which property of the claim sentence drives deference?

5691 prompts, 271 facts, neutral policy. Subject, false answer, filler, question and response constraint are held fixed at each relation's E6 low-endpoint frame; only the claim sentence varies.

## Main effects (margin, logits)

| Relation | Factor | Contrast | Delta | 95% CI | n |
|---|---|---|---:|---:|---:|
| element_symbol | act | stipulate - assert | -0.39 | [-0.70, -0.09] | 118 |
| element_symbol | realization | r1 - r2 | 1.09 | [+0.95, +1.23] | 118 |
| element_symbol | source | high - low | 4.37 | [+4.10, +4.66] | 118 |
| element_symbol | persistence | present - absent | 1.40 | [+1.25, +1.55] | 118 |
| country_capital | act | stipulate - assert | -3.95 | [-4.35, -3.51] | 153 |
| country_capital | realization | r1 - r2 | 0.62 | [+0.49, +0.73] | 153 |
| country_capital | source | high - low | 1.60 | [+1.45, +1.75] | 153 |
| country_capital | persistence | present - absent | 0.25 | [+0.14, +0.36] | 153 |

## Behaviour per cell

| Relation | Cell | n | Context | Parametric | Other | Mean margin |
|---|---|---:|---:|---:|---:|---:|
| element_symbol | `assert_r1_high_absent` | 118 | 0.0% | 100.0% | 0.0% | -7.07 |
| element_symbol | `assert_r1_high_present` | 118 | 0.0% | 100.0% | 0.0% | -5.21 |
| element_symbol | `assert_r1_low_absent` | 118 | 0.0% | 100.0% | 0.0% | -11.37 |
| element_symbol | `assert_r1_low_present` | 118 | 0.0% | 100.0% | 0.0% | -10.65 |
| element_symbol | `assert_r2_high_absent` | 118 | 0.0% | 100.0% | 0.0% | -8.74 |
| element_symbol | `assert_r2_high_present` | 118 | 0.0% | 100.0% | 0.0% | -6.89 |
| element_symbol | `assert_r2_low_absent` | 118 | 0.0% | 100.0% | 0.0% | -12.56 |
| element_symbol | `assert_r2_low_present` | 118 | 0.0% | 100.0% | 0.0% | -13.04 |
| element_symbol | `bare` | 118 | 31.4% | 68.6% | 0.0% | -0.47 |
| element_symbol | `irrelevant_assert` | 118 | 0.0% | 100.0% | 0.0% | -10.13 |
| element_symbol | `irrelevant_stipulate` | 118 | 0.0% | 100.0% | 0.0% | -11.57 |
| element_symbol | `orig_high` | 118 | 0.0% | 100.0% | 0.0% | -7.27 |
| element_symbol | `orig_low` | 118 | 0.0% | 100.0% | 0.0% | -13.23 |
| element_symbol | `stipulate_r1_high_absent` | 118 | 0.0% | 100.0% | 0.0% | -7.99 |
| element_symbol | `stipulate_r1_high_present` | 118 | 1.7% | 98.3% | 0.0% | -7.01 |
| element_symbol | `stipulate_r1_low_absent` | 118 | 0.0% | 100.0% | 0.0% | -12.45 |
| element_symbol | `stipulate_r1_low_present` | 118 | 0.0% | 100.0% | 0.0% | -11.00 |
| element_symbol | `stipulate_r2_high_absent` | 118 | 0.8% | 99.2% | 0.0% | -9.46 |
| element_symbol | `stipulate_r2_high_present` | 118 | 1.7% | 98.3% | 0.0% | -7.24 |
| element_symbol | `stipulate_r2_low_absent` | 118 | 0.0% | 100.0% | 0.0% | -13.09 |
| element_symbol | `stipulate_r2_low_present` | 118 | 0.0% | 100.0% | 0.0% | -10.43 |
| country_capital | `assert_r1_high_absent` | 153 | 0.0% | 100.0% | 0.0% | -11.37 |
| country_capital | `assert_r1_high_present` | 153 | 0.0% | 99.3% | 0.7% | -11.00 |
| country_capital | `assert_r1_low_absent` | 153 | 0.0% | 100.0% | 0.0% | -13.99 |
| country_capital | `assert_r1_low_present` | 153 | 0.0% | 99.3% | 0.7% | -13.49 |
| country_capital | `assert_r2_high_absent` | 153 | 0.0% | 99.3% | 0.7% | -12.30 |
| country_capital | `assert_r2_high_present` | 153 | 0.0% | 99.3% | 0.7% | -12.47 |
| country_capital | `assert_r2_low_absent` | 153 | 0.0% | 100.0% | 0.0% | -14.60 |
| country_capital | `assert_r2_low_present` | 153 | 0.0% | 100.0% | 0.0% | -14.97 |
| country_capital | `bare` | 153 | 1.3% | 98.0% | 0.7% | -4.42 |
| country_capital | `irrelevant_assert` | 153 | 0.0% | 100.0% | 0.0% | -9.90 |
| country_capital | `irrelevant_stipulate` | 153 | 0.0% | 100.0% | 0.0% | -15.29 |
| country_capital | `orig_high` | 153 | 1.3% | 98.0% | 0.7% | -5.87 |
| country_capital | `orig_low` | 153 | 1.3% | 98.0% | 0.7% | -6.24 |
| country_capital | `stipulate_r1_high_absent` | 153 | 0.7% | 99.3% | 0.0% | -17.02 |
| country_capital | `stipulate_r1_high_present` | 153 | 0.7% | 99.3% | 0.0% | -16.46 |
| country_capital | `stipulate_r1_low_absent` | 153 | 0.7% | 99.3% | 0.0% | -17.06 |
| country_capital | `stipulate_r1_low_present` | 153 | 1.3% | 98.7% | 0.0% | -17.15 |
| country_capital | `stipulate_r2_high_absent` | 153 | 0.7% | 99.3% | 0.0% | -16.86 |
| country_capital | `stipulate_r2_high_present` | 153 | 0.7% | 99.3% | 0.0% | -16.11 |
| country_capital | `stipulate_r2_low_absent` | 153 | 0.0% | 100.0% | 0.0% | -17.78 |
| country_capital | `stipulate_r2_low_present` | 153 | 0.7% | 99.3% | 0.0% | -17.37 |

## How to read this

- **`act` is the hypothesis.** A large positive stipulate-minus-assert effect in BOTH relations, surviving the `realization` control, means the model treats a source that ADOPTS a convention differently from one that ASSERTS a fact. That is a claim about pragmatics, and it is the version of this finding worth writing up.
- **`realization` is the killer control.** If swapping one verb for a synonym of the same act moves the margin as much as changing the act, the result is lexical and the pragmatic reading is wrong. Report this number next to `act`, never on its own.
- **`source` and `persistence`** are the two obvious alternative explanations for E6's endpoint gap. If either rivals `act`, say so.
- **`bare`** shows where an unattributed assertion sits. If it lands near the assert cells, attribution is not what matters; if it is far from both, the whole effect depends on there being a source at all.
- **A2 must be near zero.** A phrasing that lifts the claim answer even when the claim is about another entity is a salience effect, and the conflict-resolution reading would be wrong.
- Anchors are the E6 cells rebuilt here. If they do not reproduce, nothing above is comparable to E6 and the frame has drifted.
