import argparse
import datetime
import warnings

warnings.simplefilter("ignore", UserWarning)
import dash
import layout as layout
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import subprocess

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--daily", action="store_true")
parser.add_argument("--monthly", action="store_true")
args = parser.parse_args()

# Check if the daily report should be generated
if args.daily:
    print("Generando resumen diario")
    subprocess.run(["python", "src/daily_report.py"])

# Check if the monthly report should be generated
if args.monthly:
    if datetime.datetime.now().day == 1:
        print("No hay suficientes datos para generar el reporte mensual.")
    else:
        print("Generando resumen mensual")
        subprocess.run(["python", "src/monthly_report.py"])

external_stylesheets = [dbc.themes.JOURNAL]

# Build App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    [dcc.Tabs([layout.graf1(), layout.graf2(), layout.graf3(), layout.graf4()])]
)


# Run app
if __name__ == "__main__":
    app.run_server(port="8050")
