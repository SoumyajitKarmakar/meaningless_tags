# E12: what the wrapper is doing — google/gemma-4-12B-it

The paragraph, claim sentence, question and response constraint are byte-identical in every row. Only the block that encloses the paragraph changes. `delta vs inline` is paired within fact and cell, and bootstrapped over facts. `d>0` counts facts whose margin rose.


| Relation | Wrapper | What it rules out | Cell | n | Context | Margin | Δ vs inline | 95% CI | d>0 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| element_symbol | `inline` | baseline | `assert_r1` | 118 | 0.0% | -27.13 | +0.00 | [+0.00, +0.00] | 0/118 |
| element_symbol | `inline` | baseline | `bare` | 118 | 7.6% | -15.44 | +0.00 | [+0.00, +0.00] | 0/118 |
| element_symbol | `inline` | baseline | `irrelevant_assert_r1` | 118 | 0.0% | -33.37 | +0.00 | [+0.00, +0.00] | 0/118 |
| element_symbol | `blankline` | layout only | `assert_r1` | 118 | 0.0% | -25.83 | +1.30 | [+0.95, +1.67] | 94/118 |
| element_symbol | `blankline` | layout only | `bare` | 118 | 11.0% | -14.16 | +1.28 | [+0.70, +1.92] | 71/118 |
| element_symbol | `blankline` | layout only | `irrelevant_assert_r1` | 118 | 0.0% | -33.62 | -0.25 | [-0.38, -0.11] | 41/118 |
| element_symbol | `dashes` | layout + fence | `assert_r1` | 118 | 23.7% | -9.50 | +17.63 | [+16.12, +19.21] | 117/118 |
| element_symbol | `dashes` | layout + fence | `bare` | 118 | 80.5% | 4.19 | +19.63 | [+18.09, +21.14] | 117/118 |
| element_symbol | `dashes` | layout + fence | `irrelevant_assert_r1` | 118 | 0.0% | -32.82 | +0.55 | [+0.40, +0.69] | 91/118 |
| element_symbol | `quotes` | layout + fence | `assert_r1` | 118 | 5.9% | -18.59 | +8.54 | [+7.31, +9.89] | 117/118 |
| element_symbol | `quotes` | layout + fence | `bare` | 118 | 89.8% | 4.83 | +20.28 | [+18.71, +21.87] | 117/118 |
| element_symbol | `quotes` | layout + fence | `irrelevant_assert_r1` | 118 | 0.0% | -32.48 | +0.89 | [+0.70, +1.08] | 97/118 |
| element_symbol | `tag_document` | E11's condition | `assert_r1` | 118 | 100.0% | 13.89 | +41.02 | [+39.66, +42.42] | 118/118 |
| element_symbol | `tag_document` | E11's condition | `bare` | 118 | 98.3% | 14.29 | +29.73 | [+27.97, +31.33] | 118/118 |
| element_symbol | `tag_document` | E11's condition | `irrelevant_assert_r1` | 118 | 0.0% | -28.84 | +4.53 | [+4.03, +5.05] | 117/118 |
| element_symbol | `tag_passage` | same syntax, different word | `assert_r1` | 118 | 100.0% | 13.11 | +40.24 | [+38.95, +41.55] | 118/118 |
| element_symbol | `tag_passage` | same syntax, different word | `bare` | 118 | 98.3% | 14.11 | +29.55 | [+27.84, +31.17] | 118/118 |
| element_symbol | `tag_passage` | same syntax, different word | `irrelevant_assert_r1` | 118 | 0.0% | -30.53 | +2.85 | [+2.49, +3.21] | 111/118 |
| element_symbol | `tag_search` | the RAG framing, as a tag | `assert_r1` | 118 | 88.1% | 5.83 | +32.96 | [+31.79, +34.18] | 118/118 |
| element_symbol | `tag_search` | the RAG framing, as a tag | `bare` | 118 | 83.1% | 4.68 | +20.12 | [+18.51, +21.59] | 118/118 |
| element_symbol | `tag_search` | the RAG framing, as a tag | `irrelevant_assert_r1` | 118 | 0.0% | -30.10 | +3.28 | [+2.95, +3.59] | 115/118 |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `assert_r1` | 118 | 25.4% | -12.46 | +14.67 | [+12.88, +16.42] | 118/118 |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `bare` | 118 | 92.4% | 6.97 | +22.42 | [+20.97, +23.76] | 118/118 |
| element_symbol | `tag_empty` | bracket syntax, no name at all | `irrelevant_assert_r1` | 118 | 0.0% | -32.25 | +1.12 | [+0.91, +1.33] | 105/118 |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `assert_r1` | 118 | 0.0% | -24.32 | +2.81 | [+1.93, +3.71] | 85/118 |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `bare` | 118 | 31.4% | -6.98 | +8.46 | [+6.62, +10.47] | 93/118 |
| element_symbol | `tag_untrusted` | same syntax, opposite valence | `irrelevant_assert_r1` | 118 | 0.0% | -33.26 | +0.11 | [-0.09, +0.32] | 66/118 |
| element_symbol | `tag_unreliable` | opposite valence, different words | `assert_r1` | 118 | 28.8% | -5.98 | +21.15 | [+19.75, +22.60] | 118/118 |
| element_symbol | `tag_unreliable` | opposite valence, different words | `bare` | 118 | 56.8% | -0.93 | +14.51 | [+12.80, +16.25] | 109/118 |
| element_symbol | `tag_unreliable` | opposite valence, different words | `irrelevant_assert_r1` | 118 | 0.0% | -31.18 | +2.19 | [+1.93, +2.45] | 109/118 |
| element_symbol | `tag_trusted` | same syntax, positive valence | `assert_r1` | 118 | 100.0% | 16.36 | +43.49 | [+42.13, +44.89] | 118/118 |
| element_symbol | `tag_trusted` | same syntax, positive valence | `bare` | 118 | 99.2% | 17.19 | +32.64 | [+30.79, +34.39] | 118/118 |
| element_symbol | `tag_trusted` | same syntax, positive valence | `irrelevant_assert_r1` | 118 | 0.0% | -28.52 | +4.86 | [+4.47, +5.27] | 118/118 |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `assert_r1` | 118 | 78.8% | 4.11 | +31.24 | [+29.80, +32.68] | 118/118 |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `bare` | 118 | 95.8% | 9.28 | +24.72 | [+23.18, +26.14] | 118/118 |
| element_symbol | `tag_nonsense` | same syntax, no meaning at all | `irrelevant_assert_r1` | 118 | 0.0% | -31.78 | +1.59 | [+1.35, +1.81] | 108/118 |
| element_symbol | `tag_gibberish` | no meaning at all | `assert_r1` | 118 | 49.2% | -2.96 | +24.17 | [+22.32, +25.93] | 118/118 |
| element_symbol | `tag_gibberish` | no meaning at all | `bare` | 118 | 64.4% | 0.17 | +15.61 | [+13.95, +17.24] | 114/118 |
| element_symbol | `tag_gibberish` | no meaning at all | `irrelevant_assert_r1` | 118 | 0.0% | -32.16 | +1.22 | [+0.98, +1.45] | 100/118 |
| element_symbol | `label_nonsense` | nonsense label | `assert_r1` | 118 | 35.6% | -6.04 | +21.09 | [+19.41, +22.87] | 118/118 |
| element_symbol | `label_nonsense` | nonsense label | `bare` | 118 | 42.4% | -3.11 | +12.33 | [+10.88, +13.66] | 113/118 |
| element_symbol | `label_nonsense` | nonsense label | `irrelevant_assert_r1` | 118 | 0.0% | -32.50 | +0.87 | [+0.66, +1.07] | 96/118 |
| element_symbol | `label_gibberish` | gibberish label | `assert_r1` | 118 | 6.8% | -19.09 | +8.04 | [+6.87, +9.28] | 114/118 |
| element_symbol | `label_gibberish` | gibberish label | `bare` | 118 | 6.8% | -19.02 | -3.58 | [-4.72, -2.42] | 22/118 |
| element_symbol | `label_gibberish` | gibberish label | `irrelevant_assert_r1` | 118 | 0.0% | -32.89 | +0.49 | [+0.26, +0.69] | 76/118 |
| element_symbol | `label_document` | same word, no markup | `assert_r1` | 118 | 98.3% | 11.41 | +38.54 | [+37.15, +39.93] | 118/118 |
| element_symbol | `label_document` | same word, no markup | `bare` | 118 | 65.3% | 9.13 | +24.57 | [+22.97, +26.04] | 118/118 |
| element_symbol | `label_document` | same word, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -29.74 | +3.63 | [+3.26, +4.01] | 116/118 |
| element_symbol | `label_passage` | <passage>'s word, no markup | `assert_r1` | 118 | 100.0% | 9.55 | +36.68 | [+35.44, +37.98] | 118/118 |
| element_symbol | `label_passage` | <passage>'s word, no markup | `bare` | 118 | 62.7% | 10.60 | +26.05 | [+24.41, +27.63] | 118/118 |
| element_symbol | `label_passage` | <passage>'s word, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -32.02 | +1.36 | [+1.12, +1.58] | 105/118 |
| element_symbol | `label_search` | the RAG framing | `assert_r1` | 118 | 100.0% | 12.94 | +40.07 | [+38.72, +41.40] | 118/118 |
| element_symbol | `label_search` | the RAG framing | `bare` | 118 | 66.9% | 9.33 | +24.77 | [+23.12, +26.36] | 117/118 |
| element_symbol | `label_search` | the RAG framing | `irrelevant_assert_r1` | 118 | 0.0% | -28.38 | +4.99 | [+4.55, +5.44] | 118/118 |
| element_symbol | `label_untrusted` | opposite valence, no markup | `assert_r1` | 118 | 0.0% | -21.44 | +5.69 | [+4.78, +6.65] | 109/118 |
| element_symbol | `label_untrusted` | opposite valence, no markup | `bare` | 118 | 13.6% | -9.87 | +5.57 | [+4.08, +7.02] | 98/118 |
| element_symbol | `label_untrusted` | opposite valence, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -32.62 | +0.75 | [+0.54, +0.96] | 89/118 |
| element_symbol | `label_unreliable` | <unreliable_source>'s words, no markup | `assert_r1` | 118 | 0.8% | -22.43 | +4.70 | [+3.83, +5.56] | 109/118 |
| element_symbol | `label_unreliable` | <unreliable_source>'s words, no markup | `bare` | 118 | 0.8% | -16.88 | -1.43 | [-2.78, -0.17] | 48/118 |
| element_symbol | `label_unreliable` | <unreliable_source>'s words, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -32.68 | +0.69 | [+0.48, +0.89] | 88/118 |
| element_symbol | `label_trusted` | <trusted_content>'s words, no markup | `assert_r1` | 118 | 100.0% | 16.03 | +43.16 | [+41.79, +44.58] | 118/118 |
| element_symbol | `label_trusted` | <trusted_content>'s words, no markup | `bare` | 118 | 76.3% | 15.69 | +31.13 | [+29.33, +32.78] | 118/118 |
| element_symbol | `label_trusted` | <trusted_content>'s words, no markup | `irrelevant_assert_r1` | 118 | 0.0% | -24.15 | +9.23 | [+8.57, +9.90] | 118/118 |
| country_capital | `inline` | baseline | `assert_r1` | 143 | 0.0% | -28.10 | +0.00 | [+0.00, +0.00] | 0/143 |
| country_capital | `inline` | baseline | `bare` | 143 | 24.5% | -9.59 | +0.00 | [+0.00, +0.00] | 0/143 |
| country_capital | `inline` | baseline | `irrelevant_assert_r1` | 143 | 0.7% | -32.99 | +0.00 | [+0.00, +0.00] | 0/143 |
| country_capital | `blankline` | layout only | `assert_r1` | 143 | 0.0% | -24.23 | +3.87 | [+3.49, +4.25] | 143/143 |
| country_capital | `blankline` | layout only | `bare` | 143 | 33.6% | -4.61 | +4.98 | [+4.43, +5.57] | 133/143 |
| country_capital | `blankline` | layout only | `irrelevant_assert_r1` | 143 | 0.7% | -32.70 | +0.29 | [+0.09, +0.54] | 77/143 |
| country_capital | `dashes` | layout + fence | `assert_r1` | 143 | 32.9% | -4.88 | +23.22 | [+21.87, +24.54] | 143/143 |
| country_capital | `dashes` | layout + fence | `bare` | 143 | 67.1% | 4.82 | +14.41 | [+13.25, +15.60] | 143/143 |
| country_capital | `dashes` | layout + fence | `irrelevant_assert_r1` | 143 | 2.1% | -31.13 | +1.86 | [+1.34, +2.40] | 118/143 |
| country_capital | `quotes` | layout + fence | `assert_r1` | 143 | 53.8% | -1.65 | +26.45 | [+25.14, +27.71] | 143/143 |
| country_capital | `quotes` | layout + fence | `bare` | 143 | 75.5% | 8.53 | +18.12 | [+16.80, +19.45] | 143/143 |
| country_capital | `quotes` | layout + fence | `irrelevant_assert_r1` | 143 | 2.1% | -30.09 | +2.90 | [+2.32, +3.52] | 127/143 |
| country_capital | `tag_document` | E11's condition | `assert_r1` | 143 | 100.0% | 12.61 | +40.70 | [+39.59, +41.83] | 143/143 |
| country_capital | `tag_document` | E11's condition | `bare` | 143 | 100.0% | 16.48 | +26.08 | [+24.67, +27.53] | 143/143 |
| country_capital | `tag_document` | E11's condition | `irrelevant_assert_r1` | 143 | 1.4% | -21.91 | +11.08 | [+9.98, +12.22] | 141/143 |
| country_capital | `tag_passage` | same syntax, different word | `assert_r1` | 143 | 100.0% | 10.66 | +38.76 | [+37.62, +39.84] | 143/143 |
| country_capital | `tag_passage` | same syntax, different word | `bare` | 143 | 100.0% | 16.21 | +25.81 | [+24.37, +27.30] | 143/143 |
| country_capital | `tag_passage` | same syntax, different word | `irrelevant_assert_r1` | 143 | 2.1% | -20.13 | +12.86 | [+11.73, +14.09] | 141/143 |
| country_capital | `tag_search` | the RAG framing, as a tag | `assert_r1` | 143 | 76.9% | 3.87 | +31.97 | [+30.90, +33.04] | 143/143 |
| country_capital | `tag_search` | the RAG framing, as a tag | `bare` | 143 | 97.2% | 7.76 | +17.35 | [+15.95, +18.78] | 143/143 |
| country_capital | `tag_search` | the RAG framing, as a tag | `irrelevant_assert_r1` | 143 | 2.1% | -26.52 | +6.47 | [+5.68, +7.26] | 139/143 |
| country_capital | `tag_empty` | bracket syntax, no name at all | `assert_r1` | 143 | 62.9% | 0.77 | +28.86 | [+27.40, +30.27] | 143/143 |
| country_capital | `tag_empty` | bracket syntax, no name at all | `bare` | 143 | 94.4% | 8.24 | +17.83 | [+16.56, +19.14] | 143/143 |
| country_capital | `tag_empty` | bracket syntax, no name at all | `irrelevant_assert_r1` | 143 | 2.1% | -30.06 | +2.93 | [+2.38, +3.50] | 135/143 |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `assert_r1` | 143 | 0.0% | -27.33 | +0.76 | [+0.29, +1.23] | 96/143 |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `bare` | 143 | 3.5% | -17.63 | -8.04 | [-9.74, -6.36] | 36/143 |
| country_capital | `tag_untrusted` | same syntax, opposite valence | `irrelevant_assert_r1` | 143 | 0.7% | -34.43 | -1.44 | [-1.92, -1.00] | 43/143 |
| country_capital | `tag_unreliable` | opposite valence, different words | `assert_r1` | 143 | 0.7% | -21.73 | +6.36 | [+5.70, +7.05] | 143/143 |
| country_capital | `tag_unreliable` | opposite valence, different words | `bare` | 143 | 2.1% | -15.50 | -5.90 | [-7.80, -4.14] | 47/143 |
| country_capital | `tag_unreliable` | opposite valence, different words | `irrelevant_assert_r1` | 143 | 0.7% | -32.42 | +0.57 | [+0.06, +1.08] | 94/143 |
| country_capital | `tag_trusted` | same syntax, positive valence | `assert_r1` | 143 | 100.0% | 17.01 | +45.10 | [+43.99, +46.27] | 143/143 |
| country_capital | `tag_trusted` | same syntax, positive valence | `bare` | 143 | 100.0% | 18.67 | +28.26 | [+26.76, +29.80] | 143/143 |
| country_capital | `tag_trusted` | same syntax, positive valence | `irrelevant_assert_r1` | 143 | 1.4% | -25.57 | +7.42 | [+6.47, +8.35] | 141/143 |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `assert_r1` | 143 | 74.8% | 2.88 | +30.98 | [+29.65, +32.28] | 143/143 |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `bare` | 143 | 78.3% | 3.96 | +13.55 | [+12.25, +14.86] | 141/143 |
| country_capital | `tag_nonsense` | same syntax, no meaning at all | `irrelevant_assert_r1` | 143 | 2.1% | -31.18 | +1.81 | [+1.29, +2.35] | 121/143 |
| country_capital | `tag_gibberish` | no meaning at all | `assert_r1` | 143 | 36.4% | -4.44 | +23.66 | [+22.04, +25.16] | 143/143 |
| country_capital | `tag_gibberish` | no meaning at all | `bare` | 143 | 23.8% | -8.08 | +1.51 | [+0.45, +2.60] | 81/143 |
| country_capital | `tag_gibberish` | no meaning at all | `irrelevant_assert_r1` | 143 | 2.1% | -29.95 | +3.04 | [+2.44, +3.69] | 134/143 |
| country_capital | `label_nonsense` | nonsense label | `assert_r1` | 143 | 3.5% | -20.30 | +7.79 | [+6.72, +8.91] | 137/143 |
| country_capital | `label_nonsense` | nonsense label | `bare` | 143 | 13.3% | -12.16 | -2.57 | [-3.53, -1.60] | 43/143 |
| country_capital | `label_nonsense` | nonsense label | `irrelevant_assert_r1` | 143 | 0.7% | -31.21 | +1.78 | [+1.36, +2.24] | 130/143 |
| country_capital | `label_gibberish` | gibberish label | `assert_r1` | 143 | 0.0% | -24.02 | +4.08 | [+3.39, +4.79] | 134/143 |
| country_capital | `label_gibberish` | gibberish label | `bare` | 143 | 5.6% | -19.87 | -10.28 | [-11.57, -9.07] | 3/143 |
| country_capital | `label_gibberish` | gibberish label | `irrelevant_assert_r1` | 143 | 0.7% | -31.92 | +1.07 | [+0.71, +1.45] | 108/143 |
| country_capital | `label_document` | same word, no markup | `assert_r1` | 143 | 99.3% | 10.29 | +38.38 | [+37.28, +39.51] | 143/143 |
| country_capital | `label_document` | same word, no markup | `bare` | 143 | 88.8% | 17.98 | +27.57 | [+26.11, +29.12] | 143/143 |
| country_capital | `label_document` | same word, no markup | `irrelevant_assert_r1` | 143 | 0.7% | -28.39 | +4.60 | [+3.94, +5.27] | 137/143 |
| country_capital | `label_passage` | <passage>'s word, no markup | `assert_r1` | 143 | 100.0% | 12.91 | +41.00 | [+39.89, +42.10] | 143/143 |
| country_capital | `label_passage` | <passage>'s word, no markup | `bare` | 143 | 86.7% | 16.96 | +26.55 | [+25.16, +27.98] | 143/143 |
| country_capital | `label_passage` | <passage>'s word, no markup | `irrelevant_assert_r1` | 143 | 2.1% | -24.76 | +8.23 | [+7.20, +9.31] | 141/143 |
| country_capital | `label_search` | the RAG framing | `assert_r1` | 143 | 100.0% | 13.37 | +41.46 | [+40.36, +42.57] | 143/143 |
| country_capital | `label_search` | the RAG framing | `bare` | 143 | 89.5% | 14.77 | +24.36 | [+22.93, +25.78] | 143/143 |
| country_capital | `label_search` | the RAG framing | `irrelevant_assert_r1` | 143 | 2.1% | -24.72 | +8.27 | [+7.25, +9.36] | 143/143 |
| country_capital | `label_untrusted` | opposite valence, no markup | `assert_r1` | 143 | 0.7% | -19.29 | +8.81 | [+8.01, +9.59] | 142/143 |
| country_capital | `label_untrusted` | opposite valence, no markup | `bare` | 143 | 18.2% | -11.23 | -1.63 | [-2.84, -0.40] | 64/143 |
| country_capital | `label_untrusted` | opposite valence, no markup | `irrelevant_assert_r1` | 143 | 0.7% | -32.62 | +0.36 | [+0.03, +0.71] | 90/143 |
| country_capital | `label_unreliable` | <unreliable_source>'s words, no markup | `assert_r1` | 143 | 0.0% | -30.16 | -2.07 | [-2.51, -1.68] | 27/143 |
| country_capital | `label_unreliable` | <unreliable_source>'s words, no markup | `bare` | 143 | 0.7% | -25.41 | -15.82 | [-17.58, -14.12] | 2/143 |
| country_capital | `label_unreliable` | <unreliable_source>'s words, no markup | `irrelevant_assert_r1` | 143 | 0.7% | -33.85 | -0.86 | [-1.25, -0.45] | 49/143 |
| country_capital | `label_trusted` | <trusted_content>'s words, no markup | `assert_r1` | 143 | 100.0% | 13.98 | +42.08 | [+40.93, +43.18] | 143/143 |
| country_capital | `label_trusted` | <trusted_content>'s words, no markup | `bare` | 143 | 93.0% | 19.60 | +29.20 | [+27.66, +30.75] | 143/143 |
| country_capital | `label_trusted` | <trusted_content>'s words, no markup | `irrelevant_assert_r1` | 143 | 2.1% | -19.26 | +13.73 | [+12.56, +15.00] | 142/143 |

## Relevance: the same wrapper around a paragraph about another subject

- element_symbol, unwrapped: relevant − irrelevant = +6.24 [+5.48, +7.00], 113/118 facts > 0.
- country_capital, unwrapped: relevant − irrelevant = +4.89 [+3.98, +5.88], 128/143 facts > 0.

| Relation | Wrapper | n | Δ relevant | Δ irrelevant | Interaction | 95% CI | Irrelevant / relevant |
|---|---|---:|---:|---:|---:|---:|---:|
| element_symbol | `blankline` | 118 | +1.30 | -0.25 | +1.55 | [+1.23, +1.88] | -0.19 |
| element_symbol | `dashes` | 118 | +17.63 | +0.55 | +17.08 | [+15.60, +18.63] | 0.03 |
| element_symbol | `quotes` | 118 | +8.54 | +0.89 | +7.65 | [+6.42, +8.98] | 0.10 |
| element_symbol | `tag_document` | 118 | +41.02 | +4.53 | +36.48 | [+35.10, +37.90] | 0.11 |
| element_symbol | `tag_passage` | 118 | +40.24 | +2.85 | +37.39 | [+36.10, +38.69] | 0.07 |
| element_symbol | `tag_search` | 118 | +32.96 | +3.28 | +29.68 | [+28.48, +30.92] | 0.10 |
| element_symbol | `tag_empty` | 118 | +14.67 | +1.12 | +13.55 | [+11.80, +15.30] | 0.08 |
| element_symbol | `tag_untrusted` | 118 | +2.81 | +0.11 | +2.70 | [+1.84, +3.58] | 0.04 |
| element_symbol | `tag_unreliable` | 118 | +21.15 | +2.19 | +18.96 | [+17.57, +20.35] | 0.10 |
| element_symbol | `tag_trusted` | 118 | +43.49 | +4.86 | +38.63 | [+37.22, +40.06] | 0.11 |
| element_symbol | `tag_nonsense` | 118 | +31.24 | +1.59 | +29.65 | [+28.21, +31.10] | 0.05 |
| element_symbol | `tag_gibberish` | 118 | +24.17 | +1.22 | +22.95 | [+21.16, +24.69] | 0.05 |
| element_symbol | `label_nonsense` | 118 | +21.09 | +0.87 | +20.22 | [+18.51, +22.01] | 0.04 |
| element_symbol | `label_gibberish` | 118 | +8.04 | +0.49 | +7.55 | [+6.41, +8.80] | 0.06 |
| element_symbol | `label_document` | 118 | +38.54 | +3.63 | +34.91 | [+33.52, +36.28] | 0.09 |
| element_symbol | `label_passage` | 118 | +36.68 | +1.36 | +35.33 | [+34.12, +36.60] | 0.04 |
| element_symbol | `label_search` | 118 | +40.07 | +4.99 | +35.08 | [+33.65, +36.49] | 0.12 |
| element_symbol | `label_untrusted` | 118 | +5.69 | +0.75 | +4.94 | [+4.04, +5.92] | 0.13 |
| element_symbol | `label_unreliable` | 118 | +4.70 | +0.69 | +4.00 | [+3.17, +4.87] | 0.15 |
| element_symbol | `label_trusted` | 118 | +43.16 | +9.23 | +33.93 | [+32.35, +35.44] | 0.21 |
| country_capital | `blankline` | 143 | +3.87 | +0.29 | +3.58 | [+3.10, +4.04] | 0.07 |
| country_capital | `dashes` | 143 | +23.22 | +1.86 | +21.36 | [+19.97, +22.74] | 0.08 |
| country_capital | `quotes` | 143 | +26.45 | +2.90 | +23.55 | [+22.14, +24.98] | 0.11 |
| country_capital | `tag_document` | 143 | +40.70 | +11.08 | +29.62 | [+28.13, +31.07] | 0.27 |
| country_capital | `tag_passage` | 143 | +38.76 | +12.86 | +25.90 | [+24.48, +27.33] | 0.33 |
| country_capital | `tag_search` | 143 | +31.97 | +6.47 | +25.50 | [+24.31, +26.73] | 0.20 |
| country_capital | `tag_empty` | 143 | +28.86 | +2.93 | +25.93 | [+24.33, +27.52] | 0.10 |
| country_capital | `tag_untrusted` | 143 | +0.76 | -1.44 | +2.21 | [+1.58, +2.84] | -1.89 |
| country_capital | `tag_unreliable` | 143 | +6.36 | +0.57 | +5.79 | [+5.02, +6.59] | 0.09 |
| country_capital | `tag_trusted` | 143 | +45.10 | +7.42 | +37.68 | [+36.24, +39.16] | 0.16 |
| country_capital | `tag_nonsense` | 143 | +30.98 | +1.81 | +29.17 | [+27.77, +30.52] | 0.06 |
| country_capital | `tag_gibberish` | 143 | +23.66 | +3.04 | +20.62 | [+18.84, +22.33] | 0.13 |
| country_capital | `label_nonsense` | 143 | +7.79 | +1.78 | +6.01 | [+4.80, +7.24] | 0.23 |
| country_capital | `label_gibberish` | 143 | +4.08 | +1.07 | +3.00 | [+2.25, +3.81] | 0.26 |
| country_capital | `label_document` | 143 | +38.38 | +4.60 | +33.78 | [+32.54, +35.10] | 0.12 |
| country_capital | `label_passage` | 143 | +41.00 | +8.23 | +32.77 | [+31.34, +34.24] | 0.20 |
| country_capital | `label_search` | 143 | +41.46 | +8.27 | +33.19 | [+31.81, +34.63] | 0.20 |
| country_capital | `label_untrusted` | 143 | +8.81 | +0.36 | +8.44 | [+7.62, +9.28] | 0.04 |
| country_capital | `label_unreliable` | 143 | -2.07 | -0.86 | -1.20 | [-1.77, -0.69] | 0.42 |
| country_capital | `label_trusted` | 143 | +42.08 | +13.73 | +28.35 | [+26.88, +29.83] | 0.33 |

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
