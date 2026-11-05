# E13: thirty meaningless names — google/gemma-4-12B-it

30 random lower-case names of 8 letters, each as `<name>` and `Name:` around the identical paragraph. ΔM is paired within fact against `inline`. Across strings, CIs are a crossed bootstrap over strings and facts; the tag − label gap is also tested across strings (Wilcoxon signed-rank, one pair per string).

## Distribution over strings

| Relation | Cell | Form | Mean ΔM | 95% CI (crossed) | Median | Range | Strings > 0 | Strings, CI > 0 | Median rate | Strings > 50% | p (across strings) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| element_symbol | `assert_r1` | tag | +23.35 | [+20.61, +25.95] | +23.53 | [+10.9, +34.3] | 30/30 | 30/30 | 46.6% | 14/30 | – |
| element_symbol | `assert_r1` | label | +10.22 | [+8.56, +11.90] | +9.92 | [+5.1, +16.7] | 30/30 | 30/30 | 9.3% | 0/30 | – |
| element_symbol | `assert_r1` | tag_minus_label | +13.13 | [+10.79, +15.39] | +12.75 | [+1.3, +22.8] | 30/30 | – | – | – | 1.9e-09 |
| country_capital | `assert_r1` | tag | +19.81 | [+18.02, +21.71] | +19.98 | [+13.1, +26.2] | 30/30 | 30/30 | 24.5% | 1/30 | – |
| country_capital | `assert_r1` | label | +4.64 | [+3.75, +5.59] | +4.44 | [+1.6, +10.4] | 30/30 | 30/30 | 0.0% | 0/30 | – |
| country_capital | `assert_r1` | tag_minus_label | +15.17 | [+13.79, +16.65] | +15.35 | [+9.6, +22.4] | 30/30 | – | – | – | 1.9e-09 |

## The original strings, placed in the distribution

| Relation | Cell | Wrapper | ΔM | Rate | Percentile among random |
|---|---|---|---:|---:|---:|
| element_symbol | `assert_r1` | `label_gibberish` | +7.96 | 7.6% | 23 |
| element_symbol | `assert_r1` | `label_nonsense` | +21.01 | 36.4% | 100 |
| element_symbol | `assert_r1` | `tag_gibberish` | +24.08 | 49.2% | 53 |
| element_symbol | `assert_r1` | `tag_nonsense` | +31.14 | 78.8% | 87 |
| country_capital | `assert_r1` | `label_gibberish` | +4.07 | 0.0% | 40 |
| country_capital | `assert_r1` | `label_nonsense` | +7.76 | 3.5% | 97 |
| country_capital | `assert_r1` | `tag_gibberish` | +23.69 | 36.4% | 90 |
| country_capital | `assert_r1` | `tag_nonsense` | +31.01 | 74.8% | 100 |

## Exploratory: ΔM against the marker's token count

| Relation | Cell | Form | Strings | Tokens | Spearman ρ | Permutation p |
|---|---|---|---:|---:|---:|---:|
| element_symbol | `assert_r1` | tag | 30 | 5–7 | -0.50 | 0.005 |
| element_symbol | `assert_r1` | label | 30 | 5–7 | -0.37 | 0.045 |
| country_capital | `assert_r1` | tag | 30 | 5–7 | -0.19 | 0.309 |
| country_capital | `assert_r1` | label | 30 | 5–7 | -0.42 | 0.023 |

## Per string

| Relation | Cell | Name | Tag ΔM | Label ΔM | Gap | Tag rate | Label rate |
|---|---|---|---:|---:|---:|---:|---:|
| element_symbol | `assert_r1` | `splyojax` | +26.77 | +15.66 | +11.10 | 61.9% | 20.3% |
| element_symbol | `assert_r1` | `lwzmevlp` | +13.40 | +7.44 | +5.96 | 22.0% | 4.2% |
| element_symbol | `assert_r1` | `kzomgbhe` | +16.96 | +9.43 | +7.54 | 30.5% | 9.3% |
| element_symbol | `assert_r1` | `mfvyuljs` | +20.43 | +9.71 | +10.72 | 36.4% | 6.8% |
| element_symbol | `assert_r1` | `ndeaijrb` | +20.75 | +5.61 | +15.14 | 39.0% | 2.5% |
| element_symbol | `assert_r1` | `yuvfkbtg` | +22.16 | +11.43 | +10.73 | 44.1% | 10.2% |
| element_symbol | `assert_r1` | `cbstxmkq` | +28.32 | +9.84 | +18.48 | 66.1% | 9.3% |
| element_symbol | `assert_r1` | `gnjrqlha` | +17.75 | +7.19 | +10.56 | 35.6% | 5.9% |
| element_symbol | `assert_r1` | `thrrbsxu` | +29.40 | +12.56 | +16.83 | 66.9% | 11.0% |
| element_symbol | `assert_r1` | `lchczexz` | +12.41 | +7.79 | +4.61 | 20.3% | 5.9% |
| element_symbol | `assert_r1` | `pecbsgpm` | +28.24 | +5.43 | +22.81 | 66.1% | 4.2% |
| element_symbol | `assert_r1` | `hxyzqhgy` | +25.71 | +11.55 | +14.16 | 55.1% | 11.0% |
| element_symbol | `assert_r1` | `rqblpait` | +28.04 | +9.62 | +18.42 | 63.6% | 6.8% |
| element_symbol | `assert_r1` | `hluzemvj` | +10.86 | +9.51 | +1.35 | 14.4% | 7.6% |
| element_symbol | `assert_r1` | `ydqwpaxz` | +13.82 | +10.00 | +3.82 | 28.0% | 9.3% |
| element_symbol | `assert_r1` | `skwjlcvc` | +22.17 | +13.57 | +8.60 | 44.1% | 14.4% |
| element_symbol | `assert_r1` | `kvkcfqmi` | +31.42 | +8.66 | +22.76 | 78.0% | 7.6% |
| element_symbol | `assert_r1` | `dfcxuxji` | +32.91 | +12.86 | +20.05 | 85.6% | 11.9% |
| element_symbol | `assert_r1` | `eqknjdbf` | +22.26 | +11.24 | +11.02 | 46.6% | 11.9% |
| element_symbol | `assert_r1` | `xekriqrx` | +26.48 | +5.06 | +21.42 | 55.9% | 3.4% |
| element_symbol | `assert_r1` | `wztioehu` | +23.61 | +14.76 | +8.85 | 46.6% | 20.3% |
| element_symbol | `assert_r1` | `zqucqrkt` | +17.30 | +5.37 | +11.93 | 28.0% | 4.2% |
| element_symbol | `assert_r1` | `vhriuhml` | +32.91 | +11.52 | +21.39 | 83.9% | 10.2% |
| element_symbol | `assert_r1` | `lrkwwjxk` | +12.46 | +10.02 | +2.43 | 21.2% | 9.3% |
| element_symbol | `assert_r1` | `apjyugkx` | +28.17 | +9.43 | +18.75 | 63.6% | 7.6% |
| element_symbol | `assert_r1` | `mocapkwa` | +34.26 | +16.67 | +17.59 | 92.4% | 20.3% |
| element_symbol | `assert_r1` | `vcbostmq` | +30.17 | +13.67 | +16.51 | 72.9% | 16.1% |
| element_symbol | `assert_r1` | `eepmawuq` | +26.49 | +12.91 | +13.58 | 60.2% | 13.6% |
| element_symbol | `assert_r1` | `ylawbxwf` | +23.45 | +8.06 | +15.39 | 46.6% | 5.9% |
| element_symbol | `assert_r1` | `bylwbjto` | +21.42 | +10.04 | +11.37 | 44.1% | 9.3% |
| country_capital | `assert_r1` | `splyojax` | +22.93 | +7.53 | +15.40 | 32.9% | 0.7% |
| country_capital | `assert_r1` | `lwzmevlp` | +15.64 | +3.25 | +12.38 | 11.2% | 0.0% |
| country_capital | `assert_r1` | `kzomgbhe` | +17.85 | +4.06 | +13.79 | 21.7% | 0.0% |
| country_capital | `assert_r1` | `mfvyuljs` | +18.64 | +2.06 | +16.57 | 16.1% | 0.0% |
| country_capital | `assert_r1` | `ndeaijrb` | +13.05 | +1.57 | +11.48 | 6.3% | 0.0% |
| country_capital | `assert_r1` | `yuvfkbtg` | +15.98 | +3.42 | +12.56 | 11.9% | 0.0% |
| country_capital | `assert_r1` | `cbstxmkq` | +23.45 | +5.19 | +18.26 | 32.2% | 0.7% |
| country_capital | `assert_r1` | `gnjrqlha` | +15.53 | +2.87 | +12.66 | 12.6% | 0.0% |
| country_capital | `assert_r1` | `thrrbsxu` | +19.78 | +4.48 | +15.30 | 21.0% | 0.0% |
| country_capital | `assert_r1` | `lchczexz` | +17.57 | +4.41 | +13.16 | 18.2% | 0.0% |
| country_capital | `assert_r1` | `pecbsgpm` | +22.02 | +3.36 | +18.66 | 28.7% | 0.0% |
| country_capital | `assert_r1` | `hxyzqhgy` | +26.21 | +5.67 | +20.54 | 50.3% | 0.7% |
| country_capital | `assert_r1` | `rqblpait` | +16.35 | +4.51 | +11.83 | 14.7% | 0.7% |
| country_capital | `assert_r1` | `hluzemvj` | +13.87 | +2.82 | +11.04 | 11.2% | 0.0% |
| country_capital | `assert_r1` | `ydqwpaxz` | +16.14 | +4.26 | +11.88 | 12.6% | 0.7% |
| country_capital | `assert_r1` | `skwjlcvc` | +20.18 | +4.47 | +15.71 | 23.8% | 0.7% |
| country_capital | `assert_r1` | `kvkcfqmi` | +23.09 | +5.46 | +17.63 | 33.6% | 0.0% |
| country_capital | `assert_r1` | `dfcxuxji` | +24.76 | +10.44 | +14.31 | 37.8% | 5.6% |
| country_capital | `assert_r1` | `eqknjdbf` | +21.30 | +6.40 | +14.91 | 30.1% | 0.7% |
| country_capital | `assert_r1` | `xekriqrx` | +14.71 | +5.13 | +9.58 | 12.6% | 0.0% |
| country_capital | `assert_r1` | `wztioehu` | +23.27 | +5.72 | +17.55 | 30.1% | 0.0% |
| country_capital | `assert_r1` | `zqucqrkt` | +21.40 | +3.79 | +17.62 | 25.9% | 0.0% |
| country_capital | `assert_r1` | `vhriuhml` | +25.98 | +3.60 | +22.38 | 43.4% | 0.0% |
| country_capital | `assert_r1` | `lrkwwjxk` | +19.75 | +3.76 | +15.99 | 25.2% | 0.0% |
| country_capital | `assert_r1` | `apjyugkx` | +22.58 | +6.36 | +16.22 | 30.8% | 0.7% |
| country_capital | `assert_r1` | `mocapkwa` | +22.35 | +6.50 | +15.85 | 35.0% | 0.7% |
| country_capital | `assert_r1` | `vcbostmq` | +23.09 | +6.55 | +16.54 | 32.2% | 0.7% |
| country_capital | `assert_r1` | `eepmawuq` | +16.94 | +4.21 | +12.73 | 15.4% | 0.0% |
| country_capital | `assert_r1` | `ylawbxwf` | +19.28 | +4.64 | +14.64 | 21.0% | 0.0% |
| country_capital | `assert_r1` | `bylwbjto` | +20.72 | +2.84 | +17.88 | 25.9% | 0.0% |

## How to read this

- **The tag row is the claim.** If most strings lift the margin as a tag, "a meaningless tag works" is a property of the bracket syntax around an unfamiliar name, not of `qzx_block`.
- **The gap row is the interaction.** Each string is its own tag/label pair, so a positive gap in most strings means the brackets, not the name, carry the effect for meaningless names. Compare with E12's factorial, where meaningful names barely care about brackets.
- **The references** place `<qzx_block>` and `<qzxzxew>` in the distribution, and should reproduce E12 within run-to-run noise.
- **The token-count table** is exploratory: random letters split into several subword tokens, a word like `document` into one.
