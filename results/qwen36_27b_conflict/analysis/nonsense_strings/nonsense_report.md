# E13: thirty meaningless names — Qwen/Qwen3.6-27B

30 random lower-case names of 8 letters, each as `<name>` and `Name:` around the identical paragraph. ΔM is paired within fact against `inline`. Across strings, CIs are a crossed bootstrap over strings and facts; the tag − label gap is also tested across strings (Wilcoxon signed-rank, one pair per string).

## Distribution over strings

| Relation | Cell | Form | Mean ΔM | 95% CI (crossed) | Median | Range | Strings > 0 | Strings, CI > 0 | Median rate | Strings > 50% | p (across strings) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| element_symbol | `assert_r1` | tag | +3.29 | [+2.93, +3.66] | +3.41 | [+2.0, +4.4] | 30/30 | 30/30 | 0.0% | 0/30 | – |
| element_symbol | `assert_r1` | label | +2.90 | [+2.65, +3.15] | +2.92 | [+2.4, +3.7] | 30/30 | 30/30 | 0.0% | 0/30 | – |
| element_symbol | `assert_r1` | tag_minus_label | +0.39 | [+0.08, +0.70] | +0.57 | [-1.0, +1.7] | 20/30 | – | – | – | 0.012 |
| country_capital | `assert_r1` | tag | +3.66 | [+3.23, +4.11] | +3.78 | [+1.8, +5.0] | 30/30 | 30/30 | 1.4% | 0/30 | – |
| country_capital | `assert_r1` | label | +3.47 | [+3.07, +3.86] | +3.51 | [+2.2, +4.9] | 30/30 | 30/30 | 0.7% | 0/30 | – |
| country_capital | `assert_r1` | tag_minus_label | +0.19 | [-0.12, +0.52] | +0.10 | [-1.4, +1.4] | 15/30 | – | – | – | 0.229 |

## The original strings, placed in the distribution

| Relation | Cell | Wrapper | ΔM | Rate | Percentile among random |
|---|---|---|---:|---:|---:|
| element_symbol | `assert_r1` | `label_gibberish` | +3.07 | 0.8% | 63 |
| element_symbol | `assert_r1` | `label_nonsense` | +2.98 | 0.8% | 60 |
| element_symbol | `assert_r1` | `tag_gibberish` | +3.49 | 0.0% | 53 |
| element_symbol | `assert_r1` | `tag_nonsense` | +4.73 | 3.4% | 100 |
| country_capital | `assert_r1` | `label_gibberish` | +3.19 | 0.7% | 30 |
| country_capital | `assert_r1` | `label_nonsense` | +3.36 | 1.4% | 43 |
| country_capital | `assert_r1` | `tag_gibberish` | +3.58 | 2.7% | 43 |
| country_capital | `assert_r1` | `tag_nonsense` | +3.98 | 4.1% | 67 |

## Exploratory: ΔM against the marker's token count

| Relation | Cell | Form | Strings | Tokens | Spearman ρ | Permutation p |
|---|---|---|---:|---:|---:|---:|
| element_symbol | `assert_r1` | tag | 30 | 5–8 | +0.53 | 0.003 |
| element_symbol | `assert_r1` | label | 30 | 5–7 | -0.26 | 0.161 |
| country_capital | `assert_r1` | tag | 30 | 5–8 | +0.11 | 0.567 |
| country_capital | `assert_r1` | label | 30 | 5–7 | -0.11 | 0.557 |

## Per string

| Relation | Cell | Name | Tag ΔM | Label ΔM | Gap | Tag rate | Label rate |
|---|---|---|---:|---:|---:|---:|---:|
| element_symbol | `assert_r1` | `splyojax` | +4.25 | +3.73 | +0.52 | 0.0% | 1.7% |
| element_symbol | `assert_r1` | `lwzmevlp` | +2.52 | +3.33 | -0.81 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `kzomgbhe` | +2.98 | +2.35 | +0.62 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `mfvyuljs` | +2.39 | +2.67 | -0.28 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `ndeaijrb` | +3.95 | +2.96 | +0.99 | 0.0% | 0.8% |
| element_symbol | `assert_r1` | `yuvfkbtg` | +2.26 | +3.09 | -0.84 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `cbstxmkq` | +4.08 | +2.79 | +1.29 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `gnjrqlha` | +2.99 | +2.77 | +0.22 | 0.0% | 0.8% |
| element_symbol | `assert_r1` | `thrrbsxu` | +2.57 | +3.07 | -0.50 | 0.0% | 0.8% |
| element_symbol | `assert_r1` | `lchczexz` | +2.24 | +3.24 | -1.01 | 0.0% | 0.8% |
| element_symbol | `assert_r1` | `pecbsgpm` | +3.98 | +2.54 | +1.43 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `hxyzqhgy` | +2.44 | +2.90 | -0.45 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `rqblpait` | +3.72 | +2.41 | +1.31 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `hluzemvj` | +2.13 | +2.60 | -0.47 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `ydqwpaxz` | +3.77 | +3.31 | +0.46 | 0.0% | 0.8% |
| element_symbol | `assert_r1` | `skwjlcvc` | +3.64 | +2.94 | +0.70 | 0.0% | 0.8% |
| element_symbol | `assert_r1` | `kvkcfqmi` | +3.44 | +2.46 | +0.98 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `dfcxuxji` | +3.33 | +2.57 | +0.76 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `eqknjdbf` | +4.06 | +2.97 | +1.09 | 1.7% | 0.0% |
| element_symbol | `assert_r1` | `xekriqrx` | +3.10 | +2.72 | +0.38 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `wztioehu` | +2.60 | +3.17 | -0.57 | 0.0% | 0.8% |
| element_symbol | `assert_r1` | `zqucqrkt` | +3.62 | +3.00 | +0.62 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `vhriuhml` | +4.36 | +3.13 | +1.24 | 1.7% | 0.0% |
| element_symbol | `assert_r1` | `lrkwwjxk` | +4.22 | +3.28 | +0.94 | 0.0% | 0.8% |
| element_symbol | `assert_r1` | `apjyugkx` | +4.31 | +2.62 | +1.69 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `mocapkwa` | +3.20 | +3.38 | -0.17 | 0.0% | 0.8% |
| element_symbol | `assert_r1` | `vcbostmq` | +1.96 | +2.72 | -0.76 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `eepmawuq` | +3.60 | +2.52 | +1.08 | 0.0% | 0.0% |
| element_symbol | `assert_r1` | `ylawbxwf` | +3.38 | +3.24 | +0.14 | 0.8% | 0.8% |
| element_symbol | `assert_r1` | `bylwbjto` | +3.51 | +2.39 | +1.12 | 0.0% | 0.0% |
| country_capital | `assert_r1` | `splyojax` | +4.49 | +4.94 | -0.46 | 3.4% | 2.1% |
| country_capital | `assert_r1` | `lwzmevlp` | +2.52 | +3.53 | -1.01 | 1.4% | 0.7% |
| country_capital | `assert_r1` | `kzomgbhe` | +2.76 | +3.12 | -0.36 | 0.0% | 0.0% |
| country_capital | `assert_r1` | `mfvyuljs` | +2.86 | +2.89 | -0.04 | 0.7% | 0.7% |
| country_capital | `assert_r1` | `ndeaijrb` | +4.99 | +3.77 | +1.21 | 2.7% | 0.7% |
| country_capital | `assert_r1` | `yuvfkbtg` | +2.32 | +3.76 | -1.44 | 0.7% | 0.7% |
| country_capital | `assert_r1` | `cbstxmkq` | +4.57 | +3.24 | +1.34 | 3.4% | 1.4% |
| country_capital | `assert_r1` | `gnjrqlha` | +2.91 | +3.63 | -0.72 | 0.7% | 0.7% |
| country_capital | `assert_r1` | `thrrbsxu` | +3.80 | +3.94 | -0.15 | 1.4% | 1.4% |
| country_capital | `assert_r1` | `lchczexz` | +3.39 | +4.18 | -0.79 | 0.7% | 1.4% |
| country_capital | `assert_r1` | `pecbsgpm` | +3.99 | +2.88 | +1.11 | 2.1% | 0.7% |
| country_capital | `assert_r1` | `hxyzqhgy` | +3.09 | +3.24 | -0.14 | 0.7% | 1.4% |
| country_capital | `assert_r1` | `rqblpait` | +3.76 | +2.35 | +1.41 | 1.4% | 0.7% |
| country_capital | `assert_r1` | `hluzemvj` | +3.50 | +3.19 | +0.31 | 0.7% | 0.7% |
| country_capital | `assert_r1` | `ydqwpaxz` | +3.19 | +3.49 | -0.30 | 1.4% | 1.4% |
| country_capital | `assert_r1` | `skwjlcvc` | +4.89 | +3.51 | +1.38 | 2.1% | 0.7% |
| country_capital | `assert_r1` | `kvkcfqmi` | +3.99 | +3.14 | +0.85 | 1.4% | 0.7% |
| country_capital | `assert_r1` | `dfcxuxji` | +4.53 | +3.51 | +1.03 | 3.4% | 0.7% |
| country_capital | `assert_r1` | `eqknjdbf` | +3.01 | +2.20 | +0.81 | 1.4% | 0.7% |
| country_capital | `assert_r1` | `xekriqrx` | +4.41 | +3.93 | +0.48 | 0.7% | 0.7% |
| country_capital | `assert_r1` | `wztioehu` | +3.80 | +4.06 | -0.25 | 1.4% | 0.7% |
| country_capital | `assert_r1` | `zqucqrkt` | +3.29 | +3.88 | -0.59 | 2.1% | 0.7% |
| country_capital | `assert_r1` | `vhriuhml` | +3.85 | +2.75 | +1.10 | 2.7% | 0.7% |
| country_capital | `assert_r1` | `lrkwwjxk` | +4.74 | +4.15 | +0.59 | 2.7% | 1.4% |
| country_capital | `assert_r1` | `apjyugkx` | +3.84 | +3.18 | +0.66 | 2.7% | 0.7% |
| country_capital | `assert_r1` | `mocapkwa` | +4.44 | +3.74 | +0.70 | 2.1% | 0.7% |
| country_capital | `assert_r1` | `vcbostmq` | +1.82 | +2.92 | -1.09 | 0.0% | 0.7% |
| country_capital | `assert_r1` | `eepmawuq` | +3.92 | +3.97 | -0.05 | 1.4% | 0.7% |
| country_capital | `assert_r1` | `ylawbxwf` | +3.75 | +3.79 | -0.05 | 2.1% | 1.4% |
| country_capital | `assert_r1` | `bylwbjto` | +3.51 | +3.28 | +0.24 | 1.4% | 1.4% |

## How to read this

- **The tag row is the claim.** If most strings lift the margin as a tag, "a meaningless tag works" is a property of the bracket syntax around an unfamiliar name, not of `qzx_block`.
- **The gap row is the interaction.** Each string is its own tag/label pair, so a positive gap in most strings means the brackets, not the name, carry the effect for meaningless names. Compare with E12's factorial, where meaningful names barely care about brackets.
- **The references** place `<qzx_block>` and `<qzxzxew>` in the distribution, and should reproduce E12 within run-to-run noise.
- **The token-count table** is exploratory: random letters split into several subword tokens, a word like `document` into one.
