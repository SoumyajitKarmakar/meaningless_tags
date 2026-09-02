# E12: what the wrapper is doing — google/gemma-4-12B-it

The paragraph, claim sentence, question and response constraint are byte-identical in every row. Only the block that encloses the paragraph changes. `delta vs inline` is paired within fact and cluster-bootstrapped over facts.


| Relation | Wrapper | What it rules out | Cell | n | Context | Margin | Δ vs inline | 95% CI |
|---|---|---|---|---:|---:|---:|---:|---:|
| element_symbol | `inline` | baseline | `assert_r1` | 118 | 0.0% | -27.08 | +0.00 | [+0.00, +0.00] |
| element_symbol | `inline` | baseline | `bare` | 118 | 8.5% | -15.56 | +0.00 | [+0.00, +0.00] |
| element_symbol | `blankline` | layout only | `assert_r1` | 118 | 0.0% | -25.82 | +1.26 | [+0.92, +1.62] |
| element_symbol | `blankline` | layout only | `bare` | 118 | 8.5% | -14.11 | +1.45 | [+0.89, +2.08] |
| element_symbol | `dashes` | layout + fence | `assert_r1` | 118 | 23.7% | -9.28 | +17.80 | [+16.27, +19.34] |
| element_symbol | `dashes` | layout + fence | `bare` | 118 | 81.4% | 4.11 | +19.68 | [+18.18, +21.20] |
| element_symbol | `quotes` | layout + fence | `assert_r1` | 118 | 5.9% | -18.51 | +8.56 | [+7.35, +9.89] |
| element_symbol | `quotes` | layout + fence | `bare` | 118 | 88.1% | 4.74 | +20.30 | [+18.71, +21.91] |
| element_symbol | `tag_document` | E11's condition | `assert_r1` | 118 | 100.0% | 13.90 | +40.98 | [+39.61, +42.38] |
| element_symbol | `tag_document` | E11's condition | `bare` | 118 | 98.3% | 14.33 | +29.89 | [+28.14, +31.55] |
| element_symbol | `tag_passage` | same syntax, different word | `assert_r1` | 118 | 100.0% | 13.19 | +40.27 | [+38.95, +41.60] |
| element_symbol | `tag_passage` | same syntax, different word | `bare` | 118 | 98.3% | 14.16 | +29.73 | [+27.99, +31.36] |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `assert_r1` | 118 | 25.4% | -12.51 | +14.56 | [+12.77, +16.31] |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `bare` | 118 | 93.2% | 6.98 | +22.54 | [+21.10, +23.92] |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `assert_r1` | 118 | 0.0% | -24.32 | +2.76 | [+1.89, +3.66] |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `bare` | 118 | 31.4% | -6.98 | +8.58 | [+6.73, +10.55] |
| element_symbol | `tag_unreliable` | opposite valence, different words | `assert_r1` | 118 | 28.8% | -5.98 | +21.10 | [+19.68, +22.54] |
| element_symbol | `tag_unreliable` | opposite valence, different words | `bare` | 118 | 56.8% | -0.93 | +14.63 | [+12.87, +16.38] |
| element_symbol | `tag_trusted` | same syntax, positive valence | `assert_r1` | 118 | 100.0% | 16.36 | +43.43 | [+42.06, +44.87] |
| element_symbol | `tag_trusted` | same syntax, positive valence | `bare` | 118 | 99.2% | 17.19 | +32.76 | [+30.89, +34.52] |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `assert_r1` | 118 | 78.8% | 4.11 | +31.19 | [+29.73, +32.64] |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `bare` | 118 | 95.8% | 9.28 | +24.84 | [+23.28, +26.29] |
| element_symbol | `tag_gibberish` | no meaning at all | `assert_r1` | 118 | 49.2% | -2.96 | +24.11 | [+22.27, +25.89] |
| element_symbol | `tag_gibberish` | no meaning at all | `bare` | 118 | 64.4% | 0.17 | +15.73 | [+14.04, +17.41] |
| element_symbol | `label_nonsense` | nonsense label | `assert_r1` | 118 | 35.6% | -6.07 | +21.01 | [+19.32, +22.78] |
| element_symbol | `label_nonsense` | nonsense label | `bare` | 118 | 44.9% | -3.08 | +12.48 | [+11.01, +13.81] |
| element_symbol | `label_gibberish` | gibberish label | `assert_r1` | 118 | 5.9% | -19.19 | +7.89 | [+6.74, +9.14] |
| element_symbol | `label_gibberish` | gibberish label | `bare` | 118 | 5.9% | -19.09 | -3.53 | [-4.70, -2.34] |
| element_symbol | `label_document` | same word, no markup | `assert_r1` | 118 | 98.3% | 11.45 | +38.52 | [+37.13, +39.92] |
| element_symbol | `label_document` | same word, no markup | `bare` | 118 | 74.6% | 9.08 | +24.64 | [+23.02, +26.14] |
| element_symbol | `label_search` | the RAG framing | `assert_r1` | 118 | 100.0% | 12.95 | +40.03 | [+38.69, +41.36] |
| element_symbol | `label_search` | the RAG framing | `bare` | 118 | 64.4% | 9.27 | +24.84 | [+23.19, +26.49] |
| element_symbol | `label_untrusted` | opposite valence, no markup | `assert_r1` | 118 | 0.0% | -21.44 | +5.64 | [+4.74, +6.61] |
| element_symbol | `label_untrusted` | opposite valence, no markup | `bare` | 118 | 11.0% | -10.35 | +5.21 | [+3.71, +6.72] |
| country_capital | `inline` | baseline | `assert_r1` | 143 | 0.0% | -28.07 | +0.00 | [+0.00, +0.00] |
| country_capital | `inline` | baseline | `bare` | 143 | 25.2% | -9.41 | +0.00 | [+0.00, +0.00] |
| country_capital | `blankline` | layout only | `assert_r1` | 143 | 0.0% | -24.18 | +3.90 | [+3.51, +4.31] |
| country_capital | `blankline` | layout only | `bare` | 143 | 30.1% | -4.63 | +4.78 | [+4.17, +5.41] |
| country_capital | `dashes` | layout + fence | `assert_r1` | 143 | 33.6% | -4.80 | +23.28 | [+21.93, +24.58] |
| country_capital | `dashes` | layout + fence | `bare` | 143 | 67.8% | 4.83 | +14.24 | [+13.06, +15.46] |
| country_capital | `quotes` | layout + fence | `assert_r1` | 143 | 53.8% | -1.64 | +26.43 | [+25.11, +27.71] |
| country_capital | `quotes` | layout + fence | `bare` | 143 | 52.4% | 8.52 | +17.93 | [+16.59, +19.25] |
| country_capital | `tag_document` | E11's condition | `assert_r1` | 143 | 100.0% | 12.61 | +40.69 | [+39.57, +41.79] |
| country_capital | `tag_document` | E11's condition | `bare` | 143 | 100.0% | 16.49 | +25.90 | [+24.48, +27.35] |
| country_capital | `tag_passage` | same syntax, different word | `assert_r1` | 143 | 100.0% | 10.66 | +38.73 | [+37.61, +39.83] |
| country_capital | `tag_passage` | same syntax, different word | `bare` | 143 | 100.0% | 16.22 | +25.62 | [+24.18, +27.15] |
| country_capital | `tag_empty` | bracket syntax, no name at all | `assert_r1` | 143 | 62.9% | 0.76 | +28.83 | [+27.34, +30.25] |
| country_capital | `tag_empty` | bracket syntax, no name at all | `bare` | 143 | 69.9% | 8.24 | +17.65 | [+16.35, +18.97] |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `assert_r1` | 143 | 0.0% | -27.33 | +0.74 | [+0.27, +1.20] |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `bare` | 143 | 3.5% | -17.63 | -8.22 | [-9.94, -6.51] |
| country_capital | `tag_unreliable` | opposite valence, different words | `assert_r1` | 143 | 0.7% | -21.73 | +6.34 | [+5.67, +7.02] |
| country_capital | `tag_unreliable` | opposite valence, different words | `bare` | 143 | 2.1% | -15.50 | -6.09 | [-8.00, -4.31] |
| country_capital | `tag_trusted` | same syntax, positive valence | `assert_r1` | 143 | 100.0% | 17.01 | +45.08 | [+43.96, +46.27] |
| country_capital | `tag_trusted` | same syntax, positive valence | `bare` | 143 | 100.0% | 18.67 | +28.08 | [+26.56, +29.65] |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `assert_r1` | 143 | 74.8% | 2.88 | +30.96 | [+29.63, +32.28] |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `bare` | 143 | 78.3% | 3.96 | +13.37 | [+12.06, +14.68] |
| country_capital | `tag_gibberish` | no meaning at all | `assert_r1` | 143 | 36.4% | -4.44 | +23.64 | [+21.98, +25.14] |
| country_capital | `tag_gibberish` | no meaning at all | `bare` | 143 | 23.8% | -8.08 | +1.32 | [+0.28, +2.43] |
| country_capital | `label_nonsense` | nonsense label | `assert_r1` | 143 | 3.5% | -20.34 | +7.73 | [+6.63, +8.84] |
| country_capital | `label_nonsense` | nonsense label | `bare` | 143 | 14.0% | -12.16 | -2.75 | [-3.73, -1.76] |
| country_capital | `label_gibberish` | gibberish label | `assert_r1` | 143 | 0.0% | -24.00 | +4.07 | [+3.37, +4.79] |
| country_capital | `label_gibberish` | gibberish label | `bare` | 143 | 5.6% | -19.89 | -10.48 | [-11.77, -9.26] |
| country_capital | `label_document` | same word, no markup | `assert_r1` | 143 | 99.3% | 10.29 | +38.37 | [+37.26, +39.48] |
| country_capital | `label_document` | same word, no markup | `bare` | 143 | 88.1% | 18.02 | +27.43 | [+25.91, +28.97] |
| country_capital | `label_search` | the RAG framing | `assert_r1` | 143 | 100.0% | 13.38 | +41.45 | [+40.33, +42.55] |
| country_capital | `label_search` | the RAG framing | `bare` | 143 | 81.1% | 14.77 | +24.18 | [+22.75, +25.60] |
| country_capital | `label_untrusted` | opposite valence, no markup | `assert_r1` | 143 | 0.7% | -19.29 | +8.79 | [+7.99, +9.57] |
| country_capital | `label_untrusted` | opposite valence, no markup | `bare` | 143 | 14.0% | -11.21 | -1.80 | [-3.09, -0.52] |

## How to read this

- **`blankline` is the layout control.** If it moves the margin as much as `tag_document`, E11's effect was whitespace and the document framing is a red herring. If it does not, the markup is doing real work.
- **`tag_passage` versus `tag_document`** separates the syntax from the word. **`label_document`** separates the word from the syntax.
- **`tag_untrusted` is the one to report.** It is the tag whose entire purpose is to mark text as not-to-be-trusted. If deference under it matches `tag_document`, the wrapper is read as *this is source material* and its stated valence is ignored. If it does NOT -- if the tag suppresses deference -- then the model is reading the label's meaning, and the question becomes why the same words fail when they are put in the system prompt instead.
- **`tag_nonsense` is the control for that reading.** `<qzx_block>` carries the same syntax and no meaning. If it behaves like `<document>`, an unfamiliar tag is not inherently suppressive and a low score for `<untrusted_content>` really is about the word. If it behaves like `<untrusted_content>`, then any out-of-distribution tag suppresses deference and the semantic reading is wrong. `tag_trusted` and `tag_unreliable` place the same contrast on a scale.
- **`tag_empty` splits the structure term itself.** `<qzx_block>` still has a name; `<>` has only the brackets. If `<>` matches `<qzx_block>`, the name contributes nothing and the structural effect is the bracket syntax. If `<>` falls back toward `dashes`, then a tag needs to NAME something -- anything -- and `<qzx_block>`'s +31 was already partly semantic.
- **`bare` versus `assert_r1`** asks whether the wrapper confers source authority or changes the task. `bare` has no source to trust, so if it swings too, the model is switching into reading-comprehension mode rather than deciding whom to believe.
- Margins are teacher-forced. Rates classify the answer with any reasoning preamble stripped.
