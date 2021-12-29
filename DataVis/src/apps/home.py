#
# SOFTWARE ENGINEERING (CSU33012)
#
# Data Visualisation Project
#
# Home page for DV website
#
# Keira Gatt (#19334557)
#

from dash import dcc, html, Input, Output
from apps import global_vars as gl
from app import app

# App layout

layout=html.Div(style={'backgroundColor': gl.colours['blue']}, children=[

    html.Div(id='home_container', children=[], style={'font-family': gl.font, 'font-size':'40px', 'position': 'relative', 'left': '20px'}),
    html.Br(),
    html.Img(src=app.get_asset_url('dv.png'), style={'position': 'relative', 'left': '10px'}),
    html.Br(),

    dcc.Link(html.Button('Pie Chart', id='choice_button1', style={'position': 'relative', 'display': 'flex', 'top': '80px', 'width': '20%', 'height': '50px',
        'background-color': gl.colours['orange'], 'color': gl.colours['black'], 'border-radius': '8px', 'font-family': gl.font, 'font-size':'20px',
        'margin-left': 'auto', 'margin-right': 'auto', 'justify-content': 'center', 'align-items': 'center'}), href=gl.refs['piechart']),

    dcc.Link(html.Button('Bar Chart', id='choice_button2', style={'position': 'relative', 'display': 'flex', 'top': '120px', 'width': '20%', 'height': '50px',
        'background-color': gl.colours['orange'], 'color': gl.colours['black'], 'border-radius': '8px', 'font-family': gl.font, 'font-size':'20px',
        'margin-left': 'auto', 'margin-right': 'auto', 'justify-content': 'center', 'align-items': 'center'}), href=gl.refs['barchart']),

    dcc.Link(html.Button('Map', id='choice_button3', style={'position': 'relative', 'display': 'flex', 'top': '160px', 'width': '20%', 'height': '50px',
        'background-color': gl.colours['orange'], 'color': gl.colours['black'], 'border-radius': '8px', 'font-family': gl.font, 'font-size':'20px',
        'margin-left': 'auto', 'margin-right': 'auto', 'justify-content': 'center', 'align-items': 'center'}), href=gl.refs['map']),

])

# Connect the Plotly graphs with Dash Components
@app.callback(Output(component_id='home_container', component_property='children'),
    [Input(component_id='choice_button1', component_property='n_clicks1'),
        Input(component_id='choice_button2', component_property='n_clicks2'),
        Input(component_id='choice_button3', component_property='n_clicks3')
    ]
)
def update_graph(n_clicks1, n_clicks2,n_clicks3):
     container = "Data Visualisation Project"
     return container

