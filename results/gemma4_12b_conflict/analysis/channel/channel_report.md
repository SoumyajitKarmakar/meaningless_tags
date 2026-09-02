# E11: does the channel matter? — google/gemma-4-12B-it

The claim sentence, paragraph, question and user instruction are byte-identical across channels. Only who appears to be speaking changes.


| Relation | Cell | Policy | Channel | Context-following | Mean margin | n |
|---|---|---|---|---:|---:|---:|
| element_symbol | `assert_r1` | neutral | `inline` | 0.0% | -27.00 | 118 |
| element_symbol | `assert_r1` | neutral | `delimited` | 100.0% | 13.86 | 118 |
| element_symbol | `assert_r1` | neutral | `system_guard_falsehood` | 0.0% | -30.54 | 118 |
| element_symbol | `assert_r1` | neutral | `user_guard_falsehood_above` | 0.0% | -34.68 | 118 |
| element_symbol | `assert_r1` | neutral | `user_guard_falsehood_below` | 0.0% | -35.74 | 118 |
| element_symbol | `assert_r1` | neutral | `retrieved_turn` | 59.3% | 0.11 | 118 |
| element_symbol | `assert_r1` | parametric | `inline` | 0.0% | -35.35 | 118 |
| element_symbol | `assert_r1` | parametric | `delimited` | 0.0% | -34.97 | 118 |
| element_symbol | `assert_r1` | parametric | `system_guard_falsehood` | 0.0% | -35.73 | 118 |
| element_symbol | `assert_r1` | parametric | `user_guard_falsehood_above` | 0.0% | -36.07 | 118 |
| element_symbol | `assert_r1` | parametric | `user_guard_falsehood_below` | 0.0% | -35.90 | 118 |
| element_symbol | `assert_r1` | parametric | `retrieved_turn` | 0.0% | -34.51 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `inline` | 99.2% | 18.13 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `delimited` | 100.0% | 21.88 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `system_guard_falsehood` | 99.2% | 13.54 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `user_guard_falsehood_above` | 23.7% | -5.05 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `user_guard_falsehood_below` | 4.2% | -25.65 | 118 |
| element_symbol | `explicit_stipulation` | neutral | `retrieved_turn` | 95.8% | 11.15 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `inline` | 0.8% | -27.60 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `delimited` | 2.5% | -23.22 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `system_guard_falsehood` | 0.8% | -32.85 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `user_guard_falsehood_above` | 0.8% | -32.75 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `user_guard_falsehood_below` | 0.8% | -31.74 | 118 |
| element_symbol | `explicit_stipulation` | parametric | `retrieved_turn` | 0.0% | -32.02 | 118 |
| country_capital | `assert_r1` | neutral | `inline` | 0.0% | -28.08 | 143 |
| country_capital | `assert_r1` | neutral | `delimited` | 100.0% | 12.65 | 143 |
| country_capital | `assert_r1` | neutral | `system_guard_falsehood` | 0.0% | -29.23 | 143 |
| country_capital | `assert_r1` | neutral | `user_guard_falsehood_above` | 0.0% | -36.25 | 143 |
| country_capital | `assert_r1` | neutral | `user_guard_falsehood_below` | 0.0% | -37.33 | 143 |
| country_capital | `assert_r1` | neutral | `retrieved_turn` | 96.5% | 6.26 | 143 |
| country_capital | `assert_r1` | parametric | `inline` | 0.0% | -37.38 | 143 |
| country_capital | `assert_r1` | parametric | `delimited` | 0.0% | -37.36 | 143 |
| country_capital | `assert_r1` | parametric | `system_guard_falsehood` | 0.0% | -37.69 | 143 |
| country_capital | `assert_r1` | parametric | `user_guard_falsehood_above` | 0.0% | -37.84 | 143 |
| country_capital | `assert_r1` | parametric | `user_guard_falsehood_below` | 0.0% | -37.39 | 143 |
| country_capital | `assert_r1` | parametric | `retrieved_turn` | 0.0% | -37.09 | 143 |
| country_capital | `explicit_stipulation` | neutral | `inline` | 100.0% | 27.04 | 143 |
| country_capital | `explicit_stipulation` | neutral | `delimited` | 100.0% | 27.39 | 143 |
| country_capital | `explicit_stipulation` | neutral | `system_guard_falsehood` | 91.6% | 7.41 | 143 |
| country_capital | `explicit_stipulation` | neutral | `user_guard_falsehood_above` | 8.4% | -12.36 | 143 |
| country_capital | `explicit_stipulation` | neutral | `user_guard_falsehood_below` | 0.0% | -36.55 | 143 |
| country_capital | `explicit_stipulation` | neutral | `retrieved_turn` | 100.0% | 20.10 | 143 |
| country_capital | `explicit_stipulation` | parametric | `inline` | 0.0% | -36.63 | 143 |
| country_capital | `explicit_stipulation` | parametric | `delimited` | 0.0% | -37.43 | 143 |
| country_capital | `explicit_stipulation` | parametric | `system_guard_falsehood` | 0.0% | -38.22 | 143 |
| country_capital | `explicit_stipulation` | parametric | `user_guard_falsehood_above` | 0.0% | -38.38 | 143 |
| country_capital | `explicit_stipulation` | parametric | `user_guard_falsehood_below` | 0.0% | -37.66 | 143 |
| country_capital | `explicit_stipulation` | parametric | `retrieved_turn` | 0.0% | -36.20 | 143 |

## How to read this

- **`inline` is the baseline** and should reproduce E8. If it does not, nothing else here is comparable.
- **The decisive comparison** is `explicit_stipulation` across channels. E8 measured 100% for that cell with no boundary at all. If it stays near 100% through `system_guard` and `retrieved_turn`, the model does not track who authored an imperative and a system-prompt guard does not fix it. If it falls, E8's hierarchy framing was an artefact of the single-turn prompt and should be retracted.
- **`assert_r1` is the control.** It carries the same false fact without an imperative, so a channel effect there is about source trust rather than instruction-following. Report the two together or neither.
- **user versus system, wording held fixed, is the channel test.** The guard sentences and the `<document>` wrapper are identical in both; only the turn they sit in changes. If the user slot suppresses deference and the system slot does not, provenance has to be stated in-band and the claim is about the channel. If neither suppresses, the channel is not the variable: a tag NAME is read and prose about the tag is not, wherever it sits -- which is a different claim and has to be written up as one.
- **`_below` versus `_above`, wording held fixed, is the position test.** The two strings are identical and so is everything around them; only which side of the `<document>` block the guard paragraph sits on changes. Position is also distance to the question, so the two cannot be separated here -- if `_below` works where `_above` does not, the finding is about one of those and not about the delimiter slot at all.
