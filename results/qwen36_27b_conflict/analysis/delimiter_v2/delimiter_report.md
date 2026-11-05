# E12: what the wrapper is doing — Qwen/Qwen3.6-27B

The paragraph, claim sentence, question and response constraint are byte-identical in every row. Only the block that encloses the paragraph changes. `delta vs inline` is paired within fact and cell, and bootstrapped over facts. `d>0` counts facts whose margin rose.


| Relation | Wrapper | What it rules out | Cell | n | Context | Margin | Δ vs inline | 95% CI | d>0 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| element_symbol | `inline` | baseline | `assert_r1` | 118 | 0.0% | -7.24 | +0.00 | [+0.00, +0.00] | 0/118 |
| element_symbol | `inline` | baseline | `bare` | 118 | 35.6% | -0.42 | +0.00 | [+0.00, +0.00] | 0/118 |
| element_symbol | `inline` | baseline | `irrelevant_assert_r1` | 118 | 0.0% | -10.06 | +0.00 | [+0.00, +0.00] | 0/118 |
| element_symbol | `blankline` | layout only | `assert_r1` | 118 | 0.0% | -7.15 | +0.10 | [-0.01, +0.20] | 70/118 |
| element_symbol | `blankline` | layout only | `bare` | 118 | 36.4% | -0.44 | -0.02 | [-0.05, +0.01] | 49/118 |
| element_symbol | `blankline` | layout only | `irrelevant_assert_r1` | 118 | 0.0% | -10.09 | -0.03 | [-0.11, +0.06] | 56/118 |
| element_symbol | `dashes` | layout + fence | `assert_r1` | 118 | 1.7% | -3.86 | +3.39 | [+3.16, +3.63] | 118/118 |
| element_symbol | `dashes` | layout + fence | `bare` | 118 | 78.0% | 0.56 | +0.98 | [+0.87, +1.10] | 113/118 |
| element_symbol | `dashes` | layout + fence | `irrelevant_assert_r1` | 118 | 0.0% | -7.90 | +2.16 | [+1.95, +2.37] | 115/118 |
| element_symbol | `quotes` | layout + fence | `assert_r1` | 118 | 1.7% | -3.81 | +3.43 | [+3.16, +3.71] | 117/118 |
| element_symbol | `quotes` | layout + fence | `bare` | 118 | 80.5% | 0.69 | +1.12 | [+0.98, +1.25] | 111/118 |
| element_symbol | `quotes` | layout + fence | `irrelevant_assert_r1` | 118 | 0.0% | -8.72 | +1.35 | [+1.11, +1.58] | 103/118 |
| element_symbol | `tag_document` | E11's condition | `assert_r1` | 118 | 63.6% | 0.58 | +7.82 | [+7.52, +8.14] | 118/118 |
| element_symbol | `tag_document` | E11's condition | `bare` | 118 | 100.0% | 2.90 | +3.32 | [+3.12, +3.54] | 118/118 |
| element_symbol | `tag_document` | E11's condition | `irrelevant_assert_r1` | 118 | 0.0% | -6.57 | +3.50 | [+3.18, +3.82] | 117/118 |
| element_symbol | `tag_passage` | same syntax, different word | `assert_r1` | 118 | 55.9% | 0.28 | +7.53 | [+7.21, +7.85] | 118/118 |
| element_symbol | `tag_passage` | same syntax, different word | `bare` | 118 | 98.3% | 2.25 | +2.67 | [+2.47, +2.87] | 118/118 |
| element_symbol | `tag_passage` | same syntax, different word | `irrelevant_assert_r1` | 118 | 0.0% | -6.58 | +3.49 | [+3.17, +3.82] | 117/118 |
| element_symbol | `tag_search` | the RAG framing, as a tag | `assert_r1` | 118 | 26.3% | -0.55 | +6.69 | [+6.38, +7.01] | 118/118 |
| element_symbol | `tag_search` | the RAG framing, as a tag | `bare` | 118 | 98.3% | 2.12 | +2.54 | [+2.37, +2.72] | 118/118 |
| element_symbol | `tag_search` | the RAG framing, as a tag | `irrelevant_assert_r1` | 118 | 0.0% | -6.99 | +3.07 | [+2.77, +3.38] | 113/118 |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `assert_r1` | 118 | 0.0% | -5.04 | +2.20 | [+2.00, +2.41] | 114/118 |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `bare` | 118 | 33.9% | -0.18 | +0.24 | [+0.12, +0.35] | 74/118 |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `irrelevant_assert_r1` | 118 | 0.0% | -8.96 | +1.10 | [+0.90, +1.32] | 101/118 |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `assert_r1` | 118 | 0.0% | -7.94 | -0.69 | [-0.89, -0.49] | 26/118 |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `bare` | 118 | 3.4% | -1.71 | -1.29 | [-1.41, -1.16] | 5/118 |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `irrelevant_assert_r1` | 118 | 0.0% | -11.98 | -1.91 | [-2.14, -1.68] | 3/118 |
| element_symbol | `tag_unreliable` | opposite valence, different words | `assert_r1` | 118 | 0.0% | -8.18 | -0.94 | [-1.19, -0.69] | 27/118 |
| element_symbol | `tag_unreliable` | opposite valence, different words | `bare` | 118 | 0.0% | -3.05 | -2.63 | [-2.83, -2.44] | 0/118 |
| element_symbol | `tag_unreliable` | opposite valence, different words | `irrelevant_assert_r1` | 118 | 0.0% | -11.39 | -1.33 | [-1.56, -1.10] | 15/118 |
| element_symbol | `tag_trusted` | same syntax, positive valence | `assert_r1` | 118 | 1.7% | -2.98 | +4.26 | [+3.99, +4.54] | 118/118 |
| element_symbol | `tag_trusted` | same syntax, positive valence | `bare` | 118 | 46.6% | -0.10 | +0.32 | [+0.19, +0.44] | 78/118 |
| element_symbol | `tag_trusted` | same syntax, positive valence | `irrelevant_assert_r1` | 118 | 0.0% | -8.98 | +1.09 | [+0.87, +1.33] | 97/118 |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `assert_r1` | 118 | 3.4% | -2.50 | +4.75 | [+4.48, +5.02] | 118/118 |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `bare` | 118 | 64.4% | 0.37 | +0.79 | [+0.66, +0.92] | 101/118 |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `irrelevant_assert_r1` | 118 | 0.0% | -8.01 | +2.05 | [+1.81, +2.30] | 110/118 |
| element_symbol | `tag_gibberish` | no meaning at all | `assert_r1` | 118 | 0.0% | -3.73 | +3.52 | [+3.26, +3.77] | 118/118 |
| element_symbol | `tag_gibberish` | no meaning at all | `bare` | 118 | 34.7% | -0.38 | +0.04 | [-0.08, +0.16] | 61/118 |
| element_symbol | `tag_gibberish` | no meaning at all | `irrelevant_assert_r1` | 118 | 0.0% | -8.29 | +1.77 | [+1.54, +2.01] | 107/118 |
| element_symbol | `label_nonsense` | nonsense label | `assert_r1` | 118 | 0.8% | -4.23 | +3.01 | [+2.77, +3.24] | 116/118 |
| element_symbol | `label_nonsense` | nonsense label | `bare` | 118 | 33.9% | -0.40 | +0.03 | [-0.14, +0.19] | 59/118 |
| element_symbol | `label_nonsense` | nonsense label | `irrelevant_assert_r1` | 118 | 0.0% | -6.72 | +3.34 | [+3.10, +3.61] | 117/118 |
| element_symbol | `label_gibberish` | gibberish label | `assert_r1` | 118 | 0.8% | -4.16 | +3.09 | [+2.85, +3.32] | 117/118 |
| element_symbol | `label_gibberish` | gibberish label | `bare` | 118 | 22.0% | -0.81 | -0.38 | [-0.53, -0.23] | 39/118 |
| element_symbol | `label_gibberish` | gibberish label | `irrelevant_assert_r1` | 118 | 0.0% | -6.40 | +3.66 | [+3.41, +3.92] | 118/118 |
| element_symbol | `label_document` | same word, no markup | `assert_r1` | 118 | 13.6% | -2.09 | +5.16 | [+4.86, +5.45] | 118/118 |
| element_symbol | `label_document` | same word, no markup | `bare` | 118 | 96.6% | 2.01 | +2.43 | [+2.22, +2.65] | 118/118 |
| element_symbol | `label_document` | same word, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -8.12 | +1.94 | [+1.68, +2.20] | 107/118 |
| element_symbol | `label_passage` | <passage>'s word, no markup | `assert_r1` | 118 | 45.8% | 0.08 | +7.32 | [+6.97, +7.70] | 118/118 |
| element_symbol | `label_passage` | <passage>'s word, no markup | `bare` | 118 | 100.0% | 3.04 | +3.47 | [+3.25, +3.69] | 118/118 |
| element_symbol | `label_passage` | <passage>'s word, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -8.18 | +1.89 | [+1.60, +2.18] | 103/118 |
| element_symbol | `label_search` | the RAG framing | `assert_r1` | 118 | 2.5% | -3.19 | +4.06 | [+3.82, +4.29] | 117/118 |
| element_symbol | `label_search` | the RAG framing | `bare` | 118 | 73.7% | 0.67 | +1.10 | [+0.93, +1.26] | 107/118 |
| element_symbol | `label_search` | the RAG framing | `irrelevant_assert_r1` | 118 | 0.0% | -6.75 | +3.31 | [+3.04, +3.59] | 116/118 |
| element_symbol | `label_untrusted` | opposite valence, no markup | `assert_r1` | 118 | 0.0% | -7.76 | -0.52 | [-0.77, -0.27] | 44/118 |
| element_symbol | `label_untrusted` | opposite valence, no markup | `bare` | 118 | 10.2% | -1.49 | -1.07 | [-1.22, -0.92] | 10/118 |
| element_symbol | `label_untrusted` | opposite valence, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -8.27 | +1.80 | [+1.57, +2.03] | 108/118 |
| element_symbol | `label_unreliable` | <unreliable_source>'s words, no markup | `assert_r1` | 118 | 0.0% | -9.73 | -2.49 | [-2.80, -2.22] | 4/118 |
| element_symbol | `label_unreliable` | <unreliable_source>'s words, no markup | `bare` | 118 | 0.8% | -2.45 | -2.02 | [-2.22, -1.84] | 5/118 |
| element_symbol | `label_unreliable` | <unreliable_source>'s words, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -9.47 | +0.60 | [+0.39, +0.80] | 84/118 |
| element_symbol | `label_trusted` | <trusted_content>'s words, no markup | `assert_r1` | 118 | 3.4% | -3.50 | +3.75 | [+3.51, +3.98] | 116/118 |
| element_symbol | `label_trusted` | <trusted_content>'s words, no markup | `bare` | 118 | 68.6% | 0.53 | +0.95 | [+0.79, +1.11] | 106/118 |
| element_symbol | `label_trusted` | <trusted_content>'s words, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -6.50 | +3.57 | [+3.28, +3.87] | 117/118 |
| country_capital | `inline` | baseline | `assert_r1` | 146 | 0.0% | -11.08 | +0.00 | [+0.00, +0.00] | 0/146 |
| country_capital | `inline` | baseline | `bare` | 146 | 3.4% | -4.28 | +0.00 | [+0.00, +0.00] | 0/146 |
| country_capital | `inline` | baseline | `irrelevant_assert_r1` | 146 | 0.0% | -9.58 | +0.00 | [+0.00, +0.00] | 0/146 |
| country_capital | `blankline` | layout only | `assert_r1` | 146 | 0.0% | -10.39 | +0.68 | [+0.55, +0.81] | 130/146 |
| country_capital | `blankline` | layout only | `bare` | 146 | 4.1% | -4.10 | +0.18 | [+0.13, +0.23] | 108/146 |
| country_capital | `blankline` | layout only | `irrelevant_assert_r1` | 146 | 0.0% | -9.93 | -0.35 | [-0.44, -0.26] | 26/146 |
| country_capital | `dashes` | layout + fence | `assert_r1` | 146 | 2.1% | -7.07 | +4.01 | [+3.67, +4.32] | 144/146 |
| country_capital | `dashes` | layout + fence | `bare` | 146 | 24.7% | -0.67 | +3.61 | [+3.38, +3.85] | 146/146 |
| country_capital | `dashes` | layout + fence | `irrelevant_assert_r1` | 146 | 0.0% | -7.49 | +2.09 | [+1.82, +2.37] | 141/146 |
| country_capital | `quotes` | layout + fence | `assert_r1` | 146 | 2.1% | -5.87 | +5.21 | [+4.86, +5.55] | 146/146 |
| country_capital | `quotes` | layout + fence | `bare` | 146 | 25.3% | -0.66 | +3.61 | [+3.38, +3.84] | 145/146 |
| country_capital | `quotes` | layout + fence | `irrelevant_assert_r1` | 146 | 0.7% | -8.49 | +1.09 | [+0.81, +1.39] | 117/146 |
| country_capital | `tag_document` | E11's condition | `assert_r1` | 146 | 42.5% | 0.02 | +11.10 | [+10.65, +11.52] | 146/146 |
| country_capital | `tag_document` | E11's condition | `bare` | 146 | 96.6% | 2.70 | +6.98 | [+6.60, +7.36] | 146/146 |
| country_capital | `tag_document` | E11's condition | `irrelevant_assert_r1` | 146 | 0.0% | -8.84 | +0.74 | [+0.40, +1.07] | 93/146 |
| country_capital | `tag_passage` | same syntax, different word | `assert_r1` | 146 | 28.8% | -0.57 | +10.51 | [+10.05, +10.96] | 146/146 |
| country_capital | `tag_passage` | same syntax, different word | `bare` | 146 | 100.0% | 4.97 | +9.25 | [+8.82, +9.69] | 146/146 |
| country_capital | `tag_passage` | same syntax, different word | `irrelevant_assert_r1` | 146 | 0.0% | -9.54 | +0.04 | [-0.29, +0.35] | 69/146 |
| country_capital | `tag_search` | the RAG framing, as a tag | `assert_r1` | 146 | 16.4% | -1.27 | +9.80 | [+9.34, +10.27] | 146/146 |
| country_capital | `tag_search` | the RAG framing, as a tag | `bare` | 146 | 88.4% | 1.79 | +6.07 | [+5.73, +6.43] | 146/146 |
| country_capital | `tag_search` | the RAG framing, as a tag | `irrelevant_assert_r1` | 146 | 0.0% | -6.83 | +2.75 | [+2.36, +3.12] | 133/146 |
| country_capital | `tag_empty` | bracket syntax, no name at all | `assert_r1` | 146 | 2.1% | -7.09 | +3.99 | [+3.64, +4.32] | 143/146 |
| country_capital | `tag_empty` | bracket syntax, no name at all | `bare` | 146 | 7.5% | -1.98 | +2.30 | [+2.10, +2.52] | 141/146 |
| country_capital | `tag_empty` | bracket syntax, no name at all | `irrelevant_assert_r1` | 146 | 0.0% | -9.20 | +0.37 | [+0.13, +0.62] | 99/146 |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `assert_r1` | 146 | 0.0% | -13.00 | -1.92 | [-2.29, -1.54] | 27/146 |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `bare` | 146 | 2.7% | -4.49 | -0.21 | [-0.42, -0.01] | 66/146 |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `irrelevant_assert_r1` | 146 | 0.0% | -10.56 | -0.99 | [-1.27, -0.72] | 38/146 |
| country_capital | `tag_unreliable` | opposite valence, different words | `assert_r1` | 146 | 0.0% | -13.38 | -2.30 | [-2.68, -1.93] | 20/146 |
| country_capital | `tag_unreliable` | opposite valence, different words | `bare` | 146 | 0.0% | -10.74 | -6.47 | [-6.84, -6.08] | 0/146 |
| country_capital | `tag_unreliable` | opposite valence, different words | `irrelevant_assert_r1` | 146 | 0.0% | -9.92 | -0.34 | [-0.63, -0.05] | 61/146 |
| country_capital | `tag_trusted` | same syntax, positive valence | `assert_r1` | 146 | 4.8% | -4.91 | +6.17 | [+5.77, +6.54] | 146/146 |
| country_capital | `tag_trusted` | same syntax, positive valence | `bare` | 146 | 43.8% | -0.13 | +4.14 | [+3.89, +4.39] | 145/146 |
| country_capital | `tag_trusted` | same syntax, positive valence | `irrelevant_assert_r1` | 146 | 0.0% | -9.38 | +0.20 | [-0.10, +0.50] | 79/146 |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `assert_r1` | 146 | 4.1% | -7.10 | +3.98 | [+3.61, +4.33] | 142/146 |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `bare` | 146 | 22.6% | -0.89 | +3.38 | [+3.16, +3.60] | 146/146 |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `irrelevant_assert_r1` | 146 | 0.0% | -9.82 | -0.24 | [-0.51, +0.01] | 72/146 |
| country_capital | `tag_gibberish` | no meaning at all | `assert_r1` | 146 | 2.7% | -7.49 | +3.59 | [+3.22, +3.94] | 139/146 |
| country_capital | `tag_gibberish` | no meaning at all | `bare` | 146 | 8.9% | -2.39 | +1.89 | [+1.68, +2.10] | 139/146 |
| country_capital | `tag_gibberish` | no meaning at all | `irrelevant_assert_r1` | 146 | 0.0% | -10.40 | -0.82 | [-1.06, -0.60] | 35/146 |
| country_capital | `label_nonsense` | nonsense label | `assert_r1` | 146 | 1.4% | -7.71 | +3.37 | [+3.04, +3.69] | 140/146 |
| country_capital | `label_nonsense` | nonsense label | `bare` | 146 | 4.8% | -2.24 | +2.03 | [+1.82, +2.26] | 142/146 |
| country_capital | `label_nonsense` | nonsense label | `irrelevant_assert_r1` | 146 | 0.0% | -10.18 | -0.60 | [-0.87, -0.34] | 55/146 |
| country_capital | `label_gibberish` | gibberish label | `assert_r1` | 146 | 0.7% | -7.91 | +3.17 | [+2.84, +3.48] | 140/146 |
| country_capital | `label_gibberish` | gibberish label | `bare` | 146 | 5.5% | -2.19 | +2.09 | [+1.88, +2.31] | 140/146 |
| country_capital | `label_gibberish` | gibberish label | `irrelevant_assert_r1` | 146 | 0.0% | -9.59 | -0.01 | [-0.26, +0.25] | 80/146 |
| country_capital | `label_document` | same word, no markup | `assert_r1` | 146 | 5.5% | -4.87 | +6.21 | [+5.84, +6.58] | 146/146 |
| country_capital | `label_document` | same word, no markup | `bare` | 146 | 82.2% | 1.37 | +5.65 | [+5.28, +6.01] | 146/146 |
| country_capital | `label_document` | same word, no markup | `irrelevant_assert_r1` | 146 | 0.0% | -8.28 | +1.30 | [+0.99, +1.64] | 107/146 |
| country_capital | `label_passage` | <passage>'s word, no markup | `assert_r1` | 146 | 7.5% | -3.39 | +7.68 | [+7.27, +8.08] | 146/146 |
| country_capital | `label_passage` | <passage>'s word, no markup | `bare` | 146 | 95.2% | 2.43 | +6.71 | [+6.33, +7.12] | 146/146 |
| country_capital | `label_passage` | <passage>'s word, no markup | `irrelevant_assert_r1` | 146 | 0.7% | -8.75 | +0.82 | [+0.48, +1.16] | 96/146 |
| country_capital | `label_search` | the RAG framing | `assert_r1` | 146 | 2.7% | -5.69 | +5.38 | [+5.02, +5.75] | 146/146 |
| country_capital | `label_search` | the RAG framing | `bare` | 146 | 50.7% | 0.19 | +4.47 | [+4.21, +4.71] | 146/146 |
| country_capital | `label_search` | the RAG framing | `irrelevant_assert_r1` | 146 | 0.7% | -6.91 | +2.67 | [+2.31, +3.03] | 138/146 |
| country_capital | `label_untrusted` | opposite valence, no markup | `assert_r1` | 146 | 0.0% | -12.34 | -1.26 | [-1.60, -0.92] | 44/146 |
| country_capital | `label_untrusted` | opposite valence, no markup | `bare` | 146 | 2.1% | -3.62 | +0.66 | [+0.43, +0.92] | 103/146 |
| country_capital | `label_untrusted` | opposite valence, no markup | `irrelevant_assert_r1` | 146 | 0.0% | -11.25 | -1.67 | [-1.99, -1.36] | 25/146 |
| country_capital | `label_unreliable` | <unreliable_source>'s words, no markup | `assert_r1` | 146 | 0.0% | -14.10 | -3.02 | [-3.38, -2.68] | 3/146 |
| country_capital | `label_unreliable` | <unreliable_source>'s words, no markup | `bare` | 146 | 0.7% | -6.96 | -2.68 | [-2.94, -2.41] | 6/146 |
| country_capital | `label_unreliable` | <unreliable_source>'s words, no markup | `irrelevant_assert_r1` | 146 | 0.0% | -9.31 | +0.27 | [-0.02, +0.56] | 85/146 |
| country_capital | `label_trusted` | <trusted_content>'s words, no markup | `assert_r1` | 146 | 2.1% | -5.32 | +5.76 | [+5.35, +6.16] | 145/146 |
| country_capital | `label_trusted` | <trusted_content>'s words, no markup | `bare` | 146 | 49.3% | 0.12 | +4.40 | [+4.12, +4.67] | 146/146 |
| country_capital | `label_trusted` | <trusted_content>'s words, no markup | `irrelevant_assert_r1` | 146 | 0.0% | -8.64 | +0.94 | [+0.60, +1.29] | 101/146 |

## Relevance: the same wrapper around a paragraph about another subject

- element_symbol, unwrapped: relevant − irrelevant = +2.82 [+2.30, +3.41], 99/118 facts > 0.
- country_capital, unwrapped: relevant − irrelevant = -1.50 [-2.10, -0.90], 46/146 facts > 0.

| Relation | Wrapper | n | Δ relevant | Δ irrelevant | Interaction | 95% CI | Irrelevant / relevant |
|---|---|---:|---:|---:|---:|---:|---:|
| element_symbol | `blankline` | 118 | +0.10 | -0.03 | +0.13 | [-0.01, +0.26] | -0.29 |
| element_symbol | `dashes` | 118 | +3.39 | +2.16 | +1.23 | [+0.90, +1.53] | 0.64 |
| element_symbol | `quotes` | 118 | +3.43 | +1.35 | +2.08 | [+1.74, +2.43] | 0.39 |
| element_symbol | `tag_document` | 118 | +7.82 | +3.50 | +4.33 | [+3.93, +4.72] | 0.45 |
| element_symbol | `tag_passage` | 118 | +7.53 | +3.49 | +4.04 | [+3.62, +4.46] | 0.46 |
| element_symbol | `tag_search` | 118 | +6.69 | +3.07 | +3.62 | [+3.21, +4.05] | 0.46 |
| element_symbol | `tag_empty` | 118 | +2.20 | +1.10 | +1.10 | [+0.81, +1.40] | 0.50 |
| element_symbol | `tag_untrusted` | 118 | -0.69 | -1.91 | +1.22 | [+0.90, +1.53] | 2.76 |
| element_symbol | `tag_unreliable` | 118 | -0.94 | -1.33 | +0.39 | [+0.04, +0.74] | 1.42 |
| element_symbol | `tag_trusted` | 118 | +4.26 | +1.09 | +3.18 | [+2.83, +3.50] | 0.25 |
| element_symbol | `tag_nonsense` | 118 | +4.75 | +2.05 | +2.69 | [+2.37, +3.01] | 0.43 |
| element_symbol | `tag_gibberish` | 118 | +3.52 | +1.77 | +1.75 | [+1.39, +2.07] | 0.50 |
| element_symbol | `label_nonsense` | 118 | +3.01 | +3.34 | -0.33 | [-0.70, +0.02] | 1.11 |
| element_symbol | `label_gibberish` | 118 | +3.09 | +3.66 | -0.57 | [-0.94, -0.23] | 1.19 |
| element_symbol | `label_document` | 118 | +5.16 | +1.94 | +3.22 | [+2.84, +3.59] | 0.38 |
| element_symbol | `label_passage` | 118 | +7.32 | +1.89 | +5.44 | [+5.03, +5.83] | 0.26 |
| element_symbol | `label_search` | 118 | +4.06 | +3.31 | +0.74 | [+0.40, +1.06] | 0.82 |
| element_symbol | `label_untrusted` | 118 | -0.52 | +1.80 | -2.32 | [-2.66, -2.00] | -3.48 |
| element_symbol | `label_unreliable` | 118 | -2.49 | +0.60 | -3.09 | [-3.42, -2.78] | -0.24 |
| element_symbol | `label_trusted` | 118 | +3.75 | +3.57 | +0.18 | [-0.16, +0.50] | 0.95 |
| country_capital | `blankline` | 146 | +0.68 | -0.35 | +1.03 | [+0.87, +1.20] | -0.51 |
| country_capital | `dashes` | 146 | +4.01 | +2.09 | +1.92 | [+1.50, +2.34] | 0.52 |
| country_capital | `quotes` | 146 | +5.21 | +1.09 | +4.12 | [+3.65, +4.61] | 0.21 |
| country_capital | `tag_document` | 146 | +11.10 | +0.74 | +10.36 | [+9.80, +10.92] | 0.07 |
| country_capital | `tag_passage` | 146 | +10.51 | +0.04 | +10.47 | [+9.93, +11.06] | 0.00 |
| country_capital | `tag_search` | 146 | +9.80 | +2.75 | +7.05 | [+6.51, +7.61] | 0.28 |
| country_capital | `tag_empty` | 146 | +3.99 | +0.37 | +3.61 | [+3.22, +4.02] | 0.09 |
| country_capital | `tag_untrusted` | 146 | -1.92 | -0.99 | -0.94 | [-1.38, -0.50] | 0.51 |
| country_capital | `tag_unreliable` | 146 | -2.30 | -0.34 | -1.96 | [-2.48, -1.47] | 0.15 |
| country_capital | `tag_trusted` | 146 | +6.17 | +0.20 | +5.97 | [+5.51, +6.47] | 0.03 |
| country_capital | `tag_nonsense` | 146 | +3.98 | -0.24 | +4.22 | [+3.83, +4.65] | -0.06 |
| country_capital | `tag_gibberish` | 146 | +3.59 | -0.82 | +4.41 | [+4.01, +4.85] | -0.23 |
| country_capital | `label_nonsense` | 146 | +3.37 | -0.60 | +3.98 | [+3.55, +4.37] | -0.18 |
| country_capital | `label_gibberish` | 146 | +3.17 | -0.01 | +3.18 | [+2.76, +3.56] | -0.00 |
| country_capital | `label_document` | 146 | +6.21 | +1.30 | +4.91 | [+4.45, +5.38] | 0.21 |
| country_capital | `label_passage` | 146 | +7.68 | +0.82 | +6.86 | [+6.36, +7.38] | 0.11 |
| country_capital | `label_search` | 146 | +5.38 | +2.67 | +2.71 | [+2.26, +3.18] | 0.50 |
| country_capital | `label_untrusted` | 146 | -1.26 | -1.67 | +0.41 | [-0.10, +0.93] | 1.33 |
| country_capital | `label_unreliable` | 146 | -3.02 | +0.27 | -3.29 | [-3.78, -2.82] | -0.09 |
| country_capital | `label_trusted` | 146 | +5.76 | +0.94 | +4.82 | [+4.32, +5.33] | 0.16 |

## How to read this

- **`blankline` is the layout control.** If it moves the margin as much as `tag_document`, E11's effect was whitespace and the document framing is a red herring. If it does not, the markup is doing real work.
- **`tag_passage` versus `tag_document`** separates the syntax from the word. **`label_document`** separates the word from the syntax.
- **The tag × label factorial.** Every name -- document, passage, search_result, trusted_content, untrusted_content, unreliable_source, qzx_block, qzxzxew -- appears once as `<name>` and once as `Name:`, so the bracket's contribution can be read off per name. If brackets matter only for the meaningless names, the bracket and the word are two routes to the same place.
- **`tag_untrusted` is the one to report.** It is the tag whose entire purpose is to mark text as not-to-be-trusted. If deference under it matches `tag_document`, the wrapper is read as *this is source material* and its stated valence is ignored. If it does NOT -- if the tag suppresses deference -- then the model is reading the label's meaning, and the question becomes why the same words fail when they are put in the system prompt instead.
- **`tag_nonsense` is the control for that reading.** `<qzx_block>` carries the same syntax and no meaning. If it behaves like `<document>`, an unfamiliar tag is not inherently suppressive and a low score for `<untrusted_content>` really is about the word. If it behaves like `<untrusted_content>`, then any out-of-distribution tag suppresses deference and the semantic reading is wrong. `tag_trusted` and `tag_unreliable` place the same contrast on a scale. E13 replaces these two strings with a sample of thirty.
- **`tag_empty` splits the structure term itself.** `<qzx_block>` still has a name; `<>` has only the brackets. If `<>` matches `<qzx_block>`, the name contributes nothing and the structural effect is the bracket syntax. If `<>` falls back toward `dashes`, then a tag needs to NAME something -- anything -- and `<qzx_block>`'s +31 was already partly semantic.
- **`bare` versus `assert_r1`** asks whether the wrapper confers source authority or changes the task. `bare` has no source to trust, so if it swings too, the model is switching into reading-comprehension mode rather than deciding whom to believe.
- **`irrelevant_assert_r1` is the priming control.** The same sentence and the same false answer, about a different subject, so the paragraph never claims anything about the queried one. A wrapper that lifts the false answer here is priming a salient token, not getting a claim adopted. The interaction column is the part of the wrapper effect that needs the claim to be about the queried subject.
- Margins are teacher-forced. Rates classify the answer with any reasoning preamble stripped.
