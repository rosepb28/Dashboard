import os
import yaml
import urllib3
import requests
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dash_table
import plotly.graph_objects as go
from datetime import date, timedelta


pd.set_option("mode.chained_assignment", None)
urllib3.disable_warnings()

# Abrir el archivo YAML
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


def create_csv_if_not_exists(st_file):
    if not os.path.exists(st_file):
        # Crear DataFrame con los últimos 6 días en la columna 'Fecha'
        fecha_actual = pd.Timestamp.now().date()
        fechas = pd.date_range(end=fecha_actual, periods=45)
        fechas_str = fechas.strftime("%Y-%m-%d")
        df = pd.DataFrame({"Fecha": fechas_str, "Tmax": -999, "Tmin": -999, "PP": -999})

        # Guardar DataFrame en un archivo CSV
        df.to_csv(st_file, index=False)
        print(f"Archivo {st_file} creado exitosamente.")


def lvera():
    """
    Web scraping de la web lvera para extraer los últimos días con datos
    de las estaciones escogidas en file.
    Devuelve un diccionario (data) que contiene todas las estaciones con los datos
    de los últimos 30 días, para las 3 variables (Tmax, Tmin y PP).

    Parámetros:
    download_to_csv: Booleano para descargar datos de lvera a archivos csv.
                        Es False por defecto.
    from_file: Booleano, por defecto ingresa a la página de lvera. Si se tiene
                guardada la página en el archivo url y se quiere ingresar a través
                de este, cambiar a True.
    """
    # Filtro de estaciones
    ss = pd.read_excel(config["files"]["list"])
    ss = ss[ss["Dash"] == 1]

    # Web scraping con la web lvera

    if config["url_from_file"]:
        print("Leyendo datos desde archivo guardado.")
        f = open(config["files"]["url"])
        rpc = pd.read_html(f.read(), header=[0, 1])[0]
    else:
        print("Leyendo datos desde la web lvera.")
        url = "https://www.senamhi.gob.pe/site/lvera/reporte_diario_rpc.php"
        f = requests.get(url, verify=False).content
        rpc = pd.read_html(f, header=[0, 1])[0]

    # Arreglando encabezados de la tabla extraída
    rpc.columns = [c[0] if c[0] == c[1] else "_".join(c) for c in rpc.columns.values]
    rpc.columns.values[
        5
    ] = "Estacion"  # Modificar directamente los valores de la columna

    # Leyendo info de web y creando header
    rpc["Cod_Ant."] = rpc["Cod_Ant."].map(lambda x: "%06d" % x)
    rpc["Cod."] = rpc["Cod."].map(lambda x: "%d" % x)

    # Seleccionando solo los que hay en la web
    idd = ss["Cod"].isin(rpc["Cod."])
    ss_rpc = ss[idd]
    v_rpc = ["MAX", "MIN", "PP"]
    v_df = ["Tmax", "Tmin", "PP"]

    # loop para todas las estaciones
    data_dict = {}
    for i in range(len(ss_rpc)):
        cod, prv, st = ss_rpc[["Cod", "Provincia", "Nombre"]].values[i]

        # Leyendo csv's con datos
        st_file = os.path.join(config["paths"]["series"], f"{prv}/{cod}_{st}.csv")

        try:
            data = pd.read_csv(st_file)
        except:
            create_csv_if_not_exists(st_file)
            data = pd.read_csv(st_file)

        data["Fecha"] = pd.to_datetime(data["Fecha"])

        # Creando rango de fechas con última fecha de csv hasta día actual
        fe = pd.date_range(
            start=data["Fecha"].values[-1], end=date.today(), closed="right"
        )

        # Generando dataframe vacío con nuevo rango de fechas
        nn = pd.DataFrame(
            {
                "Fecha": fe,
                "Tmax": np.full(len(fe), -999),
                "Tmin": np.full(len(fe), -999),
                "PP": np.full(len(fe), -999),
            }
        )

        # Uniendo data de csv's con nuevo dataframe
        df = pd.concat([data, nn], ignore_index=True)

        # Bucle para extraer data de web de cada columna y asignarlo al dataframe
        for a, b in zip(v_rpc, v_df):
            vc = [x for x in rpc.columns if a in x]
            ld = date.today() - timedelta(days=1)
            if a == "MIN":
                ld = date.today()
            ff = pd.date_range(end=ld, periods=len(vc))
            df.loc[df["Fecha"].isin(ff), b] = (
                rpc.loc[rpc["Cod."] == cod, vc].values[0].tolist()
            )

        data_dict[st] = df.tail(45)

        # Actualizando bases de datos con información del lvera
        if config["export_to_csv"]:
            print("Descargando datos de web lvera a archivos locales..")
            df.to_csv(st_file, index=False)
            print("Archivos actualizados.")

    return data_dict


class LastData:
    def __init__(self, last_data_df):
        self.last_data_df = last_data_df

    def meteorogram(self):
        df = self.last_data_df.reset_index()

        tmx = go.Scatter(
            x=df["ESTACIONES"],
            y=df["TMAX"],
            name="Tmax de ayer (°C)",
            mode="markers+text",
            marker_symbol="triangle-up",
            marker_size=10,
            yaxis="y2",
            line={"color": "Red"},
            text=df["TMAX"].astype(str).tolist(),
            textposition="top center",
            textfont={"size": 14, "color": "crimson"},
        )
        tmn = go.Scatter(
            x=df["ESTACIONES"],
            y=df["TMIN"],
            name="Tmin de hoy (°C)",
            yaxis="y2",
            line={"color": "Blue"},
            mode="markers+text",
            marker_symbol="square",
            marker_size=8,
            text=df["TMIN"].astype(str).tolist(),
            textposition="top center",
            textfont={"size": 14, "color": "blue"},
        )
        ppp = go.Bar(
            x=df["ESTACIONES"],
            y=df["PP"],
            name="PP de ayer (mm/día)",
            marker_color="yellowgreen",
            opacity=0.6,
            text=df["PP"].astype(str).tolist(),
            textposition="auto",
            textfont={"size": 14, "color": "darkgreen"},
        )
        layout = go.Layout(
            xaxis={
                "title_font": {"color": "rgba(100,143,240,255)"},
                "domain": [0, 0.94],
                "linewidth": 0.5,
                "linecolor": "rgba(196,198,206,255)",
                "showline": True,
                "showgrid": True,
                "gridwidth": 1,
                "gridcolor": "#e3e2e1",
            },
            yaxis={
                "title": "Precipitacion (mm/día)",
                "title_font": {"color": "rgba(100,143,240,255)"},
                "tickfont": {"color": "rgba(100,143,240,255)"},
                "domain": [0, 0.94],
                "side": "right",
                "showgrid": False,
                "gridwidth": 0.5,
                "gridcolor": "#e3e2e1",
            },
            yaxis2={
                "title": "Temperatura (°C)",
                "title_font": {"color": "rgba(100,143,240,255)"},
                "tickfont": {"color": "rgba(100,143,240,255)"},
                "anchor": "x",
                "overlaying": "y",
                "side": "left",
                "showgrid": True,
                "gridwidth": 0.5,
                "gridcolor": "#e3e2e1",
                "dtick": 3,
            },
            margin={"l": 50, "r": 50, "b": 20, "t": 40, "pad": 4},
            plot_bgcolor="rgb(255, 255, 255)",
            paper_bgcolor="rgb(255, 255, 255)",
            showlegend=True,
            legend={
                "y": 1.1,
                "x": 0.3,
                "yanchor": "top",
                "bordercolor": "rgba(244,244,244,255)",
                "borderwidth": 1,
                "orientation": "h",
            },
            xaxis_tickangle=-45,
            height=600,
        )
        last_data_fig = go.Figure(data=[tmx, tmn, ppp], layout=layout)

        return last_data_fig

    def map_temps(self, var, mapbox_token):
        var = var.upper()
        plu_st = ["LIVES", "CHUGUR"]
        df = self.last_data_df[["Lat", "Lon", var]]
        df = df[~df.index.isin(plu_st)]
        df["size"] = 10

        if var == "TMIN":
            opt = {"Lat": False, "Lon": False, "size": False, "TMIN": True}
            color_scale = px.colors.sequential.ice
        elif var == "TMAX":
            opt = {"Lat": False, "Lon": False, "size": False, "TMAX": True}
            color_scale = px.colors.sequential.YlOrRd
        else:
            ValueError("Variable no soportada.")

        mapbx = px.scatter_mapbox(
            df,
            lat="Lat",
            lon="Lon",
            hover_name=df.index,
            hover_data=opt,
            opacity=0.9,
            color=var,
            color_continuous_scale=color_scale,
            size=df["size"],
            size_max=17,
            zoom=8,
            height=500,
            width=600,
        )

        mapbx.update_layout(
            hovermode="closest",
            autosize=False,
            mapbox=dict(
                accesstoken=mapbox_token,
                bearing=0,
                center=go.layout.mapbox.Center(lat=-7.16, lon=-78.49),
                style="light",
                pitch=0,
                zoom=8,
            ),
            margin=dict(t=0, b=0, l=0, r=0),
        )

        return mapbx

    def map_pp(self, mapbox_token):
        df = self.last_data_df[["Lat", "Lon", "PP"]]
        df.dropna(inplace=True)
        opt = {"Lat": False, "Lon": False, "PP": True}

        mapbx = px.scatter_mapbox(
            df,
            lat="Lat",
            lon="Lon",
            hover_name=df.index,
            hover_data=opt,
            opacity=0.9,
            color="PP",
            color_continuous_scale=px.colors.sequential.Viridis_r,
            size="PP",
            size_max=30,
            zoom=8,
            height=500,
            width=600,
        )

        mapbx.update_layout(
            hovermode="closest",
            autosize=False,
            mapbox=dict(
                accesstoken=mapbox_token,
                bearing=0,
                center=go.layout.mapbox.Center(lat=-7.16, lon=-78.49),
                style="light",
                pitch=0,
                zoom=8,
            ),
            margin=dict(t=0, b=0, l=0, r=0),
        )
        return mapbx


def series(var, df, this_month, day):
    """
    Devuelve gráficos de series de tiempo para las temperaturas extremas,
    y gráfico de barras para precipitación.

    var: 'tmax', 'tmin' o 'pp'.
    df: dataframe (mx, mn o pp).
    this_month: mes anterior si es el día 1 del mes, mes actual para los demás días.
    day: día anterior si es el día 1 del mes, día actual a partir del día 2 del mes.
    """
    var = var.lower()
    if var == "tmax" or var == "tmin":
        ss = []
        for i in range(len(df.columns)):
            ss.append(
                go.Scatter(
                    x=df[df.index.month == this_month].index.day,
                    y=df.iloc[-day:, i],
                    mode="lines+markers",
                    name=df.columns[i],
                )
            )

        layout = go.Layout(
            xaxis={
                "title": "Días",
                "title_font": {"color": "rgba(100,143,240,255)"},
                "showline": True,
                "linewidth": 1,
                "linecolor": "rgba(196,198,206,255)",
                "showgrid": True,
                "gridwidth": 1,
                "gridcolor": "rgba(244,244,244,255)",
                "dtick": 1,
            },
            yaxis={
                "title": "Temperatura (°C)",
                "title_font": {"color": "rgba(100,143,240,255)"},
                "showgrid": True,
                "gridwidth": 0.5,
                "gridcolor": "rgba(244,244,244,255)",
                "dtick": 2,
            },
            colorway=px.colors.qualitative.Plotly,
            paper_bgcolor="rgb(255,255,255)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            showlegend=True,
            legend={"title_text": "Estaciones", "x": 1.03, "y": 0.93},
            height=650,
        )

        fig = go.Figure(data=ss, layout=layout)

    elif var == "pp":
        pp_daily_sum = pd.DataFrame(
            columns=["PP_sum"], index=df.index, data=df.sum(axis=1)
        )
        pp_daily_sum = pp_daily_sum[pp_daily_sum.index.month == this_month]

        pp_bars = go.Bar(
            x=pp_daily_sum.index.day,
            y=pp_daily_sum.iloc[:, 0],
            marker_color="#17BECF",
            opacity=0.8,
        )
        layout = go.Layout(
            yaxis={
                "title": "Precipitación acumulada por día",
                "title_font": {"color": "rgba(100,143,240,255)"},
                "tickfont": {"color": "rgba(100,143,240,255)"},
                "showgrid": True,
                "gridwidth": 0.5,
                "gridcolor": "rgba(244,244,244,255)",
                "dtick": 50,
            },
            xaxis={"nticks": len(pp_daily_sum) + 1},
            paper_bgcolor="rgb(255,255,255)",  # "rgba(0, 0, 0, 0)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            colorway=px.colors.qualitative.Plotly,
            xaxis_tickangle=0,
        )

        fig = go.Figure(data=pp_bars, layout=layout)
    else:
        ValueError("Variable no soportada.")

    return fig


class Anomalies:
    """
    Esta clase calcula las anomalías, genera gráficos de barras y mapas,
    para las variables de interés.

    Parámetros:
    var: 'tmax', 'tmin' o 'pp'.
    df_mean: dataframe con promedio o acumulado mensual.
    this_month: mes anterior si es el día 1 del mes, mes actual para los demás días.
    file: archivo 'lista' con todas las estaciones.
    file_w_normals: archivo 'norm' con los valores de las normales climátias.
    """

    def __init__(self, var, df_mean, this_month, file, file_w_normals):
        self.var = var.upper()
        self.df_mean = df_mean
        self.this_month = this_month
        self.file = file
        self.file_w_normals = file_w_normals
        # self.calculate_anomalies()

    def calculate_anomalies(self):
        normal_file = pd.read_excel(self.file_w_normals, sheet_name=self.var)
        if self.var == "TMAX" or self.var == "TMIN":
            ee = self.df_mean.index  # Lista completa de estaciones
            idd = ee.isin(
                normal_file[1:].columns
            )  # Condicional para estaciones con anomalías
            # Filtro en dataframe con valores promedio
            df_mean_f = self.df_mean.loc[ee[idd]]
            # Filtro en dataframe de normales
            normal_f = normal_file.loc[normal_file["MES"] == self.this_month, ee[idd]]
            anomaly = (df_mean_f.T.values - normal_f.values)[0].tolist()
            df_mean_f["anomaly"] = anomaly
        elif self.var == "PP":
            ee = self.df_mean.index  # Lista completa de estaciones
            idd = ee.isin(
                normal_file[1:].columns
            )  # Condicional para estaciones con anomalías
            # Filtro en dataframe con valores promedio
            df_mean_f = self.df_mean.loc[ee[idd]]
            # Filtro en dataframe de normales
            normal_f = normal_file.loc[normal_file["MES"] == self.this_month, ee[idd]]

            missing_stations = normal_f.columns[
                normal_f.loc[self.this_month - 1] == 0
            ].tolist()

            if missing_stations:
                normal_f.drop(columns=missing_stations, inplace=True)
                df_mean_f.drop(index=missing_stations, inplace=True)

            # Cálculo de la anomalía
            anomaly = (
                (((df_mean_f.T.values / normal_f.values) - 1) * 100)
                .round(1)[0]
                .tolist()
            )
            df_mean_f["anomaly"] = anomaly
        else:
            raise ValueError("Variable no soportada")

        return df_mean_f

    def bars_fig(self, today_date):
        """
        Gráfico de barras.

        Parámetro:
        today_date: fecha en tipo string del día anterior si es el día 1 del mes,
                    o fecha actual si es cualquier otro día.
        """
        df_mean_f = self.calculate_anomalies()
        df_mean_f = df_mean_f.dropna()
        # Añadiendo colores dependiendo de la variable
        if self.var == "TMAX" or self.var == "TMIN":
            for st in df_mean_f.index:
                if df_mean_f.loc[st, "anomaly"] > 0:
                    df_mean_f.loc[st, "color"] = "red"
                elif df_mean_f.loc[st, "anomaly"] == 0:
                    df_mean_f.loc[st, "color"] = "white"
                else:
                    df_mean_f.loc[st, "color"] = "blue"
        elif self.var == "PP":
            df_mean_f = self.calculate_anomalies()
            df_mean_f["color"] = np.where(
                df_mean_f["anomaly"] > 0, "yellowgreen", "rgb(237,173,8)"
            )
        else:
            raise ValueError("Variable no soportada")

        anom_bars = go.Bar(
            x=df_mean_f.index,
            y=df_mean_f.loc[:, "anomaly"],
            marker_color=df_mean_f["color"],
            opacity=0.5,
        )

        layout = go.Layout(
            yaxis={
                "title": "Anomalía (°C)",
                "title_font": {"color": "rgba(100,143,240,255)"},
                "tickfont": {"color": "rgba(100,143,240,255)"},
                "showgrid": True,
                "gridwidth": 0.5,
                "gridcolor": "rgba(244,244,244,255)",
            },
            title={
                "text": f"Anomalías al <b>{today_date}<b>",
                "font": {"color": "black", "size": 18},
                "x": 0.5,
            },
            colorway=px.colors.qualitative.Plotly,
            plot_bgcolor="rgba(0, 0, 0, 0)",
            xaxis_tickangle=-45,
        )

        fig = go.Figure(data=anom_bars, layout=layout)

        return fig

    def maps(self, mapbox_token):
        """
        Genera mapas de anomalías.

        Parámetros:
        mapbox_token: key de mapbox.
        """
        df_map = self.calculate_anomalies()
        df_map = df_map.dropna()  # Eliminando estaciones sin anomalías

        # Añadiendo coordenadas a estaciones con anomalías
        df_map = Utils(df_map, self.file).add_lat_lon()

        df_map = df_map.rename_axis("Estaciones").reset_index()
        # Añadiendo colores de acuerdo al valor
        if self.var == "TMAX" or self.var == "TMIN":
            limits = [-np.inf, -3, -2, -1, 1, 2, 3, np.inf]
            colors = [
                "#1f42b4",
                "#52a2d7",
                "#a6cee3",
                "#ffffff",
                "#ffb9b9",
                "#f57474",
                "#d1191f",
            ]
        elif self.var == "PP":
            limits = [-np.inf, -100, -60, -15, 15, 60, 100, np.inf]
            colors = [
                "#f09d05",
                "#e4a906",
                "#fae76c",
                "#ffffff",
                "#95cf4f",
                "#039408",
                "#2fad9c",
            ]
        else:
            ValueError("Variable no soportada.")

        df_map["Color"] = pd.cut(
            df_map["anomaly"], bins=limits, labels=colors, right=False
        )
        df_map["Color"] = df_map["Color"].astype(str)
        # Añadiendo opciones para los marcadores del mapa
        df_map["size"] = 10
        opt = {"Lat": False, "Lon": False, "size": False, "anomaly": True}

        mapbx = px.scatter_mapbox(
            df_map,
            lat="Lat",
            lon="Lon",
            hover_name="Estaciones",
            hover_data=opt,
            opacity=0.9,
            color=df_map["Color"],
            color_discrete_map="identity",
            size=df_map["size"],
            size_max=27,
            zoom=8,
            height=500,
            width=600,
        )

        mapbx.update_layout(
            hovermode="closest",
            autosize=False,
            mapbox=dict(
                accesstoken=mapbox_token,
                bearing=0,
                center=go.layout.mapbox.Center(lat=-7.16, lon=-78.49),
                style="light",
                pitch=0,
                zoom=8,
            ),
            margin=dict(t=0, b=0, l=0, r=0),
        )

        return mapbx


class Clasification:
    """
    Esta clase genera las tablas con la caracterización de las variables de interés
    en base a sus percentiles y normales climáticas.

    Parámetros:
    var: 'tmax', 'tmin' o 'pp'.
    df: dataframe (mx, mn o pp).
    this_month: mes anterior si es el día 1 del mes, mes actual para los demás días.
    this_month_days_list: Lista con los días (tipo string) del mes anterior si es el día 1,
                            o del mes actual si es cualquier otro día.
    """

    def __init__(self, var, df, this_month, this_month_days_list, umb_path):
        self.var = var
        self.df = df
        self.this_month = this_month
        self.this_month_days_list = this_month_days_list
        self.umb_path = umb_path
        self.get_percentile()
        self.prep_dataframe()

    def get_percentile(self):
        """
        Selecciona los percentiles y normales climáticas de la variable escogida,
        Retorna el dataframe ingresado SOLO con las estaciones que cuentan con
        dichos umbrales.
        """
        var = self.var.upper()
        prc_file = os.path.join(config["paths"]["umbrales"], f"PRC_{var}.xlsx")
        if var == "TMIN":
            norm_file = config["files"]["normals"]

            prc_1 = pd.read_excel(prc_file, sheet_name="prc_1")
            prc_5 = pd.read_excel(prc_file, sheet_name="prc_5")
            prc_10 = pd.read_excel(prc_file, sheet_name="prc_10")
            normal = pd.read_excel(norm_file, sheet_name=var)

            ee = self.df.columns
            idd = ee.isin(prc_1.columns[1:])
            df_f = self.df.loc[:, ee[idd]]
            df_f = df_f[df_f.index.month == self.this_month]

            p1 = prc_1[(prc_1["MES"] == self.this_month)]
            p1 = p1[ee[idd]]
            p5 = prc_5[(prc_5["MES"] == self.this_month)]
            p5 = p5[ee[idd]]
            p10 = prc_10[(prc_10["MES"] == self.this_month)]
            p10 = p10[ee[idd]]
            normal_f = normal.loc[normal["MES"] == self.this_month, ee[idd]]

            self.df_f = df_f
            self.normal_f = normal_f
            self.p1 = p1
            self.p5 = p5
            self.p10 = p10
        else:
            prc_90 = pd.read_excel(prc_file, sheet_name="prc_90")
            prc_95 = pd.read_excel(prc_file, sheet_name="prc_95")
            prc_99 = pd.read_excel(prc_file, sheet_name="prc_99")

            ee = self.df.columns
            idd = ee.isin(prc_90.columns[1:])
            df_f = self.df.loc[:, ee[idd]]
            df_f = df_f[df_f.index.month == self.this_month]

            p90 = prc_90[(prc_90["MES"] == self.this_month)]
            p90 = p90[ee[idd]]
            p95 = prc_95[(prc_95["MES"] == self.this_month)]
            p95 = p95[ee[idd]]
            p99 = prc_99[(prc_99["MES"] == self.this_month)]
            p99 = p99[ee[idd]]

            self.df_f = df_f
            self.p90 = p90
            self.p95 = p95
            self.p99 = p99

    def prep_dataframe(self):
        """
        Este método prepara el dataframe generado en get_percentile() para añadir
        estilos.
        """
        prep_df = pd.DataFrame(
            index=self.this_month_days_list, columns=self.df_f.columns, data=np.NaN
        )

        for i in range(len(self.df_f)):
            prep_df.iloc[i] = self.df_f.values[i]
        prep_df = prep_df.T

        prep_df = prep_df.rename_axis("ESTACIONES").reset_index()
        prep_df["id"] = prep_df.index

        self.prep_df = prep_df

    def style_tmin(self):
        numeric_columns = (
            self.prep_df.select_dtypes("number").drop(["id"], axis=1).columns
        )
        styles = []

        for i in range(len(self.prep_df)):
            row = self.prep_df.loc[i, numeric_columns]
            ranges = [
                self.p1.iloc[0, i],
                self.p5.iloc[0, i],
                self.p10.iloc[0, i],
                self.normal_f.iloc[0, i],
            ]

            for j in range(len(self.prep_df.columns) - 2):
                style = {
                    "if": {
                        "filter_query": "{{id}} = {}".format(i),
                        "column_id": row.keys()[j],
                    },
                    "backgroundColor": "#ffffff",
                    "color": "black",
                }

                if row[j] <= ranges[0]:
                    style["backgroundColor"] = "#ff0000"
                elif row[j] <= ranges[1]:
                    style["backgroundColor"] = "#ffc000"
                elif row[j] <= ranges[2]:
                    style["backgroundColor"] = "#ffff00"
                elif row[j] <= ranges[3]:
                    style["backgroundColor"] = "#a7ea52"
                elif np.isnan(row[j]):
                    style["backgroundColor"] = "#d9d9d9"

                styles.append(style)

        cc = dash_table.DataTable(
            data=self.prep_df.to_dict("records"),
            sort_action="native",
            columns=[{"name": i, "id": i} for i in self.prep_df.columns if i != "id"],
            style_data_conditional=styles,
            style_data={"height": "auto"},
            style_cell_conditional=[{"textAlign": "center"}],
        )

        return cc

    def style_tmax(self):
        numeric_columns = (
            self.prep_df.select_dtypes("number").drop(["id"], axis=1).columns
        )
        styles = []

        for i in range(len(self.prep_df)):
            row = self.prep_df.loc[i, numeric_columns]
            ranges = [self.p90.iloc[0, i], self.p95.iloc[0, i], self.p99.iloc[0, i]]

            for j in range(len(self.prep_df.columns) - 2):
                style = {
                    "if": {
                        "filter_query": "{{id}} = {}".format(i),
                        "column_id": row.keys()[j],
                    },
                    "backgroundColor": "#ffffff",
                    "color": "black",
                }

                if row[j] >= ranges[0] and row[j] < ranges[1]:
                    style["backgroundColor"] = "#ffff00"  # amarillo
                elif row[j] >= ranges[1] and row[j] < ranges[2]:
                    style["backgroundColor"] = "#ffc000"  # naranja
                elif row[j] >= ranges[2]:
                    style["backgroundColor"] = "#ff0000"  # rojo
                elif np.isnan(row[j]):
                    style["backgroundColor"] = "#d9d9d9"  # plomo (para vacíos)

                styles.append(style)

        cc = dash_table.DataTable(
            data=self.prep_df.to_dict("records"),
            sort_action="native",
            columns=[{"name": i, "id": i} for i in self.prep_df.columns if i != "id"],
            style_data_conditional=styles,
            style_data={"height": "auto"},
            style_cell_conditional=[{"textAlign": "center"}],
        )

        return cc

    def style_pp(self):
        return self.style_tmax()


class Decadiarias:
    """
    Esta clase calcula las anomalías de precipitación por decadiarias y
    genera los mapas.

    Parámetros:
    pp: dataframe 'pp'.
    this_month: mes anterior si es el día 1 del mes, mes actual para los demás días.
    file: ruta de archivo 'lista' con todas las estaciones.
    dec_file: ruta de archivo con decadiarias.
    """

    def __init__(self, pp, this_month, file, dec_file):
        self.pp = pp
        self.this_month = this_month
        self.file = file
        self.dc = pd.read_excel(dec_file)
        self.df_prep()

    def df_prep(self):
        """
        Este método prepara el dataframe 'pp' que contiene los datos de los últimos 30 días.

        Retorna un dataframe con la suma de las precipitaciones en las 3 decadiarias del mes
        y las decadiarias adecuadas de acuerdo al mes.
        """
        # Filtrando valores del mes actual
        df = self.pp[self.pp.index.month == self.this_month]
        # Creando dataframe de precipitación y añadiendo columna con nro de decadiaria
        df.insert(0, "Decadiaria", np.nan)

        df.loc[df.index.day <= 10, "Decadiaria"] = 1
        df.loc[(df.index.day > 10) & (df.index.day <= 20), "Decadiaria"] = 2
        df.loc[df.index.day > 20, "Decadiaria"] = 3

        # Calculando suma de valores por decadiaria
        sum_df = df.groupby(pd.Grouper("Decadiaria")).sum()

        # Escogiendo decadiarias del mes actual:
        dc = self.dc[self.dc["MES"] == self.this_month]

        # Omitiendo estaciones con normales iguales a 0
        self.columns_to_drop = []
        for i in dc.columns[2:]:
            if (dc[i] == 0).any():
                self.columns_to_drop.append(i)

        dc.drop(columns=self.columns_to_drop, inplace=True)
        sum_df.drop(columns=self.columns_to_drop, inplace=True)

        ee = sum_df.columns
        idd = sum_df.columns.isin(dc.columns)
        sum_df_f = sum_df[ee[idd]]  # filtro de estaciones con decadiarias
        dc_f = dc[ee[idd]]  # filtro en archivo de decadiarias

        return sum_df_f, dc_f

    def calculate_anom(self):
        """
        Calcula las anomalías por decadiaria y asigna colores de acuerdo a su valor.
        """
        sum_df_f, dc_f = self.df_prep()

        # Creando nuevo array con la forma de dc_f
        shape = dc_f.shape
        new_array = np.zeros(shape)
        new_array[: sum_df_f.shape[0], :] = sum_df_f

        # Cálculo de decadiarias
        dec = (((new_array / dc_f) - 1) * 100).round(1)
        idx = ["1ra-Dec", "2da-Dec", "3ra-Dec"]
        dec_df = dec.T.copy()
        dec_df.columns = idx

        # Función para asignar colores basados en las condiciones
        val = [-100, -60, -30, -15, 15, 30, 60, 100, 200, 400, 800, np.inf]
        cols = [
            "#c2523c",
            "#e99519",
            "#fbea06",
            "#ffffff",
            "#b8f501",
            "#40e300",
            "#1ab04d",
            "#19875a",
            "#089ead",
            "#2b61a9",
            "#0b2c7b",
        ]

        def assign_color(value):
            if value == -100:
                return "#c2523c"
            else:
                return pd.cut([value], bins=val, labels=cols)[0]

        # Aplicar la función a las columnas correspondientes
        dec_df.loc[:, "C1"] = dec_df.loc[:, "1ra-Dec"].apply(assign_color)
        dec_df.loc[:, "C2"] = dec_df.loc[:, "2da-Dec"].apply(assign_color)
        dec_df.loc[:, "C3"] = dec_df.loc[:, "3ra-Dec"].apply(assign_color)

        # Añadiendo coordenadas
        dec_df = Utils(dec_df, self.file).add_lat_lon()

        dec = dec_df.rename_axis("Estaciones").reset_index()

        return dec

    def maps(self, d, mapbox_token):
        """
        Genera los mapas de anomalías por decadiarias usando mapbox.

        Parámetros:
        d: decadiaria a solicitar ('d1', 'd2', 'd3')
        mapbox_token: key de mapbox.
        """
        dec = self.calculate_anom()
        dec.loc[:, "size"] = 10

        if d == "d1":
            opt = {
                "Lat": False,
                "Lon": False,
                "size": False,
                "1ra-Dec": True,
                "2da-Dec": False,
                "3ra-Dec": False,
            }
            color_col = "C1"
        elif d == "d2":
            opt = {
                "Lat": False,
                "Lon": False,
                "size": False,
                "1ra-Dec": False,
                "2da-Dec": True,
                "3ra-Dec": False,
            }
            color_col = "C2"
        else:
            opt = {
                "Lat": False,
                "Lon": False,
                "size": False,
                "1ra-Dec": False,
                "2da-Dec": False,
                "3ra-Dec": True,
            }
            color_col = "C3"

        mapbx_dc = px.scatter_mapbox(
            dec,
            lat="Lat",
            lon="Lon",
            hover_name="Estaciones",
            hover_data=opt,
            opacity=1,
            color=dec[color_col],
            color_discrete_map="identity",
            size=dec["size"],
            size_max=27,
            zoom=8,
            height=500,
            width=600,
        )

        mapbx_dc.update_layout(
            hovermode="closest",
            autosize=False,
            mapbox=dict(
                accesstoken=mapbox_token,
                bearing=0,
                center=go.layout.mapbox.Center(lat=-7.16, lon=-78.49),
                style="light",
                pitch=0,
                zoom=8,
            ),
            margin=dict(t=0, b=0, l=0, r=0),
        )

        return mapbx_dc


class Utils:
    """
    Clase para añadir coordenadas y provincias.
    Se usa SOLO para generar mapas.
    """

    def __init__(self, df, file):
        self.df = df
        self.file = file

    def add_lat_lon(self):
        file = pd.read_excel(self.file)

        coords = file[file.Nombre.isin(self.df.index)][["Lat", "Lon"]]
        lat = coords["Lat"].tolist()
        lon = coords["Lon"].tolist()

        self.df.insert(0, "Lat", value=lat)
        self.df.insert(1, "Lon", value=lon)

        return self.df

    def add_lat_lon_prov(self):
        file = pd.read_excel(self.file)
        coords = file[file.Nombre.isin(self.df.index)][["Provincia", "Lat", "Lon"]]
        prov = coords["Provincia"].tolist()
        lat = coords["Lat"].tolist()
        lon = coords["Lon"].tolist()

        self.df.insert(0, "Provincia", value=prov)
        self.df.insert(1, "Lat", value=lat)
        self.df.insert(2, "Lon", value=lon)

        return self.df
