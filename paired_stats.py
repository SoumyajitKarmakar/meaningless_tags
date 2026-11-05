#!/usr/bin/env python3
"""Paired statistics shared by the analysis scripts.

Every experiment measures the same facts under several conditions, so every
comparison here is paired within fact:

* a paragraph rate or a mean margin gets a percentile bootstrap CI over facts.
  A rate also gets an exact Clopper-Pearson interval, because the bootstrap
  collapses to a single point at 0% and 100%, which is where many cells sit;
* a rate contrast gets an exact McNemar test on the discordant facts;
* a margin contrast (ΔM) gets a paired bootstrap CI, a Wilcoxon signed-rank
  test, and per-fact sign counts with an exact sign test;
* a cross-model rank agreement gets a permutation p-value;
* a mean over a SAMPLE of wrapper strings gets a crossed bootstrap that
  resamples strings and facts together, so the interval covers both.

numpy is required. scipy is imported lazily, only by the functions that need it,
so the figure script can use the numpy-only helpers without it.
"""

from __future__ import annotations

import functools
import math
from typing import Any, Sequence

import numpy as np


DEFAULT_REPLICATES = 10_000
DEFAULT_PERMUTATIONS = 100_000
DEFAULT_SEED = 20260816
ALPHA = 0.05


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


@functools.lru_cache(maxsize=16)
def _bootstrap_indices(n: int, replicates: int, seed: int) -> np.ndarray:
    """One read-only (replicates x n) matrix of resampled positions.

    Cached per (n, replicates, seed), so every statistic over the same number
    of facts reuses the same draws. Each interval is still an ordinary
    bootstrap; they just share random numbers.
    """
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, n, size=(replicates, n), dtype=np.int32)
    indices.setflags(write=False)
    return indices


def percentile_interval(draws: Any, alpha: float = ALPHA) -> tuple[float, float]:
    values = np.asarray(draws, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return float("nan"), float("nan")
    low, high = np.quantile(values, [alpha / 2, 1 - alpha / 2])
    return float(low), float(high)


def bootstrap_mean_ci(
    values: Any,
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
    alpha: float = ALPHA,
) -> tuple[float, float]:
    """Percentile CI of the mean, resampling units (facts) with replacement.

    With one value per fact this is exactly the cluster bootstrap the
    experiment scripts use, and for a paired difference it is the paired
    bootstrap: pass the per-fact differences.
    """
    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise ValueError("bootstrap_mean_ci expects a 1-D array, one value per unit")
    if array.size == 0:
        return float("nan"), float("nan")
    if not np.all(np.isfinite(array)):
        raise ValueError("bootstrap_mean_ci received a non-finite value")
    if array.size > 2000:
        # Far more units than any per-fact analysis has; draw in chunks rather
        # than caching a very large index matrix.
        rng = np.random.default_rng(seed)
        means = np.empty(int(replicates), dtype=float)
        for start in range(0, int(replicates), 500):
            size = min(500, int(replicates) - start)
            picked = rng.integers(0, array.size, size=(size, array.size))
            means[start : start + size] = array[picked].mean(axis=1)
        return percentile_interval(means, alpha)
    indices = _bootstrap_indices(int(array.size), int(replicates), int(seed))
    return percentile_interval(array[indices].mean(axis=1), alpha)


def crossed_bootstrap_mean_ci(
    matrix: Any,
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
    alpha: float = ALPHA,
) -> tuple[float, float]:
    """Percentile CI for the grand mean of a (strings x facts) matrix.

    Rows and columns are resampled independently in every replicate, so the
    interval reflects both which strings happened to be sampled and which
    facts. Resampling with replacement is the same as drawing multinomial
    weights, which keeps each replicate a single matrix product.
    """
    values = np.asarray(matrix, dtype=float)
    if values.ndim != 2 or values.size == 0:
        return float("nan"), float("nan")
    if not np.all(np.isfinite(values)):
        raise ValueError("crossed_bootstrap_mean_ci needs a complete, finite matrix")
    rows, columns = values.shape
    rng = np.random.default_rng(seed)
    draws = np.empty(int(replicates), dtype=float)
    chunk = 2000
    for start in range(0, int(replicates), chunk):
        size = min(chunk, int(replicates) - start)
        row_weights = rng.multinomial(rows, np.full(rows, 1.0 / rows), size=size)
        column_weights = rng.multinomial(columns, np.full(columns, 1.0 / columns), size=size)
        draws[start : start + size] = (
            (row_weights @ values) * column_weights
        ).sum(axis=1) / (rows * columns)
    return percentile_interval(draws, alpha)


# ---------------------------------------------------------------------------
# Exact and rank tests
# ---------------------------------------------------------------------------


def clopper_pearson(successes: int, trials: int, alpha: float = ALPHA) -> tuple[float, float]:
    """Exact binomial interval for a single rate."""
    k, n = int(successes), int(trials)
    if n <= 0:
        return float("nan"), float("nan")
    from scipy.stats import beta

    low = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    high = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return low, high


def mcnemar_exact(a: Any, b: Any) -> dict[str, Any]:
    """Exact McNemar test for paired binary outcomes (same facts, same order).

    Only the discordant facts carry information: ``only_a`` facts went to the
    paragraph under A but not B, ``only_b`` the reverse. The two-sided p-value
    is a binomial test of ``only_a`` out of ``only_a + only_b`` against 1/2.
    With no discordant facts the two conditions are indistinguishable on this
    outcome and p = 1.
    """
    first = np.asarray(a, dtype=bool)
    second = np.asarray(b, dtype=bool)
    if first.shape != second.shape:
        raise ValueError("mcnemar_exact needs two outcome vectors over the same facts")
    only_a = int(np.sum(first & ~second))
    only_b = int(np.sum(~first & second))
    if only_a + only_b == 0:
        p = 1.0
    else:
        from scipy.stats import binomtest

        p = float(binomtest(only_a, only_a + only_b, 0.5).pvalue)
    return {"only_a": only_a, "only_b": only_b, "p": p}


def sign_counts(deltas: Any) -> tuple[int, int, int]:
    values = np.asarray(deltas, dtype=float)
    return int(np.sum(values > 0)), int(np.sum(values < 0)), int(np.sum(values == 0))


def sign_test_p(positive: int, negative: int) -> float:
    """Exact two-sided sign test; ties are excluded beforehand."""
    total = int(positive) + int(negative)
    if total == 0:
        return 1.0
    from scipy.stats import binomtest

    return float(binomtest(int(positive), total, 0.5).pvalue)


def wilcoxon_p(deltas: Any) -> float:
    """Two-sided Wilcoxon signed-rank test of paired differences against 0.

    Zero differences are dropped first (the classical ``wilcox`` convention).
    If every difference is zero the conditions are identical and p = 1.
    """
    values = np.asarray(deltas, dtype=float)
    values = values[values != 0]
    if values.size == 0:
        return 1.0
    from scipy.stats import wilcoxon

    return float(wilcoxon(values).pvalue)


def holm(pvalues: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values. NaNs stay NaN and do not count."""
    p = np.asarray(pvalues, dtype=float)
    adjusted = np.full(p.shape, np.nan)
    finite = np.flatnonzero(np.isfinite(p))
    m = finite.size
    running = 0.0
    for rank, index in enumerate(finite[np.argsort(p[finite], kind="mergesort")]):
        running = max(running, min(1.0, (m - rank) * float(p[index])))
        adjusted[index] = running
    return [float(value) for value in adjusted]


def rankdata_average(values: Any) -> np.ndarray:
    """1-based ranks, ties sharing their average rank (numpy only)."""
    x = np.asarray(values, dtype=float)
    order = np.argsort(x, kind="mergesort")
    ordered = x[order]
    ranks = np.empty(x.size, dtype=float)
    start = 0
    while start < x.size:
        stop = start
        while stop + 1 < x.size and ordered[stop + 1] == ordered[start]:
            stop += 1
        ranks[order[start : stop + 1]] = (start + stop) / 2 + 1
        start = stop + 1
    return ranks


def spearman_permutation(
    x: Any,
    y: Any,
    permutations: int = DEFAULT_PERMUTATIONS,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Spearman's rho with a two-sided Monte Carlo permutation p-value.

    The null shuffles one ranking against the other. p counts the observed
    statistic as one of the permutations, (1 + #|rho_perm| >= |rho|) / (1 + P),
    so it is never exactly zero.
    """
    rx = rankdata_average(x)
    ry = rankdata_average(y)
    if rx.size != ry.size:
        raise ValueError("spearman_permutation needs two equal-length vectors")
    n = int(rx.size)
    result: dict[str, Any] = {"n": n, "rho": float("nan"), "p": float("nan"),
                              "permutations": int(permutations)}
    if n < 3:
        return result
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denominator = math.sqrt(float(rx @ rx) * float(ry @ ry))
    if denominator == 0:
        return result
    rho = float(rx @ ry) / denominator
    rng = np.random.default_rng(seed)
    exceed = 0
    done = 0
    while done < int(permutations):
        size = min(20_000, int(permutations) - done)
        shuffled = rng.permuted(np.tile(ry, (size, 1)), axis=1)
        values = (shuffled @ rx) / denominator
        exceed += int(np.sum(np.abs(values) >= abs(rho) - 1e-12))
        done += size
    result["rho"] = rho
    result["p"] = (exceed + 1) / (int(permutations) + 1)
    return result


def permutation_mean_difference(
    x: Any,
    y: Any,
    permutations: int = DEFAULT_PERMUTATIONS,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """mean(x) - mean(y) with a two-sided permutation p-value over group labels."""
    first = np.asarray(x, dtype=float)
    second = np.asarray(y, dtype=float)
    result: dict[str, Any] = {
        "n_x": int(first.size), "n_y": int(second.size),
        "difference": float("nan"), "p": float("nan"), "permutations": int(permutations),
    }
    if first.size == 0 or second.size == 0:
        return result
    observed = float(first.mean() - second.mean())
    pooled = np.concatenate([first, second])
    rng = np.random.default_rng(seed)
    exceed = 0
    done = 0
    while done < int(permutations):
        size = min(20_000, int(permutations) - done)
        shuffled = rng.permuted(np.tile(pooled, (size, 1)), axis=1)
        values = shuffled[:, : first.size].mean(axis=1) - shuffled[:, first.size :].mean(axis=1)
        exceed += int(np.sum(np.abs(values) >= abs(observed) - 1e-12))
        done += size
    result["difference"] = observed
    result["p"] = (exceed + 1) / (int(permutations) + 1)
    return result


# ---------------------------------------------------------------------------
# One cell, one paired contrast
# ---------------------------------------------------------------------------


def describe_cell(
    contextual: Any,
    margins: Any,
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Paragraph rate and mean margin of one condition, each with its CIs."""
    outcome = np.asarray(contextual, dtype=bool)
    margin = np.asarray(margins, dtype=float)
    if outcome.shape != margin.shape or outcome.ndim != 1:
        raise ValueError("describe_cell needs one outcome and one margin per fact")
    n = int(outcome.size)
    k = int(outcome.sum())
    rate_low, rate_high = bootstrap_mean_ci(outcome.astype(float), replicates, seed)
    exact_low, exact_high = clopper_pearson(k, n)
    margin_low, margin_high = bootstrap_mean_ci(margin, replicates, seed)
    return {
        "n": n,
        "k": k,
        "rate": k / n if n else float("nan"),
        "rate_ci_low": rate_low,
        "rate_ci_high": rate_high,
        "rate_exact_low": exact_low,
        "rate_exact_high": exact_high,
        "mean_margin": float(margin.mean()) if n else float("nan"),
        "margin_ci_low": margin_low,
        "margin_ci_high": margin_high,
    }


def paired_contrast(
    contextual_a: Any,
    margins_a: Any,
    contextual_b: Any,
    margins_b: Any,
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Condition A minus condition B over the same facts, in the same order."""
    xa = np.asarray(contextual_a, dtype=bool)
    xb = np.asarray(contextual_b, dtype=bool)
    ma = np.asarray(margins_a, dtype=float)
    mb = np.asarray(margins_b, dtype=float)
    if not (xa.shape == xb.shape == ma.shape == mb.shape) or xa.ndim != 1:
        raise ValueError("paired_contrast needs four equal-length vectors over the same facts")
    n = int(xa.size)
    if n == 0:
        raise ValueError("paired_contrast needs at least one shared fact")
    rate_deltas = xa.astype(float) - xb.astype(float)
    margin_deltas = ma - mb
    rate_low, rate_high = bootstrap_mean_ci(rate_deltas, replicates, seed)
    margin_low, margin_high = bootstrap_mean_ci(margin_deltas, replicates, seed)
    mcnemar = mcnemar_exact(xa, xb)
    positive, negative, zero = sign_counts(margin_deltas)
    return {
        "n": n,
        "rate_a": float(xa.mean()),
        "rate_b": float(xb.mean()),
        "delta_rate": float(rate_deltas.mean()),
        "delta_rate_ci_low": rate_low,
        "delta_rate_ci_high": rate_high,
        "mcnemar_only_a": mcnemar["only_a"],
        "mcnemar_only_b": mcnemar["only_b"],
        "mcnemar_p": mcnemar["p"],
        "mean_margin_a": float(ma.mean()),
        "mean_margin_b": float(mb.mean()),
        "delta_margin": float(margin_deltas.mean()),
        "delta_margin_ci_low": margin_low,
        "delta_margin_ci_high": margin_high,
        "wilcoxon_p": wilcoxon_p(margin_deltas),
        "n_positive": positive,
        "n_negative": negative,
        "n_zero": zero,
        "sign_test_p": sign_test_p(positive, negative),
    }


def paired_delta_summary(
    deltas: Any,
    replicates: int = DEFAULT_REPLICATES,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Mean, bootstrap CI, Wilcoxon p and sign counts of per-fact differences.

    For contrasts that are already differences, such as an interaction
    (ΔM relevant - ΔM irrelevant) or a main effect averaged over cells.
    """
    values = np.asarray(deltas, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("paired_delta_summary needs at least one per-fact difference")
    low, high = bootstrap_mean_ci(values, replicates, seed)
    positive, negative, zero = sign_counts(values)
    return {
        "n": int(values.size),
        "delta": float(values.mean()),
        "ci_low": low,
        "ci_high": high,
        "wilcoxon_p": wilcoxon_p(values),
        "n_positive": positive,
        "n_negative": negative,
        "n_zero": zero,
        "sign_test_p": sign_test_p(positive, negative),
    }


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_p(p: Any) -> str:
    """Readable p-value: three decimals, or scientific notation below 0.001."""
    try:
        value = float(p)
    except (TypeError, ValueError):
        return "–"
    if not math.isfinite(value):
        return "–"
    if value == 0:
        return "<1e-300"
    if value < 0.001:
        return f"{value:.1e}"
    return f"{value:.3f}"


def format_ci(low: Any, high: Any, digits: int = 1, scale: float = 1.0, signed: bool = True) -> str:
    try:
        lo, hi = float(low) * scale, float(high) * scale
    except (TypeError, ValueError):
        return "–"
    if not (math.isfinite(lo) and math.isfinite(hi)):
        return "–"
    sign = "+" if signed else ""
    return f"[{lo:{sign}.{digits}f}, {hi:{sign}.{digits}f}]"
