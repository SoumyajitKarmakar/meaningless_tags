# E11: does the channel matter? — Qwen/Qwen3.6-27B

The claim sentence, paragraph, question and user instruction are byte-identical across channels. Only who appears to be speaking changes.


| Relation | Cell | Policy | Channel | Context-following | Mean margin | n |
|---|---|---|---|---:|---:|---:|
| element_symbol | `assert_r1` | neutral | `inline` | 0.0% | -7.24 | 118 |
| element_symbol | `assert_r1` | neutral | `delimited` | 62.7% | 0.56 | 118 |
| element_symbol | `assert_r1` | neutral | `system_guard_falsehood` | 0.0% | -14.06 | 118 |
| element_symbol | `assert_r1` | neutral | `user_guard_falsehood_above` | 0.0% | -15.23 | 118 |
| element_symbol | `assert_r1` | neutral | `user_guard_falsehood_below` | 0.0% | -15.30 | 118 |
| element_symbol | `assert_r1` | neutral | `retrieved_turn` | 14.4% | -1.22 | 118 |
| element_symbol | `assert_r1` | parametric | `inline` | 0.0% | -14.76 | 118 |
| element_symbol | `assert_r1` | parametric | `delimited` | 0.0% | -16.91 | 118 |
| element_symbol | `assert_r1` | parametric | `system_guard_falsehood` | 0.0% | -16.47 | 118 |
| element_symbol | `assert_r1` | parametric | `user_guard_falsehood_above` | 0.0% | -16.64 | 118 |
| element_symbol | `assert_r1` | parametric | `user_guard_falsehood_below` | 0.0% | -15.80 | 118 |
| element_symbol | `assert_r1` | parametric | `retrieved_turn` | 0.0% | -14.43 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `inline` | 94.1% | 1.81 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `delimited` | 100.0% | 3.39 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `system_guard_falsehood` | 5.9% | -2.65 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `user_guard_falsehood_above` | 0.0% | -8.79 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `user_guard_falsehood_below` | 0.0% | -11.34 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `retrieved_turn` | 66.9% | 0.37 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `inline` | 0.0% | -11.14 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `delimited` | 0.0% | -14.27 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `system_guard_falsehood` | 0.0% | -14.92 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `user_guard_falsehood_above` | 0.0% | -15.37 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `user_guard_falsehood_below` | 0.0% | -14.23 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `retrieved_turn` | 0.0% | -14.47 | 118 |
| country_capital | `assert_r1` | neutral | `inline` | 0.0% | -11.07 | 146 |
| country_capital | `assert_r1` | neutral | `delimited` | 41.1% | 0.02 | 146 |
| country_capital | `assert_r1` | neutral | `system_guard_falsehood` | 0.0% | -12.26 | 146 |
| country_capital | `assert_r1` | neutral | `user_guard_falsehood_above` | 0.0% | -17.70 | 146 |
| country_capital | `assert_r1` | neutral | `user_guard_falsehood_below` | 0.0% | -17.42 | 146 |
| country_capital | `assert_r1` | neutral | `retrieved_turn` | 2.7% | -2.68 | 146 |
| country_capital | `assert_r1` | parametric | `inline` | 0.0% | -16.90 | 146 |
| country_capital | `assert_r1` | parametric | `delimited` | 0.0% | -17.70 | 146 |
| country_capital | `assert_r1` | parametric | `system_guard_falsehood` | 0.0% | -17.48 | 146 |
| country_capital | `assert_r1` | parametric | `user_guard_falsehood_above` | 0.0% | -18.90 | 146 |
| country_capital | `assert_r1` | parametric | `user_guard_falsehood_below` | 0.0% | -17.36 | 146 |
| country_capital | `assert_r1` | parametric | `retrieved_turn` | 0.0% | -15.74 | 146 |
| country_capital | `explicit_stipulation` | neutral | `inline` | 100.0% | 7.01 | 146 |
| country_capital | `explicit_stipulation` | neutral | `delimited` | 100.0% | 10.62 | 146 |
| country_capital | `explicit_stipulation` | neutral | `system_guard_falsehood` | 25.3% | -1.66 | 146 |
| country_capital | `explicit_stipulation` | neutral | `user_guard_falsehood_above` | 0.0% | -12.81 | 146 |
| country_capital | `explicit_stipulation` | neutral | `user_guard_falsehood_below` | 0.0% | -17.39 | 146 |
| country_capital | `explicit_stipulation` | neutral | `retrieved_turn` | 61.6% | 0.31 | 146 |
| country_capital | `explicit_stipulation` | parametric | `inline` | 0.0% | -11.56 | 146 |
| country_capital | `explicit_stipulation` | parametric | `delimited` | 0.0% | -16.94 | 146 |
| country_capital | `explicit_stipulation` | parametric | `system_guard_falsehood` | 0.0% | -18.16 | 146 |
| country_capital | `explicit_stipulation` | parametric | `user_guard_falsehood_above` | 0.0% | -18.74 | 146 |
| country_capital | `explicit_stipulation` | parametric | `user_guard_falsehood_below` | 0.0% | -18.42 | 146 |
| country_capital | `explicit_stipulation` | parametric | `retrieved_turn` | 0.0% | -16.23 | 146 |

## How to read this

- **`inline` is the baseline** and should reproduce E8. If it does not, nothing else here is comparable.
- **The decisive comparison** is `explicit_stipulation` under `neutral` across channels. E8 measured 100% for that cell with no boundary at all. If it stays near 100% through `system_guard` and `retrieved_turn`, the model does not track who authored an imperative and a system-prompt guard does not fix it. If it falls, E8's hierarchy framing was an artefact of the single-turn prompt and should be retracted.
- **`assert_r1` is the control.** It carries the same false fact without an imperative, so a channel effect there is about source trust rather than instruction-following. Report the two together or neither.
- **user versus system, wording held fixed, is the channel test.** The guard sentences and the `<document>` wrapper are identical in both; only the turn they sit in changes. If the user slot suppresses deference and the system slot does not, provenance has to be stated in-band and the claim is about the channel. If neither suppresses, the channel is not the variable: a tag NAME is read and prose about the tag is not, wherever it sits -- which is a different claim and has to be written up as one.
- **`_below` versus `_above`, wording held fixed, is the position test.** The two strings are identical and so is everything around them; only which side of the `<document>` block the guard paragraph sits on changes. This matters because the `parametric` policy line is already a prose guard that works (about -49 logits against `delimited` on Gemma, more than renaming the tag) and it sits below the block. If `_below` works where `_above` does not, the finding is about position and not about the delimiter slot at all.
- Under `parametric` the user has told the model to ignore the paragraph. Any non-zero context-following there is the document winning against an explicit user instruction.
