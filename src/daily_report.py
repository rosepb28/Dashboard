import os
import sys
import yaml
import string
import xlsxwriter as xw
from datetime import datetime

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from dashboard import Dashboard

# Abrir el archivo YAML
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

ds = Dashboard(graphs=False)

month = datetime.now().strftime("%b")
today_date = datetime.now().strftime("%d-%m-%y")

folder = config["paths"]["exported"] + f"/{ds.year}/{month}/"
os.makedirs(folder) if not os.path.exists(folder) else "No"

# Generar reporte
print("Generando reporte diario...", end="", flush=True)

wbk = xw.Workbook(folder + "data.xlsx")


wst = wbk.add_worksheet(f"{today_date}")

df = ds.last_data_df.reset_index()
df = df.fillna(" ")

# Escribir header
fmt = wbk.add_format(
    {
        "bold": True,
        "border": 1,
        "align": "center",
    }
)
abc = list(string.ascii_uppercase)
cl = abc[: len(df.columns)]
tt = df.columns
for c, t in zip(cl, tt):
    wst.write("%s1" % c, t, fmt)

for j, cc in enumerate(df.columns):
    for i in range(len(df)):
        ps = "%s%d" % (cl[j], i + 2)
        vv = df[cc][i]
        wst.write(ps, vv, wbk.add_format({"border": 1}))

wbk.close()

print("Listo!")
