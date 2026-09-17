"""Bygger hovedfiguren: Sharpe og krisedrawdown pr. rebalanceringsdag."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyse import indlaes, regimescore, koer, noegletal

UD = "paper/figures"
KRISE = ("2007-10-01", "2009-03-31")


def drawdown(x):
    k = x.cumsum()
    return (k - k.cummax()).min()


if __name__ == "__main__":
    os.makedirs(UD, exist_ok=True)
    p, m = indlaes()
    score = regimescore(p, m)

    dage = list(range(1, 22))
    afkast = {k: koer(p, score, k) for k in dage}
    sharpe = [noegletal(afkast[k])["sharpe"] for k in dage]
    krise = [drawdown(afkast[k].loc[KRISE[0]:KRISE[1]]) * 100 for k in dage]

    passiv = np.log(p["offensiv"]).diff().dropna()
    sharpe_passiv = noegletal(passiv)["sharpe"]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.6))

    a1.scatter(dage, sharpe, s=26, color="#1a1a1a", zorder=3)
    a1.axhline(sharpe_passiv, color="#999999", linestyle="--", linewidth=1)
    a1.text(21.3, sharpe_passiv, "passiv", va="center", fontsize=8,
            color="#666666")
    a1.set_xlabel("Rebalanceringsdag i måneden")
    a1.set_ylabel("Sharpe")
    a1.set_title("Samme model, 21 implementeringer", fontsize=10)
    a1.set_xticks([1, 5, 10, 15, 21])

    a2.scatter(dage, krise, s=26, color="#1a1a1a", zorder=3)
    a2.set_xlabel("Rebalanceringsdag i måneden")
    a2.set_ylabel("Maks. drawdown, pct.")
    a2.set_title("Finanskrisen 2007--2009", fontsize=10)
    a2.set_xticks([1, 5, 10, 15, 21])

    for a in (a1, a2):
        a.grid(axis="y", color="#e8e8e8", linewidth=0.8, zorder=0)
        for kant in ("top", "right"):
            a.spines[kant].set_visible(False)

    fig.tight_layout()
    for endelse in ("png", "pdf"):
        sti = f"{UD}/hovedfigur.{endelse}"
        fig.savefig(sti, dpi=200, bbox_inches="tight")
        print("gemte", sti)

    print(f"\nSharpe: {min(sharpe):.3f} til {max(sharpe):.3f} "
          f"(passiv {sharpe_passiv:.3f})")
    print(f"Krisedrawdown: {min(krise):.1f}% til {max(krise):.1f}%")
