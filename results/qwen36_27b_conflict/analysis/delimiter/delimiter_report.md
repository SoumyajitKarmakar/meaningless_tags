# E12: what the wrapper is doing — Qwen/Qwen3.6-27B

The paragraph, claim sentence, question and response constraint are byte-identical in every row. Only the block that encloses the paragraph changes. `delta vs inline` is paired within fact and cluster-bootstrapped over facts.


| Relation | Wrapper | What it rules out | Cell | n | Context | Margin | Δ vs inline | 95% CI |
|---|---|---|---|---:|---:|---:|---:|---:|
| element_symbol | `inline` | baseline | `assert_r1` | 118 | 0.0% | -7.19 | +0.00 | [+0.00, +0.00] |
| element_symbol | `inline` | baseline | `bare` | 118 | 35.6% | -0.43 | +0.00 | [+0.00, +0.00] |
| element_symbol | `blankline` | layout only | `assert_r1` | 118 | 0.0% | -7.15 | +0.04 | [-0.07, +0.14] |
| element_symbol | `blankline` | layout only | `bare` | 118 | 37.3% | -0.44 | -0.01 | [-0.04, +0.02] |
| element_symbol | `dashes` | layout + fence | `assert_r1` | 118 | 0.8% | -3.86 | +3.32 | [+3.09, +3.56] |
| element_symbol | `dashes` | layout + fence | `bare` | 118 | 78.8% | 0.55 | +0.98 | [+0.87, +1.10] |
| element_symbol | `quotes` | layout + fence | `assert_r1` | 118 | 1.7% | -3.81 | +3.37 | [+3.10, +3.65] |
| element_symbol | `quotes` | layout + fence | `bare` | 118 | 80.5% | 0.69 | +1.12 | [+0.98, +1.26] |
| element_symbol | `tag_document` | E11's condition | `assert_r1` | 118 | 63.6% | 0.56 | +7.75 | [+7.44, +8.06] |
| element_symbol | `tag_document` | E11's condition | `bare` | 118 | 100.0% | 2.91 | +3.34 | [+3.14, +3.56] |
| element_symbol | `tag_passage` | same syntax, different word | `assert_r1` | 118 | 54.2% | 0.28 | +7.46 | [+7.15, +7.77] |
| element_symbol | `tag_passage` | same syntax, different word | `bare` | 118 | 97.5% | 2.26 | +2.69 | [+2.49, +2.89] |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `assert_r1` | 118 | 0.0% | -5.04 | +2.15 | [+1.94, +2.36] |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `bare` | 118 | 34.7% | -0.18 | +0.26 | [+0.14, +0.37] |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `assert_r1` | 118 | 0.0% | -7.94 | -0.75 | [-0.95, -0.55] |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `bare` | 118 | 3.4% | -1.70 | -1.27 | [-1.40, -1.15] |
| element_symbol | `tag_unreliable` | opposite valence, different words | `assert_r1` | 118 | 0.0% | -8.18 | -1.00 | [-1.25, -0.75] |
| element_symbol | `tag_unreliable` | opposite valence, different words | `bare` | 118 | 0.0% | -3.05 | -2.62 | [-2.82, -2.43] |
| element_symbol | `tag_trusted` | same syntax, positive valence | `assert_r1` | 118 | 1.7% | -2.98 | +4.20 | [+3.92, +4.47] |
| element_symbol | `tag_trusted` | same syntax, positive valence | `bare` | 118 | 46.6% | -0.10 | +0.33 | [+0.20, +0.45] |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `assert_r1` | 118 | 3.4% | -2.50 | +4.69 | [+4.42, +4.95] |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `bare` | 118 | 64.4% | 0.37 | +0.80 | [+0.67, +0.93] |
| element_symbol | `tag_gibberish` | no meaning at all | `assert_r1` | 118 | 0.0% | -3.73 | +3.46 | [+3.20, +3.71] |
| element_symbol | `tag_gibberish` | no meaning at all | `bare` | 118 | 34.7% | -0.38 | +0.05 | [-0.08, +0.17] |
| element_symbol | `label_nonsense` | nonsense label | `assert_r1` | 118 | 0.8% | -4.23 | +2.96 | [+2.72, +3.18] |
| element_symbol | `label_nonsense` | nonsense label | `bare` | 118 | 34.7% | -0.39 | +0.04 | [-0.12, +0.20] |
| element_symbol | `label_gibberish` | gibberish label | `assert_r1` | 118 | 0.8% | -4.16 | +3.02 | [+2.79, +3.25] |
| element_symbol | `label_gibberish` | gibberish label | `bare` | 118 | 20.3% | -0.81 | -0.38 | [-0.53, -0.22] |
| element_symbol | `label_document` | same word, no markup | `assert_r1` | 118 | 15.3% | -2.09 | +5.09 | [+4.80, +5.38] |
| element_symbol | `label_document` | same word, no markup | `bare` | 118 | 95.8% | 2.02 | +2.45 | [+2.24, +2.67] |
| element_symbol | `label_search` | the RAG framing | `assert_r1` | 118 | 2.5% | -3.20 | +3.99 | [+3.76, +4.22] |
| element_symbol | `label_search` | the RAG framing | `bare` | 118 | 74.6% | 0.67 | +1.11 | [+0.94, +1.27] |
| element_symbol | `label_untrusted` | opposite valence, no markup | `assert_r1` | 118 | 0.0% | -7.76 | -0.57 | [-0.82, -0.33] |
| element_symbol | `label_untrusted` | opposite valence, no markup | `bare` | 118 | 9.3% | -1.49 | -1.06 | [-1.21, -0.91] |
| country_capital | `inline` | baseline | `assert_r1` | 146 | 0.0% | -11.08 | +0.00 | [+0.00, +0.00] |
| country_capital | `inline` | baseline | `bare` | 146 | 3.4% | -4.28 | +0.00 | [+0.00, +0.00] |
| country_capital | `blankline` | layout only | `assert_r1` | 146 | 0.0% | -10.39 | +0.70 | [+0.57, +0.83] |
| country_capital | `blankline` | layout only | `bare` | 146 | 4.1% | -4.10 | +0.18 | [+0.13, +0.24] |
| country_capital | `dashes` | layout + fence | `assert_r1` | 146 | 2.1% | -7.09 | +3.99 | [+3.67, +4.30] |
| country_capital | `dashes` | layout + fence | `bare` | 146 | 24.7% | -0.66 | +3.62 | [+3.39, +3.86] |
| country_capital | `quotes` | layout + fence | `assert_r1` | 146 | 2.1% | -5.87 | +5.21 | [+4.87, +5.56] |
| country_capital | `quotes` | layout + fence | `bare` | 146 | 27.4% | -0.67 | +3.61 | [+3.38, +3.83] |
| country_capital | `tag_document` | E11's condition | `assert_r1` | 146 | 41.1% | 0.00 | +11.09 | [+10.64, +11.51] |
| country_capital | `tag_document` | E11's condition | `bare` | 146 | 96.6% | 2.70 | +6.98 | [+6.61, +7.37] |
| country_capital | `tag_passage` | same syntax, different word | `assert_r1` | 146 | 30.1% | -0.56 | +10.52 | [+10.07, +10.97] |
| country_capital | `tag_passage` | same syntax, different word | `bare` | 146 | 100.0% | 4.95 | +9.23 | [+8.80, +9.68] |
| country_capital | `tag_empty` | bracket syntax, no name at all | `assert_r1` | 146 | 2.1% | -7.10 | +3.98 | [+3.64, +4.30] |
| country_capital | `tag_empty` | bracket syntax, no name at all | `bare` | 146 | 7.5% | -1.97 | +2.31 | [+2.10, +2.53] |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `assert_r1` | 146 | 0.0% | -13.01 | -1.93 | [-2.30, -1.55] |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `bare` | 146 | 2.7% | -4.48 | -0.20 | [-0.41, -0.00] |
| country_capital | `tag_unreliable` | opposite valence, different words | `assert_r1` | 146 | 0.0% | -13.38 | -2.30 | [-2.68, -1.93] |
| country_capital | `tag_unreliable` | opposite valence, different words | `bare` | 146 | 0.0% | -10.74 | -6.46 | [-6.83, -6.07] |
| country_capital | `tag_trusted` | same syntax, positive valence | `assert_r1` | 146 | 4.8% | -4.91 | +6.17 | [+5.78, +6.55] |
| country_capital | `tag_trusted` | same syntax, positive valence | `bare` | 146 | 43.8% | -0.13 | +4.15 | [+3.90, +4.40] |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `assert_r1` | 146 | 4.1% | -7.10 | +3.98 | [+3.62, +4.34] |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `bare` | 146 | 22.6% | -0.89 | +3.39 | [+3.17, +3.61] |
| country_capital | `tag_gibberish` | no meaning at all | `assert_r1` | 146 | 2.7% | -7.49 | +3.59 | [+3.23, +3.96] |
| country_capital | `tag_gibberish` | no meaning at all | `bare` | 146 | 8.9% | -2.39 | +1.89 | [+1.69, +2.11] |
| country_capital | `label_nonsense` | nonsense label | `assert_r1` | 146 | 1.4% | -7.71 | +3.37 | [+3.05, +3.69] |
| country_capital | `label_nonsense` | nonsense label | `bare` | 146 | 5.5% | -2.25 | +2.03 | [+1.83, +2.26] |
| country_capital | `label_gibberish` | gibberish label | `assert_r1` | 146 | 0.7% | -7.90 | +3.18 | [+2.86, +3.49] |
| country_capital | `label_gibberish` | gibberish label | `bare` | 146 | 5.5% | -2.19 | +2.09 | [+1.88, +2.31] |
| country_capital | `label_document` | same word, no markup | `assert_r1` | 146 | 5.5% | -4.87 | +6.22 | [+5.85, +6.58] |
| country_capital | `label_document` | same word, no markup | `bare` | 146 | 82.9% | 1.39 | +5.67 | [+5.30, +6.04] |
| country_capital | `label_search` | the RAG framing | `assert_r1` | 146 | 2.7% | -5.72 | +5.36 | [+5.01, +5.72] |
| country_capital | `label_search` | the RAG framing | `bare` | 146 | 50.7% | 0.19 | +4.46 | [+4.21, +4.72] |
| country_capital | `label_untrusted` | opposite valence, no markup | `assert_r1` | 146 | 0.0% | -12.32 | -1.24 | [-1.57, -0.90] |
| country_capital | `label_untrusted` | opposite valence, no markup | `bare` | 146 | 2.1% | -3.60 | +0.68 | [+0.44, +0.94] |

## How to read this

- **`blankline` is the layout control.** If it moves the margin as much as `tag_document`, E11's effect was whitespace and the document framing is a red herring. If it does not, the markup is doing real work.
- **`tag_passage` versus `tag_document`** separates the syntax from the word. **`label_document`** separates the word from the syntax.
- **`tag_untrusted` is the one to report.** It is the tag whose entire purpose is to mark text as not-to-be-trusted. If deference under it matches `tag_document`, the wrapper is read as *this is source material* and its stated valence is ignored. If it does NOT -- if the tag suppresses deference -- then the model is reading the label's meaning, and the question becomes why the same words fail when they are put in the system prompt instead.
- **`tag_nonsense` is the control for that reading.** `<qzx_block>` carries the same syntax and no meaning. If it behaves like `<document>`, an unfamiliar tag is not inherently suppressive and a low score for `<untrusted_content>` really is about the word. If it behaves like `<untrusted_content>`, then any out-of-distribution tag suppresses deference and the semantic reading is wrong. `tag_trusted` and `tag_unreliable` place the same contrast on a scale.
- **`tag_empty` splits the structure term itself.** `<qzx_block>` still has a name; `<>` has only the brackets. If `<>` matches `<qzx_block>`, the name contributes nothing and the structural effect is the bracket syntax. If `<>` falls back toward `dashes`, then a tag needs to NAME something -- anything -- and `<qzx_block>`'s +31 was already partly semantic.
- **`bare` versus `assert_r1`** asks whether the wrapper confers source authority or changes the task. `bare` has no source to trust, so if it swings too, the model is switching into reading-comprehension mode rather than deciding whom to believe.
- Margins are teacher-forced. Rates classify the answer with any reasoning preamble stripped.
