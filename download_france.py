import pandas as pd
import requests
from io import StringIO
import re
import datetime

url = "https://fr.wikipedia.org/wiki/Mouvement_social_contre_le_projet_de_r%C3%A9forme_des_retraites_en_France_de_2023"
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers)
tables = pd.read_html(StringIO(r.text))

t = tables[4]
# MultiIndex
dates_raw = t.iloc[:, 1] # Date

# convert 'jeudi 19 janvier 2023' to real dates
def parse_date(x):
    months = {
        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
    }
    m = re.search(r'(\d+)\s+([a-zûé]+)\s+(\d{4})', str(x).lower())
    if m:
        day = int(m.group(1))
        month = months.get(m.group(2), 1)
        year = int(m.group(3))
        return datetime.date(year, month, day)
    return None

dates = dates_raw.apply(parse_date)

def clean_num(x):
    if pd.isna(x): return None
    s = str(x).replace(u"\xa0", "").replace(" ", "").replace("millions", "000000").replace("million", "000000").replace(",", ".")
    m = re.search(r"([\d\.]+)", s)
    if m: 
        val = m.group(1)
        if '.' in val:
            return int(float(val) * 1000000)
        return int(val)
    return None

cgt = t[("Toute la France", "CGT")].apply(clean_num)
ministry = t[("Toute la France", "Ministère de l'Intérieur")].apply(clean_num)

df = pd.DataFrame({
    "date": dates,
    "cgt_count": cgt,
    "ministry_count": ministry
})
df["mid"] = (df["cgt_count"] + df["ministry_count"]) / 2
df.dropna(subset=["date"], inplace=True)
df.to_csv("data/france_2023_weekly.csv", index=False)
print("Saved france_2023_weekly.csv")
