#
# SOFTWARE ENGINEERING (CSU33012)
#
# Data Visualisation Project
#
# Startup declarations & logic for DV website
#
# Keira Gatt (#19334557)
#

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
from app import app
from apps import map, piechart, barchart, home

# Do not display HTTP logs on console (Flask default)

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/map':
        return map.layout
    elif pathname == '/apps/piechart':
        return piechart.layout
    elif pathname == '/apps/barchart':
        return barchart.layout
    else:
        return home.layout


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050, debug=False)
