from __future__ import annotations

import argparse
import os
import pickle
from typing import Dict, List

import pandas as pd

from lib.normalize import parse_setting_name


def dict_to_long_df(dmap: Dict[str, pd.DataFrame], source_tag: str) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for setting, df in dmap.items():
        meta = parse_setting_name(setting)
        df2 = df.copy()
        df2["setting"] = setting
        df2["source_tag"] = source_tag
        for k, v in meta.items():
            df2[k] = v
        # normalize column names if needed
        # ensure expected columns exist (fill if missing)
        for col in ["answeronly", "withexplanation", "withexplanationquality"]:
            if col not in df2.columns:
                df2[col] = pd.NA
        if "ground_truth" not in df2.columns:
            df2["ground_truth"] = pd.NA
        frames.append(df2)
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description="Build unified long-format dataset from pickles.")
    parser.add_argument("--df_map", default="src_analysis/df_map.pkl")
    parser.add_argument("--df_combined123_map", default="src_analysis/df_combined123_map.pkl")
    parser.add_argument("--out_csv", default="src_analysis/unified_human_study.csv")
    parser.add_argument("--out_parquet", default="src_analysis/unified_human_study.parquet")
    args = parser.parse_args()

    frames: List[pd.DataFrame] = []

    if os.path.exists(args.df_map):
        with open(args.df_map, "rb") as f:
            d1 = pickle.load(f)
        frames.append(dict_to_long_df(d1, source_tag="df_map"))

    if os.path.exists(args.df_combined123_map):
        with open(args.df_combined123_map, "rb") as f:
            d2 = pickle.load(f)
        frames.append(dict_to_long_df(d2, source_tag="df_combined123_map"))

    if not frames:
        print("No input pickles found.")
        return

    uni = pd.concat(frames, ignore_index=True)

    # Derive a few convenience columns
    # three-way decision at each stage already represented by integers 0/1/2
    # expose boolean masks for quick filtering
    for stage in ["answeronly", "withexplanation", "withexplanationquality"]:
        if stage in uni.columns:
            uni[f"{stage}_is_accept"] = (uni[stage] == 0)
            uni[f"{stage}_is_reject"] = (uni[stage] == 1)
            uni[f"{stage}_is_unsure"] = (uni[stage] == 2)

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    uni.to_csv(args.out_csv, index=False)

    try:
        uni.to_parquet(args.out_parquet, index=False)
    except Exception as e:
        print(f"(parquet write skipped: {e})")

    print("Saved:")
    print("  ", os.path.abspath(args.out_csv))
    print("  ", os.path.abspath(args.out_parquet))
    print("Rows:", len(uni))
    print("Columns:", list(uni.columns)[:20], "...")


if __name__ == "__main__":
    main()

