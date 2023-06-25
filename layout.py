import yaml
import warnings

warnings.simplefilter("ignore", UserWarning)

from dashboard import Dashboard
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


ds = Dashboard()

card_body_style = {"textAlign": "center"}


def create_card(title):
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.H2(title),
                            ],
                            style=card_body_style,
                        )
                    ]
                )
            ),
        ]
    )


def res_text1():
    return create_card("Tmax, Tmin y PP diaria")


def res_text2():
    return create_card("Distribución espacial de Tmax, Tmin y PP")


def temp_text1():
    return create_card("Comportamiento diario")


def temp_text2():
    return create_card("Caracterización")


def temp_text3():
    return create_card("Anomalía mensual")


def temp_text4():
    return create_card("Mapa de anomalías")


def prp_text1():
    return create_card("Precipitación diaria")


def prp_text2():
    return create_card("Caracterización")


def prp_text3():
    return create_card("Anomalías mensuales")


def prp_text4():
    return create_card("1ra Decadiaria")


def prp_text5():
    return create_card("2da Decadiaria")


def prp_text6():
    return create_card("3ra Decadiaria")


def res():
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row([dbc.Col([res_text1()], width=12)], align="center"),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="graph1", figure=ds.meteogram)],
                                    width=12,
                                )
                            ],
                            align="center",
                        ),
                        html.Br(),
                        dbc.Row([dbc.Col([res_text2()], width=12)], align="center"),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="graph2", figure=ds.map_last_tmax)],
                                    width=4,
                                ),
                                dbc.Col(
                                    [dcc.Graph(id="graph3", figure=ds.map_last_tmin)],
                                    width=4,
                                ),
                                dbc.Col(
                                    [dcc.Graph(id="graph4", figure=ds.map_last_pp)],
                                    width=4,
                                ),
                            ]
                        ),
                    ]
                ),
                color="light",
            )
        ]
    )


def tmax():
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        # ------------------------Card1--------------------------
                        dbc.Row(
                            [
                                dbc.Col([temp_text1()], width=12),
                            ],
                            align="center",
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="graph5", figure=ds.fig_mx)], width=12
                                ),
                            ],
                            align="center",
                        ),
                        # -------------------------Card2-------------------------
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col([temp_text2()], width=12),
                            ],
                            align="center",
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col([ds.ctmax], width={"size": 12}),
                            ],
                            align="center",
                        ),
                        # -------------------------Card3-------------------------
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col([temp_text3()], width=8),
                                dbc.Col([temp_text4()], width=4),
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="graph6", figure=ds.amx)], width=8
                                ),
                                dbc.Col(
                                    [dcc.Graph(id="graph7", figure=ds.map_amx)], width=4
                                ),
                            ],
                            align="center",
                        ),
                    ]
                ),
                color="light",
            )
        ]
    )


def tmin():
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        # ------------------------Card1--------------------------
                        dbc.Row([dbc.Col([temp_text1()], width=12)], align="center"),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="graph8", figure=ds.fig_mn)], width=12
                                )
                            ],
                            align="center",
                        ),
                        # ------------------------Card2--------------------------
                        html.Br(),
                        dbc.Row([dbc.Col([temp_text2()], width=12)], align="center"),
                        html.Br(),
                        dbc.Row(
                            [dbc.Col([ds.ctmin], width={"size": 12})],
                            align="center",
                            justify="center",
                        ),
                        # ------------------------Card3--------------------------
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col([temp_text3()], width=8),
                                dbc.Col([temp_text4()], width=4),
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="graph9", figure=ds.amn)], width=8
                                ),
                                dbc.Col(
                                    [dcc.Graph(id="graph10", figure=ds.map_amn)],
                                    width=4,
                                ),
                            ],
                            align="center",
                        ),
                    ]
                ),
                color="light",
            )
        ]
    )


def pp():
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        # -----------------------------Card 1-------------------------------
                        dbc.Row(
                            [
                                dbc.Col([prp_text1()], width=12),
                            ],
                            align="center",
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="graph11", figure=ds.fig_pp)], width=8
                                ),
                                dbc.Col(
                                    [dcc.Graph(id="graph12", figure=ds.pp_accum)],
                                    width=4,
                                ),
                            ]
                        ),
                        # -----------------------------Card 2-------------------------------
                        html.Br(),
                        dbc.Row([dbc.Col([prp_text2()], width=12)], align="center"),
                        html.Br(),
                        dbc.Row(
                            [dbc.Col([ds.cpp], width={"size": 12})],
                            align="center",
                            justify="center",
                        ),
                        # -----------------------------Card 3-------------------------------
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [prp_text4()], width=4, style={"height": "50%"}
                                ),
                                dbc.Col(
                                    [prp_text5()], width=4, style={"height": "50%"}
                                ),
                                dbc.Col(
                                    [prp_text6()], width=4, style={"height": "50%"}
                                ),
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="graph13", figure=ds.d1)], width=4
                                ),
                                dbc.Col(
                                    [dcc.Graph(id="graph14", figure=ds.d2)], width=4
                                ),
                                dbc.Col(
                                    [dcc.Graph(id="graph15", figure=ds.d3)], width=4
                                ),
                            ]
                        ),
                        # -----------------------------Card 4-------------------------------
                        html.Br(),
                        dbc.Row([dbc.Col([prp_text3()], width=12)], align="center"),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="graph16", figure=ds.app)],
                                    width=8,
                                ),
                                dbc.Col(
                                    [dcc.Graph(id="graph17", figure=ds.map_app)],
                                    width=4,
                                ),
                            ]
                        ),
                    ]
                ),
                color="light",
            )
        ]
    )


def graf1():
    return dcc.Tab(
        label="Resumen 24 hrs",
        children=[res()],
        selected_style={
            "borderTop": "1px solid #d6d6d6",
            "borderBottom": "1px solid #d6d6d6",
            "backgroundColor": "#bfbfbf",
            "color": "white",
        },
    )


def graf2():
    return dcc.Tab(
        label="Temperatura máxima",
        children=[tmax()],
        selected_style={
            "borderTop": "1px solid #d6d6d6",
            "borderBottom": "1px solid #d6d6d6",
            "backgroundColor": "#f78d7b",
            "color": "white",
        },
    )


def graf3():
    return dcc.Tab(
        label="Temperatura mínima",
        children=[tmin()],
        selected_style={
            "borderTop": "1px solid #d6d6d6",
            "borderBottom": "1px solid #d6d6d6",
            "backgroundColor": "#4eadf3",
            "color": "white",
        },
    )


def graf4():
    return dcc.Tab(
        label="Precipitación",
        children=[pp()],
        selected_style={
            "borderTop": "1px solid #d6d6d6",
            "borderBottom": "1px solid #d6d6d6",
            "backgroundColor": "#a7ea52",
            "color": "white",
        },
    )
