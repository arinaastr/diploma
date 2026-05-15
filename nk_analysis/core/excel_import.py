# Импорт данных из Excel (.xlsx)
# Читает листы СТВОЛ и НЕ_СТВОЛ, возвращает DataFrame-ы

import os
import openpyxl
import pandas as pd


def load_xlsx(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    result = {}
    for name in wb.sheetnames:
        ws = wb[name]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) >= 2:
            result[name] = pd.DataFrame(rows[1:], columns=rows[0])
        elif len(rows) == 1:
            result[name] = pd.DataFrame(columns=rows[0])
    return result


def parse_stvol(df):
    """Разворачивает лист СТВОЛ: одна строка (горизонт, 4 стороны) → 4 записи."""
    records = []
    for _, row in df.iterrows():
        horiz = row.get("Горизонт") or row.get("горизонт") or row.iloc[0]
        sides = ["С", "Ю", "З", "В"]
        v_cols = [c for c in df.columns if "V" in str(c).upper() or "скор" in str(c).lower()]
        f_cols = [c for c in df.columns if "f" in str(c).lower() or "прочн" in str(c).lower()]
        for i, side in enumerate(sides):
            v_val = row.iloc[1 + i * 2] if len(row) > 1 + i * 2 else None
            f_val = row.iloc[2 + i * 2] if len(row) > 2 + i * 2 else None
            records.append({"Горизонт": horiz, "Сторона": side, "V": v_val, "f_МО": f_val})
    result = pd.DataFrame(records)
    result["V"]    = pd.to_numeric(result["V"],    errors="coerce")
    result["f_МО"] = pd.to_numeric(result["f_МО"], errors="coerce")
    return result


def parse_ne_stvol(df):
    """Парсит лист НЕ_СТВОЛ с гибким поиском колонок V и f_МО."""
    rename = {}
    for col in df.columns:
        cs = str(col).strip().lower()
        if "v" == cs or "скор" in cs:
            rename[col] = "V"
        elif "f" in cs or "прочн" in cs or "мо" in cs:
            rename[col] = "f_МО"
        elif "уч" in cs or "конст" in cs or "эл" in cs:
            rename[col] = "Участок"
    result = df.rename(columns=rename).copy()
    for col in ["V", "f_МО"]:
        if col in result:
            result[col] = pd.to_numeric(result[col], errors="coerce")
    if "Участок" not in result.columns:
        result["Участок"] = [f"Конструкция {i+1}" for i in range(len(result))]
    return result


def extract_pairs(df):
    """Выбирает строки с обоими значениями V и f_МО."""
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["V", "f"])
    pairs = df.dropna(subset=["V", "f_МО"]).copy()
    pairs = pairs.rename(columns={"f_МО": "f"})[["V", "f"]]
    return pairs.reset_index(drop=True)


def load_all_files(paths):
    """Загружает список xlsx. Возвращает (ds, dn, pairs_s, pairs_n, errors)."""
    all_s, all_n, errors = [], [], []
    for p in paths:
        fn = os.path.basename(p)
        try:
            sheets = load_xlsx(p)
            sheet_names_upper = {k.upper(): k for k in sheets}
            if "СТВОЛ" in sheet_names_upper:
                df = parse_stvol(sheets[sheet_names_upper["СТВОЛ"]])
                df["Файл"] = fn
                all_s.append(df)
            if "НЕ_СТВОЛ" in sheet_names_upper or "НЕ СТВОЛ" in sheet_names_upper:
                key = sheet_names_upper.get("НЕ_СТВОЛ") or sheet_names_upper.get("НЕ СТВОЛ")
                df = parse_ne_stvol(sheets[key])
                df["Файл"] = fn
                all_n.append(df)
        except Exception as e:
            errors.append(f"{fn}: {e}")
    ds = pd.concat(all_s, ignore_index=True) if all_s else pd.DataFrame()
    dn = pd.concat(all_n, ignore_index=True) if all_n else pd.DataFrame()
    return ds, dn, extract_pairs(ds), extract_pairs(dn), errors
