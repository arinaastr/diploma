import math
import numpy as np
import pandas as pd

from nk_analysis.utils.constants import (
    BETON_CLASSES, THRESHOLD_OK, THRESHOLD_WARN,
    MAX_ITERATIONS, MIN_PAIRS,
    OK_BG, OK_FG, WRN_BG, WRN_FG, BAD_BG, BAD_FG,
)

def build_calibration(pairs):
    df = pairs[["V", "f"]].copy()
    df["V"] = pd.to_numeric(df["V"], errors="coerce")
    df["f"] = pd.to_numeric(df["f"], errors="coerce")
    df = df.dropna().reset_index(drop=True)

    if len(df) < MIN_PAIRS:
        return None

    mask = pd.Series(True, index=df.index)
    iterations = []
    a0 = a1 = s_t = r2 = r_corr = 0.0

    for step in range(MAX_ITERATIONS):
        sub = df[mask]
        n = len(sub)
        if n < MIN_PAIRS:
            break

        v_mean = sub["V"].mean()
        f_mean = sub["f"].mean()
        sum_dv2   = ((sub["V"] - v_mean) ** 2).sum()
        if sum_dv2 == 0:
            break
        sum_dv_df = ((sub["V"] - v_mean) * (sub["f"] - f_mean)).sum()

        a1 = sum_dv_df / sum_dv2
        a0 = f_mean - a1 * v_mean

        f_calc   = a0 + a1 * sub["V"]
        residuals = sub["f"] - f_calc
        s_t = float(np.sqrt((residuals ** 2).sum() / max(n - 2, 1)))

        ss_total    = ((sub["f"] - f_mean) ** 2).sum()
        ss_residual = (residuals ** 2).sum()
        r2 = float(1 - ss_residual / ss_total) if ss_total > 0 else 0.0

        denom = float(np.sqrt(sum_dv2 * ((sub["f"] - f_mean) ** 2).sum()))
        r_corr = float(sum_dv_df / denom) if denom > 0 else 0.0

        outliers  = residuals.abs() > 2 * s_t
        n_out = int(outliers.sum())

        iterations.append({
            "Итерация": step + 1,
            "Точек": n,
            "S, МПа": round(s_t, 3),
            "Выбросов": n_out,
            "r": round(r_corr, 4),
        })

        if n_out == 0:
            break
        mask[sub[outliers].index] = False

    # Проверка допустимости по ГОСТ 17624: r >= 0.7 и S/R <= 0.15
    sub_final = df[mask]
    f_mean_final = float(sub_final["f"].mean()) if len(sub_final) else float("nan")
    if not math.isnan(f_mean_final) and f_mean_final != 0:
        sr_ratio = float(s_t / abs(f_mean_final))
    else:
        sr_ratio = float("nan")
    valid = bool(r_corr >= 0.7 and not math.isnan(sr_ratio) and sr_ratio <= 0.15)

    return {"a0": a0, "a1": a1, "S_T": s_t, "R2": r2, "r": r_corr,
            "sr": sr_ratio, "valid": valid,
            "mask": mask, "iters": iterations, "df": df}

def get_beton_class(avg_strength):
    if avg_strength is None or (isinstance(avg_strength, float) and np.isnan(avg_strength)):
        return "—"
    for limit, cls in BETON_CLASSES:
        if avg_strength <= limit * 1.15:
            return cls
    return "B60+"

def beton_class_index(cls_name):
    for i, (_, cls) in enumerate(BETON_CLASSES):
        if cls == cls_name:
            return i
    if cls_name == "B60+":
        return len(BETON_CLASSES)
    return -1

def classify_strength(f_mpa):
    if f_mpa is None or (isinstance(f_mpa, float) and np.isnan(f_mpa)):
        return "—", BAD_BG, BAD_FG
    if f_mpa >= THRESHOLD_OK:
        return "Норма",    OK_BG,  OK_FG
    if f_mpa >= THRESHOLD_WARN:
        return "Внимание", WRN_BG, WRN_FG
    return "Критично", BAD_BG, BAD_FG

def calculate_strength(df, a0, a1):

    result = df.copy()
    result["f_расч МПа"] = np.nan
    result["Класс"]      = "—"
    result["Статус"]     = "—"

    for idx, row in result.iterrows():
        v = pd.to_numeric(row.get("V"), errors="coerce")
        if pd.isna(v):
            continue
        f = a0 + a1 * v
        cls   = get_beton_class(f)
        stat, _, _ = classify_strength(f)
        result.at[idx, "f_расч МПа"] = round(f, 1)
        result.at[idx, "Класс"]      = cls
        result.at[idx, "Статус"]     = stat

    return result
