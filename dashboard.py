import yaml
import pandas as pd
from tqdm import tqdm
from time import sleep
from src.calculations import *
from calendar import monthrange
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


class Dashboard:
    def __init__(self, graphs=config["graphs"]):
        """
        Recibe como parámetro el booleano graphs. Por defecto es True.
        Para pruebas, asignar False al llamar a la clase, cuando se quiera
        obtener SOLO los datos.
        """
        self.data_path = config["paths"]["data"]
        self.umb_path = config["paths"]["umbrales"]
        self.get_day_month()
        self.get_files()

        # Llamar a las funciones auxiliares y mostrar mensajes después de cada una
        self.read_lvera()
        self.get_last_data()
        self.summary_data()

        if graphs:
            methods = [
                self.get_time_series(),
                self.get_tables(),
                self.get_anomalies(),
                self.get_pp_by_province_map(),
                self.get_dec_maps(),
                self.get_meteorogram(),
                self.get_today_maps(),
            ]

            for i in tqdm(range(len(methods)), desc="Generando gráficos", colour="red"):
                for method in methods:
                    method
                    sleep(0.1)

    def get_files(self):
        """
        Método para leer rutas de archivos necesarios para el Dashboard.
        Deben permanecer en las carpetas predefinidas.
        """
        self.file = config["files"]["list"]
        self.file_w_normals = config["files"]["normals"]
        self.dec_file = config["files"]["decadiarias"]
        self.mapbox_token = open(config["files"]["mapbox_token"]).read()

    def read_lvera(self):
        """
        Este método importa la función lvera para la recolección de datos de la web.
        """
        self.data = lvera()

        for i in self.data.keys():
            self.data[i]["Tmax"] = self.data[i]["Tmax"].astype(float)
            self.data[i]["Tmin"] = self.data[i]["Tmin"].astype(float)
            self.data[i]["PP"] = self.data[i]["PP"].astype(float)

            self.data[i].replace(-999.0, np.nan, inplace=True)
            self.data[i].replace(-999, np.nan, inplace=True)
            self.data[i].replace(-888, 0.01, inplace=True)

        dataframes = {}
        for var in ["Tmin", "Tmax", "PP"]:
            var_data = {}
            for st in self.data.keys():
                var_data[st] = self.data[st][var].values.tolist()
                var_data["Fecha"] = self.data[st]["Fecha"].tolist()

            df = pd.DataFrame.from_dict(var_data)
            df.set_index("Fecha", inplace=True)
            dataframes[var] = df

        self.dataframes = dataframes
        self.mx = dataframes["Tmax"]
        self.mn = dataframes["Tmin"]
        self.pp = dataframes["PP"]

    def get_last_data(self):
        """
        Obtiene un dataframe con los datos de las últimas 24 horas.
        """
        this_month, _, _, _ = self.filter_month()

        last_data = {
            "ESTACIONES": self.mn.columns,
            "TMIN": self.mn[
                (self.mn.index.day == self.day)
                & (self.mn.index.month == self.this_month)
            ]
            .values[-1]
            .tolist(),
            "TMAX": self.mx[
                (self.mx.index.day == self.yday) & (self.mx.index.month == this_month)
            ]
            .values[0]
            .tolist(),
            "PP": self.pp[
                (self.pp.index.day == self.yday) & (self.pp.index.month == this_month)
            ]
            .values[0]
            .tolist(),
        }

        last_data_df = pd.DataFrame(last_data)
        last_data_df.set_index("ESTACIONES", inplace=True)
        last_data_df = Utils(last_data_df, self.file).add_lat_lon()

        self.last_data_df = last_data_df

    def get_day_month(self):
        """
        Método para determinar días, meses, cantidad de días del mes, etc.
        """
        self.today = datetime.now()
        self.day = self.today.day
        self.today_date = self.today.strftime("%d-%b-%Y")
        self.year = self.today.year
        self.this_month = self.today.month
        self.this_month_days = monthrange(self.year, self.this_month)[1]
        self.this_month_days_list = list(map(str, range(1, self.this_month_days + 1)))

        self.prev_month = self.today - relativedelta(months=1)
        self.yday = (self.today - timedelta(days=1)).day
        self.yday_date = (self.today - timedelta(days=1)).strftime("%d-%b-%Y")
        self.past_month = self.prev_month.month
        self.past_month_days = monthrange(self.year, self.past_month)[1]
        self.past_month_days_list = list(map(str, range(1, self.past_month_days + 1)))

    def filter_month(self):
        """
        Método importante. Determina el mes de acuerdo al día para evitar vacíos innecesarios
        en el dashboard. Por ejemplo, en el día 1 de cada mes, solo se tiene un valor (tmin)
        mas aún no se cuenta con tmax o pp, aunque estos sí cuentan con datos del mes anterior
        completos. Por ello, cuando el día actual sea 1, el mes actual (this_month) para las
        las variables 'tmax' o 'pp' aún será el anterior, y todo lo contrario cuando sea cualquier
        otro día.

        Parámetros:
        this_month: mes actual o anterior, dependiendo de la variable.
        this_month_days_list: lista con días del mes en tipo string.
        day: día actual o anterior, dependiendo de la variable y el día.
        today_date: fecha actual o anterior, dependiendo de la variable, en formatro string.
        """
        if self.day == 1:
            month = self.past_month
            days_list = self.past_month_days_list
            day = self.yday
            date_str = self.yday_date
        else:
            month = self.this_month
            days_list = self.this_month_days_list
            day = self.day
            date_str = self.today_date

        return month, days_list, day, date_str

    def get_monthly_means(self, var, df, this_month):
        """
        Este método filtra los últimos 45 datos recibidos por Dashboard para calcular
        los promedios y acumulados del mes actual dependiendo de la variable.
        """
        var = var.lower()
        this_month, _, _, _ = self.filter_month()

        # Hacer filtro de estaciones que tienen normales
        if var == "tmax":
            df = df[df.index.month == this_month]
            df = pd.DataFrame(columns=["Mean"], data=df.mean(axis=0).round(1))
        elif var == "tmin":
            df = df[df.index.month == self.this_month]
            df = pd.DataFrame(columns=["Mean"], data=df.mean(axis=0).round(1))
        elif var == "pp":
            df = df[df.index.month == this_month]
            df = pd.DataFrame(columns=["Sum"], data=df.sum(axis=0).round(1))
        else:
            ValueError("Variable no soportada.")
        return df

    def summary_data(self):
        """
        Calcula los promedios o acumulados mensuales por cada variable.
        """
        this_month, _, _, _ = self.filter_month()

        self.mx_mean = self.get_monthly_means("tmax", self.mx, this_month)
        self.mn_mean = self.get_monthly_means("tmin", self.mn, self.this_month)
        self.pp_sum = self.get_monthly_means("pp", self.pp, this_month)

    def get_time_series(self):
        """
        Genera los gráficos de series de tiempo o barras, según la variable.
        """
        this_month, _, day, _ = self.filter_month()
        self.fig_mx = series("tmax", self.mx, this_month, day)
        self.fig_mn = series("tmin", self.mn, self.this_month, self.day)
        self.fig_pp = series("pp", self.pp, this_month, day)

    def get_tables(self):
        """
        Genera las tablas de caracterización para las 3 variables.
        """
        this_month, this_month_days_list, _, _ = self.filter_month()
        self.ctmax = Clasification(
            "tmax", self.mx, this_month, this_month_days_list, self.umb_path
        ).style_tmax()
        self.ctmin = Clasification(
            "tmin", self.mn, self.this_month, self.this_month_days_list, self.umb_path
        ).style_tmin()
        self.cpp = Clasification(
            "pp", self.pp, this_month, this_month_days_list, self.umb_path
        ).style_pp()

    def get_anomalies(self):
        """
        Genera los gráficos de barras para las anomalías mensuales.
        """
        this_month, _, _, today_date = self.filter_month()

        anom_mx = Anomalies(
            "tmax", self.mx_mean, this_month, self.file, self.file_w_normals
        )
        anom_mn = Anomalies(
            "tmin", self.mn_mean, self.this_month, self.file, self.file_w_normals
        )
        anom_pp = Anomalies(
            "pp", self.pp_sum, this_month, self.file, self.file_w_normals
        )

        self.amx = anom_mx.bars_fig(today_date)
        self.amn = anom_mn.bars_fig(self.today_date)
        self.app = anom_pp.bars_fig(today_date)

        self.map_amx = anom_mx.maps(self.mapbox_token)
        self.map_amn = anom_mn.maps(self.mapbox_token)
        self.map_app = anom_pp.maps(self.mapbox_token)

    def get_pp_by_province_map(self):
        """
        Genera el mapa de precipitación acumulada mensual por provincia.
        """
        # Añadiendo provincias y coordenadas
        pp_sum = Utils(self.pp_sum, self.file).add_lat_lon_prov()
        pp_sum = pp_sum.rename_axis("Estaciones").reset_index()

        # Calculando suma de precipitación por provincia
        sum_by_prov = pp_sum.groupby("Provincia").sum().reset_index()
        # sum_by_prov["size"] = 20

        opt = {
            "Provincia": True,
            "Lat": False,
            "Lon": False,
            "Sum": True,
        }  # , "size": False}

        mapbx = px.scatter_mapbox(
            sum_by_prov,
            lat="Lat",
            lon="Lon",
            color="Provincia",
            size="Sum",
            size_max=30,
            color_discrete_sequence=px.colors.qualitative.Bold,
            hover_data=opt,
            height=500,
            width=600,
        )

        mapbx.update_layout(
            hovermode="closest",
            autosize=False,
            mapbox=dict(
                accesstoken=self.mapbox_token,
                bearing=0,
                center=go.layout.mapbox.Center(lat=-7.16, lon=-78.49),
                style="light",
                pitch=0,
                zoom=8,
            ),
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=False,
        )

        self.pp_accum = mapbx

    def get_dec_maps(self):
        """
        Genera los mapas de anomalías por decadiaria.
        """
        this_month, _, _, _ = self.filter_month()

        self.d1 = Decadiarias(self.pp, this_month, self.file, self.dec_file).maps(
            "d1", self.mapbox_token
        )
        self.d2 = Decadiarias(self.pp, this_month, self.file, self.dec_file).maps(
            "d2", self.mapbox_token
        )
        self.d3 = Decadiarias(self.pp, this_month, self.file, self.dec_file).maps(
            "d3", self.mapbox_token
        )

    def get_meteorogram(self):
        last_data = LastData(self.last_data_df)
        self.meteogram = last_data.meteorogram()

    def get_today_maps(self):
        last_data = LastData(self.last_data_df)
        self.map_last_tmin = last_data.map_temps("tmin", self.mapbox_token)
        self.map_last_tmax = last_data.map_temps("tmax", self.mapbox_token)
        self.map_last_pp = last_data.map_pp(self.mapbox_token)
