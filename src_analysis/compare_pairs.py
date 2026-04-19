from __future__ import annotations

import argparse
import json
from typing import List, Tuple

import numpy as np

from lib.loader import load_predictions_and_groundtruths, explain_missing_settings, get_user_studies_base_dirs
from lib.metrics import summarize_decisions, build_3cat_table


def ztest(success_a: int, total_a: int, success_b: int, total_b: int) -> Tuple[float, float]:
    count = np.array([success_a, success_b], dtype=float)
    nobs = np.array([total_a, total_b], dtype=float)
    if np.any(nobs <= 0):
        return float("nan"), float("nan")
    try:
        # Lazy import to avoid type-checker complaints about missing stubs
        from statsmodels.stats.proportion import proportions_ztest  # type: ignore
        stat, p = proportions_ztest(count, nobs, alternative='two-sided')
        return float(stat), float(p)
    except Exception:
        return float("nan"), float("nan")


def compare_pair(a: str, b: str, stage: str = "withexplanationquality") -> dict:
    pa, ga = load_predictions_and_groundtruths(a, stage=stage)
    pb, gb = load_predictions_and_groundtruths(b, stage=stage)

    sa = summarize_decisions(pa, ga)
    sb = summarize_decisions(pb, gb)

    # Decision distribution (2x3 chi-square), guard empty totals
    table = build_3cat_table(pa, pb)
    if table.sum() == 0:
        p_decision_dist = float("nan")
    else:
        try:
            # Lazy import to avoid type-checker complaints about missing stubs
            from scipy.stats import chi2_contingency  # type: ignore
            _, p_decision_dist, _, _ = chi2_contingency(table)
            p_decision_dist = float(p_decision_dist)
        except Exception:
            p_decision_dist = float("nan")

    # Not‑unsure Accept Rate
    maskA_nonU = (pa != 2)
    sA = int(np.sum(pa[maskA_nonU] == 0))
    tA = int(np.sum(maskA_nonU))

    maskB_nonU = (pb != 2)
    sB = int(np.sum(pb[maskB_nonU] == 0))
    tB = int(np.sum(maskB_nonU))
    _, p_acc_nonU = ztest(sA, tA, sB, tB)

    # FPR (AI‑incorrect, accept among non‑unsure)
    maskA_inc = (ga == 1) & maskA_nonU
    sA_fpr = int(np.sum((pa == 0) & maskA_inc))
    tA_fpr = int(np.sum(maskA_inc))
    maskB_inc = (gb == 1) & maskB_nonU
    sB_fpr = int(np.sum((pb == 0) & maskB_inc))
    tB_fpr = int(np.sum(maskB_inc))
    _, p_fpr = ztest(sA_fpr, tA_fpr, sB_fpr, tB_fpr)

    # FRR (AI‑correct, reject among non‑unsure)
    maskA_cor = (ga == 0) & maskA_nonU
    sA_frr = int(np.sum((pa == 1) & maskA_cor))
    tA_frr = int(np.sum(maskA_cor))
    maskB_cor = (gb == 0) & maskB_nonU
    sB_frr = int(np.sum((pb == 1) & maskB_cor))
    tB_frr = int(np.sum(maskB_cor))
    _, p_frr = ztest(sA_frr, tA_frr, sB_frr, tB_frr)

    return {
        "A": a,
        "B": b,
        "sumA": sa,
        "sumB": sb,
        "p_decision_dist": p_decision_dist,
        "p_accept_rate_nonU": p_acc_nonU,
        "p_FPR": p_fpr,
        "p_FRR": p_frr,
    }


def main():
    parser = argparse.ArgumentParser(description="Compare pairs of settings for decision distributions and key rates.")
    parser.add_argument("pairs", nargs="*", help="Pairs as A,B (comma-separated). If empty, runs a default set.")
    parser.add_argument("--stage", default="withexplanationquality", help="Stage key to analyze.")
    args = parser.parse_args()

    base_dirs = get_user_studies_base_dirs()
    if not base_dirs:
        print("No valid base dirs found. Set USER_STUDIES_DIR(S).")
        return

    if args.pairs:
        raw_pairs: List[Tuple[str, str]] = []
        for token in args.pairs:
            if "," in token:
                a, b = token.split(",", 1)
                raw_pairs.append((a.strip(), b.strip()))
        pairs = raw_pairs
    else:
        pairs = [
            ("vf_numeric_llava1.5_aokvqa_better_sampled_q10_i10_s0", "vf_as_prod_numeric_llava1.5_aokvqa_better_sampled_q10_i10_s0"),
            ("vf_numeric_llava1.5_vizwiz_q10_i10_s0", "vf_as_prod_numeric_llava1.5_vizwiz_q10_i10_s0"),
            ("contr_numeric_llava1.5_aokvqa_better_sampled_q10_i10_s0", "contr_as_prod_numeric_llava1.5_aokvqa_better_sampled_q10_i10_s0"),
            ("contr_numeric_llava1.5_vizwiz_q10_i10_s0", "contr_as_prod_numeric_llava1.5_vizwiz_q10_i10_s0"),
            ("prodmetric_llava1.5_aokvqa_better_sampled_q10_i10_s0", "prod_as_vf_numeric_llava1.5_aokvqa_better_sampled_q10_i10_s0"),
            ("prodmetric_llava1.5_aokvqa_better_sampled_q10_i10_s0", "prod_as_contr_numeric_llava1.5_aokvqa_better_sampled_q10_i10_s0"),
            ("prodmetric_llava1.5_vizwiz_q10_i10_s0", "prod_as_vf_numeric_llava1.5_vizwiz_q10_i10_s0"),
            ("prodmetric_llava1.5_vizwiz_q10_i10_s0", "prod_as_contr_numeric_llava1.5_vizwiz_q10_i10_s0"),
        ]

    # Check missing
    missing = [s for s in set([x for p in pairs for x in p]) if not load_predictions_and_groundtruths(s)[0].size]
    if missing:
        print(explain_missing_settings(missing))

    outputs = [compare_pair(a, b, stage=args.stage) for a, b in pairs]
    for r in outputs:
        print("\n", r["A"], "vs", r["B"]) 
        print("  Decision dist p-value:", r["p_decision_dist"]) 
        print("  Not‑unsure AcceptRate p-value:", r["p_accept_rate_nonU"]) 
        print("  FPR p-value:", r["p_FPR"]) 
        print("  FRR p-value:", r["p_FRR"]) 
        print("  A summary:", r["sumA"]) 
        print("  B summary:", r["sumB"]) 


if __name__ == "__main__":
    main()

