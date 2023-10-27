import os
import sys
import yaml
import string
import numpy as np
import pandas as pd
import xlsxwriter as xw
from datetime import datetime
from dateutil.relativedelta import relativedelta
from calculations import Clasification, Utils, Anomalies, Decadiarias

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from dashboard import Dashboard

# Abrir el archivo YAML
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

ds = Dashboard(graphs=False)
month = datetime.now().strftime("%b")
folder = config["paths"]["exported"] + f"/{ds.year}/{month}/"
os.makedirs(folder) if not os.path.exists(folder) else "No"

if ds.day == 1:
    this_month = ds.past_month
    month = (ds.today - relativedelta(months=1)).strftime("%b")
    this_month_day_list = ds.past_month_days_list
else:
    this_month = ds.this_month
    month = ds.today.strftime("%b")
    this_month_day_list = ds.this_month_days_list

abc = list(string.ascii_uppercase)


class ExcelWriter:
    def __init__(self, wbk, wst):
        self.wbk = wbk
        self.wst = wst

    def no_color_cell(self, df, extend=False):
        df = df.fillna(" ")

        # Escribir header
        fmt = self.wbk.add_format(
            {
                "bold": True,
                "border": 1,
                "align": "center",
            }
        )
        cl = abc[: len(df.columns)]
        if extend:
            cl.extend(["AA", "AB", "AC", "AD", "AE", "AF"])

        tt = df.columns
        for c, t in zip(cl, tt):
            self.wst.write("%s1" % c, t, fmt)

        for j, cc in enumerate(df.columns):
            for i in range(len(df)):
                ps = "%s%d" % (cl[j], i + 2)
                vv = df[cc][i]
                self.wst.write(ps, vv, self.wbk.add_format({"border": 1}))

        return self.wst

    def colored_cell(self, var, ds, this_month, this_month_day_list):
        if var not in ["tmax", "pp", "tmin"]:
            raise ValueError("Variable no soportada")

        if var == "tmax":
            data = ds.mx
            thresholds = ["p90", "p95", "p99"]
            ad = [[255, 255, 0], [255, 192, 0], [255, 0, 0]]
            comparison_operator = lambda vv, xx: vv >= xx
        elif var == "pp":
            data = ds.pp
            thresholds = ["p90", "p95", "p99"]
            ad = [[255, 255, 0], [255, 192, 0], [255, 0, 0]]
            comparison_operator = lambda vv, xx: vv >= xx
        elif var == "tmin":
            data = ds.mn
            thresholds = ["normal_f", "p10", "p5", "p1"]
            ad = [[167, 234, 82], [255, 255, 0], [255, 192, 0], [255, 0, 0]]
            comparison_operator = lambda vv, xx: vv <= xx

        clasif = Clasification(var, data, this_month, this_month_day_list, ds.umb_path)
        df = clasif.prep_df.drop(columns=["id"])
        df = df.fillna(" ")

        fmt = self.wbk.add_format(
            {
                "bold": True,
                "border": 1,
                "align": "center",
                "bg_color": "#%02x%02x%02x" % (217, 217, 217),
            }
        )
        cl = abc[: len(df.columns)]
        cl.extend(["AA", "AB", "AC", "AD", "AE", "AF"])
        tt = df.columns
        ss = df.ESTACIONES.values

        for c, t in zip(cl, tt):
            self.wst.write("%s1" % c, t, fmt)

        for i, s in enumerate(ss):
            rr = [clasif.__dict__[threshold][s].values[0] for threshold in thresholds]

            for j in range(len(tt)):
                ps = "%s%d" % (cl[j], i + 2)
                vv = df.loc[i, tt[j]]

                if isinstance(vv, str):
                    self.wst.write(ps, vv, self.wbk.add_format({"border": 1}))
                else:
                    um = 0
                    for xx in rr:
                        if comparison_operator(vv, xx):
                            um += 1
                    if np.isnan(vv):
                        vv = " "

                    if um == 0:
                        self.wst.write(
                            ps,
                            vv,
                            self.wbk.add_format({"bg_color": "FFFFFF", "border": 1}),
                        )
                    else:
                        r, g, b = ad[um - 1]
                        col = "#%02x%02x%02x" % (r, g, b)
                        self.wst.write(
                            ps, vv, self.wbk.add_format({"bg_color": col, "border": 1})
                        )

                if vv == " ":
                    self.wst.write(
                        ps, vv, self.wbk.add_format({"bg_color": "e6e6e6", "border": 1})
                    )

        return self.wst


# Creando hoja de excel
wbk = xw.Workbook(os.path.join(folder, f"{this_month}_{month}_DATOS.xlsx"))

# HOJA CON PROMEDIOS Y ACUMULADOS MENSUALES
wst_means = wbk.add_worksheet("Means")

# Calculo
tmin_mean = ds.get_monthly_means("tmin", ds.mn, ds.this_month).rename(
    columns={"Mean": "TMIN"}
)
tmax_mean = ds.get_monthly_means("tmax", ds.mx, this_month).rename(
    columns={"Mean": "TMAX"}
)
pp_sum = ds.get_monthly_means("pp", ds.pp, this_month).rename(columns={"Sum": "PP"})

# Combinando datos en un solo dataframe
df_means = pd.DataFrame(
    {"TMAX": tmax_mean["TMAX"], "TMIN": tmin_mean["TMIN"], "PP": pp_sum["PP"]}
).reindex(columns=["TMAX", "TMIN", "PP"])

# Añadiendo coordenadas
df = Utils(df_means, ds.file).add_lat_lon().rename_axis("Estaciones").reset_index()

ExcelWriter(wbk, wst_means).no_color_cell(df)

# HOJA DE ANOMALÍAS
wst_anomalies = wbk.add_worksheet("Anomalies")

amn = Anomalies(
    "tmin", tmin_mean, ds.this_month, ds.file, ds.file_w_normals
).calculate_anomalies()
amx = Anomalies(
    "tmax", tmax_mean, this_month, ds.file, ds.file_w_normals
).calculate_anomalies()
app = Anomalies(
    "pp", pp_sum, this_month, ds.file, ds.file_w_normals
).calculate_anomalies()

df_anomalies = pd.DataFrame(
    {"TMAX": amx["anomaly"], "TMIN": amn["anomaly"], "PP": app["anomaly"]}
).reindex(columns=["TMAX", "TMIN", "PP"])

df = Utils(df_anomalies, ds.file).add_lat_lon().rename_axis("Estaciones").reset_index()

ExcelWriter(wbk, wst_anomalies).no_color_cell(df)

# HOJA DE DECADIARIAS
wst_dec = wbk.add_worksheet("Dec")

df = Decadiarias(ds.pp, this_month, ds.file, ds.dec_file).calculate_anom().iloc[:, :-3]

ExcelWriter(wbk, wst_dec).no_color_cell(df)

# HOJA CON DATOS DIARIOS DE TMAX (todas las estaciones)
wst_tmax = wbk.add_worksheet("TMAX")

# Extrayendo los datos del mes actual
df_tmax = ds.mx[ds.mx.index.month == this_month]

df = pd.DataFrame(index=this_month_day_list, columns=df_tmax.columns)

for i in range(len(df_tmax)):
    df.iloc[i] = df_tmax.values[i]

df = df.T[~df.T.index.isin(config["plu_st"])]
df = df.rename_axis("Estaciones").reset_index()

ExcelWriter(wbk, wst_tmax).no_color_cell(df, extend=True)

# HOJA CON DATOS DIARIOS DE TMIN (todas las estaciones)
wst_tmin = wbk.add_worksheet("TMIN")

# Extrayendo los datos del mes actual
df_tmin = ds.mn[ds.mn.index.month == ds.this_month]

df = pd.DataFrame(index=ds.this_month_days_list, columns=df_tmin.columns)

for i in range(len(df_tmin)):
    df.iloc[i] = df_tmin.values[i]

df = df.T[~df.T.index.isin(config["plu_st"])]
df = df.rename_axis("Estaciones").reset_index()

ExcelWriter(wbk, wst_tmin).no_color_cell(df, extend=True)

# HOJA CON DATOS DIARIOS DE PP (todas las estaciones)
wst_pp = wbk.add_worksheet("PP")

# Extrayendo los datos del mes actual
df_pp = ds.pp[ds.pp.index.month == this_month]

df = pd.DataFrame(index=this_month_day_list, columns=df_pp.columns)

for i in range(len(df_pp)):
    df.iloc[i] = df_pp.values[i]

df = df.T.rename_axis("Estaciones").reset_index()

ExcelWriter(wbk, wst_pp).no_color_cell(df, extend=True)

# HOJA DE CARACTERIZACIÓN DE TMAX
wst_ctmax = wbk.add_worksheet("cTmax")

ExcelWriter(wbk, wst_ctmax).colored_cell("tmax", ds, this_month, this_month_day_list)

# HOJA DE CARACTERIZACIÓN DE TMIN
wst_ctmin = wbk.add_worksheet("cTmin")

ExcelWriter(wbk, wst_ctmin).colored_cell("tmin", ds, this_month, this_month_day_list)

# HOJA DE CARACTERIZACIÓN DE PP
wst_cpp = wbk.add_worksheet("cPP")
# data_w_color(wbk, wst_cpp, 'pp', ds, this_month, this_month_day_list)
ExcelWriter(wbk, wst_cpp).colored_cell("pp", ds, this_month, this_month_day_list)

wbk.close()
