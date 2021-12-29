#
# SOFTWARE ENGINEERING (CSU33012)
#
# Data Visualisation Project
#
# Deploy DV app as as server
#
# Keira Gatt (#19334557)
#

import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
