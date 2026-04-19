from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import numpy as np
import matplotlib.pyplot as plt


def plot_unsure_rate_over_questions(series: Dict[str, List[float]], title: str = "Unsure Rate over Questions") -> plt.Figure:
    """
    series: mapping label -> list of unsure rates per question index (as percentages or proportions).
    Returns a matplotlib Figure.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, values in series.items():
        y = np.asarray(values, dtype=float)
        ax.plot(np.arange(1, len(y) + 1), y, label=label)
    ax.set_xlabel("Question Index")
    ax.set_ylabel("Unsure Rate")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def bar_with_ci(categories: List[str], means: List[float], ci_halfwidths: List[float], ylabel: str, title: str) -> plt.Figure:
    """Simple bar plot with symmetric CI half‑widths."""
    x = np.arange(len(categories))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x, means, yerr=ci_halfwidths, capsize=4, color="#4e79a7")
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=30, ha='right')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, axis='y', alpha=0.2)
    fig.tight_layout()
    return fig


def stacked_decision_distribution(labels: List[str], counts: List[Tuple[int, int, int]], title: str = "Decision Distribution") -> plt.Figure:
    """Stacked bars for (accept, reject, unsure)."""
    accepts = [a for a, _, _ in counts]
    rejects = [r for _, r, _ in counts]
    unsures = [u for _, _, u in counts]

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x, accepts, label="Accept")
    ax.bar(x, rejects, bottom=accepts, label="Reject")
    bottom2 = (np.array(accepts) + np.array(rejects)).tolist()
    ax.bar(x, unsures, bottom=bottom2, label="Unsure")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha='right')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, axis='y', alpha=0.2)
    fig.tight_layout()
    return fig

