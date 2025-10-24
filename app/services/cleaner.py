# app/services/cleaner.py
import os
import pandas as pd

class Cleaner:
    """
    Classe pour transformer fichiers BRUT -> CLEAN.
    Usage:
        cleaner = Cleaner(brut_dir, clean_dir)
        cleaner.process_all()
    """
    def __init__(self, brut_dir: str, clean_dir: str):
        self.brut_dir = brut_dir
        self.clean_dir = clean_dir
        os.makedirs(self.clean_dir, exist_ok=True)

    def _process_file(self, path):
        df = pd.read_excel(path, sheet_name=0, header=None)
        file_title = df.iloc[1, 9] if len(df.columns) > 9 else ""
        file_date = df.iloc[3, 0].split(' ')[1] if " " in str(df.iloc[3, 0]) else None
        name = "RD" if file_title == "Agents report" else "EA"
        file_date_clean = file_date.replace("/", "-") if file_date else "unknown"
        final_file_name = f"{name}_{file_date_clean}.csv"
        final_path = os.path.join(self.clean_dir, final_file_name)

        lignes = []
        date_nettoyee = ""
        agent = ""
        for _, row in df.iterrows():
            col_a = str(row[0])
            col_b = str(row[1]) if pd.notna(row[1]) else ""
            if "résumé" in col_a.lower() or "resume" in col_a.lower():
                break
            elif "Le " in col_a:
                date_nettoyee = col_a.replace("Le ", "")
            elif "Agent" in col_a:
                agent = col_a
            elif len(col_b) <= 30:
                lignes.append({
                    "Date": date_nettoyee,
                    "Agent": agent,
                    "Statut": col_b,
                    "Occ": row[4] if 4 in row.index else None,
                    "Temps total": row[6] if 6 in row.index else None,
                    "Dur. moy.": row[8] if 8 in row.index else None,
                    "Dur. max.": row[10] if 10 in row.index else None,
                    "Ecart type": row[12] if 12 in row.index else None,
                    "Pourcent. temps": row[14] if 14 in row.index else None,
                    "Pourcent. Temps 2": row[16] if 16 in row.index else None
                })

        if lignes:
            df_base = pd.DataFrame(lignes)
            for col in ["Occ", "Temps total", "Dur. moy.", "Dur. max.", "Ecart type", "Pourcent. temps", "Pourcent. Temps 2"]:
                if col in df_base.columns:
                    df_base[col] = df_base[col].apply(lambda x: str(x).replace("h", ":").replace("'", ":") if pd.notna(x) else x)
            df_base = df_base[df_base["Statut"].notna() & (df_base["Statut"].astype(str).str.strip() != "")]
            df_base["LIB"] = df_base["Pourcent. Temps 2"].apply(lambda x: "Global" if pd.isna(x) or str(x).strip()=="" else "Détail")
            df_base["Agent"] = (df_base["Agent"].astype(str)
                                .str.replace(r"^Agent\s*", "", regex=True)
                                .str.split(":").str[0]
                                .str.strip())
            # garder entêtes demandés (renommer colonnes si besoin)
            df_base = df_base.rename(columns={
                "Date": "Date",
                "Agent": "Agent",
                "Statut": "Statut",
                "Occ": "Occ",
                "Temps total": "Temps total",
                "Dur. moy.": "Dur. moy.",
                "Dur. max.": "Dur. max.",
                "Ecart type": "Ecart type",
                "Pourcent. temps": "Pourcent. temps",
                "Pourcent. Temps 2": "Pourcent. Temps 2",
                "LIB": "LIB"
            })
            df_base.to_csv(final_path, index=False, sep=';')
            return final_path, len(df_base)
        return None, 0

    def process_all(self):
        files = [f for f in os.listdir(self.brut_dir) if f.endswith(('.xls', '.xlsx', '.xlsm'))]
        results = []
        for f in files:
            path = os.path.join(self.brut_dir, f)
            out_path, rows = self._process_file(path)
            results.append((f, out_path, rows))
        return results
