import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def draw_scatter(ax, fig, cal, title=""):
    df   = cal["df"]
    mask = cal["mask"]
    a0, a1, s_t = cal["a0"], cal["a1"], cal["S_T"]

    accepted = df[mask]
    rejected = df[~mask]

    ax.scatter(accepted["V"], accepted["f"],
               color="#2C365A", s=40, zorder=5, label="Принятые точки")
    if len(rejected):
        ax.scatter(rejected["V"], rejected["f"],
                   color="#c0392b", s=40, marker="x", zorder=5, label="Выбросы")

    v_min, v_max = df["V"].min(), df["V"].max()
    margin = (v_max - v_min) * 0.05 if v_max > v_min else 100
    v_line = np.linspace(v_min - margin, v_max + margin, 200)
    f_line = a0 + a1 * v_line

    b_str = f"+ {a0:.3f}" if a0 >= 0 else f"- {abs(a0):.3f}"
    ax.plot(v_line, f_line, color="#2C365A", linewidth=1.5,
            label=f"R = {a1:.5f}·V {b_str}")
    ax.fill_between(v_line, f_line - 2 * s_t, f_line + 2 * s_t,
                    alpha=0.12, color="#2C365A", label=f"±2·S ({2*s_t:.2f} МПа)")

    ax.set_xlabel("Скорость ультразвука V, м/с")
    ax.set_ylabel("R, МПа")
    if title:
        ax.set_title(title)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

def save_chart_to_temp(fig):
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return path

def cleanup_temp(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
