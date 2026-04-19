from __future__ import annotations

import argparse
import os
import pickle
import sys
from typing import Any, Iterable


def sample_iterable(it: Iterable[Any], k: int = 10):
    out = []
    for i, x in enumerate(it):
        if i >= k:
            break
        out.append(x)
    return out


def summarize_obj(name: str, obj: Any) -> None:
    print(f"\n=== {name} ===")
    print(f"type: {type(obj)}")
    try:
        if isinstance(obj, dict):
            keys = list(obj.keys())
            print(f"dict keys: {len(keys)} total")
            print(f"sample keys: {sample_iterable(keys, 10)}")
            if keys:
                k0 = keys[0]
                v0 = obj[k0]
                print(f"value type @ first key: {type(v0)}")
                # Try to show shape/columns if DataFrame-like
                shape = getattr(v0, "shape", None)
                cols = getattr(v0, "columns", None)
                if shape is not None:
                    print(f"value shape: {shape}")
                if cols is not None:
                    try:
                        print(f"value columns (first 20): {list(cols)[:20]}")
                    except Exception:
                        pass
        else:
            # DataFrame-like
            shape = getattr(obj, "shape", None)
            cols = getattr(obj, "columns", None)
            if shape is not None:
                print(f"shape: {shape}")
            if cols is not None:
                try:
                    print(f"columns (first 20): {list(cols)[:20]}")
                except Exception:
                    pass
    except Exception as e:
        print(f"(error during summary: {e})")


def main():
    parser = argparse.ArgumentParser(description="Inspect pickled analysis artifacts.")
    parser.add_argument("files", nargs="*", default=[
        "src_analysis/df_map.pkl",
        "src_analysis/df_combined123_map.pkl",
    ])
    args = parser.parse_args()

    for path in args.files:
        abspath = os.path.abspath(path)
        print(f"\nFile: {abspath}")
        if not os.path.exists(abspath):
            print("  (missing)")
            continue
        try:
            with open(abspath, "rb") as f:
                obj = pickle.load(f)
        except Exception as e:
            print(f"  (failed to load pickle: {e})")
            continue
        summarize_obj(os.path.basename(path), obj)


if __name__ == "__main__":
    main()

