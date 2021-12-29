#
# SOFTWARE ENGINEERING (CSU33012)
#
# Data Visualisation Project
#
# Present Github User Most Used Languages as a Bar Chart
#
# Keira Gatt (#19334557)
#

import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State
import requests
import json
from apps import global_vars as gl
from app import app

db = gl.mongo_client[gl.db_name]  # Access DB
col = db[gl.barchart_col]


# Connect Frontend to MongoDB Server
def connect_Mongo():

    cursor = col.find()
    mongo_docs = list(cursor)
    docs = pd.DataFrame(columns=[])

# Iterate through docs in collection and make a panda dataframe
    for num, doc in enumerate( mongo_docs ):
        doc["_id"] = str(doc["_id"])
        doc_id = doc["_id"]
        series_obj = pd.Series(doc, name=doc_id)
        docs = docs.append(series_obj)

    docs.to_csv(gl.barchart_csv, ",") # Create CSV file
    df = pd.read_csv(gl.barchart_csv)
    df.reset_index(inplace=True)

    return df

# App layout
layout=html.Div([

    html.H1("Languages Most Used by User", style={'text-align': 'center', 'background-color': gl.colours['blue'], 'font-family': gl.font}), # html header title
    html.Br(),

    dcc.Textarea(id='username',placeholder='Enter a username...',value='KeiraGatt',style={'width': '10%', 'height': '25px',
                                                                                            'position': 'relative', 'left': '20px', 'font-family': gl.font}),

    html.Button('Submit', id='input_button1', n_clicks=0,
                style={'background-color': gl.colours['orange'], 'top': '-10px', 'height': '32px',
                       'position': 'relative', 'left': '40px', 'border-radius': '8px', 'font-family': gl.font}),

    dcc.Link(html.Button('Home', id='input_button2',
                         style={'background-color': gl.colours['orange'], 'top': '-10px', 'height': '32px',
                                'position': 'relative', 'left': '60px',
                                'border-radius': '8px', 'font-family': gl.font}), href=gl.refs['home']),

    html.Br(),
    html.Label("Enter a Github Username",
               style={'text-align': 'left', 'background-color': gl.colours['blue'], 'position': 'relative', 'left' : '20px', 'font-family': gl.font}),

    html.Br(),
    html.Hr(style={'border-top': '3px solid #bbb'}),
    html.Br(),

    html.Div(id='User_Lang_container', children=[], style={'width': '50vw', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto', 'font-family': gl.font}),
    html.Br(),

    dcc.Graph(id='User_Lang_barchart', figure={}, style={'width': '50vw', 'height': '70vh', 'display': 'block', 'margin-left': 'auto',
                                                         'margin-right': 'auto', 'font-family': gl.font, 'font-weight': 'bold', 'font-size': '100%'})

])

# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='User_Lang_container', component_property='children'),
     Output(component_id='User_Lang_barchart', component_property='figure')],
    [Input(component_id='input_button1', component_property='n_clicks'),
     Input(component_id='input_button2', component_property='n_clicks'),
    State(component_id='username', component_property='value')]
)
def update_graph(n_clicks1, n_clicks2, username):

    update_flag = True

    if len(username) > 0:

        container = "Barchart showing Languages most used by User : {}".format(username)
        get_Github_data(username)  # Call function to retrieve & process Github API data
        df = connect_Mongo()       # Connect to Client-side copy of DB
        dff = df.copy()            # Make a copy of dataframe

        if "Invalid" in dff:  # check if user input was invalid
            update_flag = False

            if "Repos" in dff.values:
                container = "** User has no repositories! [Displaying results for default Username (KeiraGatt)]"
            elif "Username" in dff.values:
                container = "** Username is invalid! [Displaying results for default Username (KeiraGatt)]"
            else:
                container = "** Username cannot be resolved! [Displaying results for default Username (KeiraGatt)]"

    else:  # Empty input strings
        update_flag = False
        container = "** Username is missing! [Displaying results for default Username (KeiraGatt)]"

    if not update_flag:         # On error, use default values

            gl.delete_docs(col)
            username = 'KeiraGatt'

            get_Github_data(username)  # Call function to retrieve & process Github API data
            df = connect_Mongo()  # Connect to Client-side copy of DB
            dff = df.copy()  # Make a copy of dataframe

    list_lang = list((dff['Languages']))    # Retrieve Language field in dataframe

    new_list = list_lang[0].replace("'", '"')   # Format data to change into a dict
    res = json.loads(new_list)

    fig = px.bar(data_frame=dff, x=res.values(), y=res.keys(), labels=dict(x=" # Bytes", y="Language"))  # Display BarChart
    fig.update_traces(width=0.3)
    fig.update_xaxes(title_font=dict(size=18, family=gl.font, color=gl.colours['orange']))
    fig.update_yaxes(title_font=dict(size=18, family=gl.font, color=gl.colours['orange']))

    gl.delete_docs(col) # Delete redundant docs after use

    return container, fig


# Connect to Github REST API and process data
def get_Github_data(username):

    repos_used = []
    langs_used = {}

    url = "https://api.github.com/users/" + username + "/repos" # Retrieve user's repositories
    repo = requests.get(url, headers=gl.headers).json()

    if repo and not ("message" in repo):
    # For each repository get number of bytes of every language used
        for repo_no in range(len(repo)):
            url = "https://api.github.com/repos/" + username + "/" + repo[repo_no]['name'] + "/languages"
            langs = requests.get(url, headers=gl.headers).json()
            langs_used = add_to_list(langs, langs_used)

            repos_used.append(repo[repo_no]['name'])

    # Add to DB
        record = {'Username': username}
        record['Languages'] = langs_used
        if not bool(langs_used):  # if dict is empty ( User only has empty Repos)
            record = {'Username': username}
            record['Invalid'] = 'Repos'
    else:
        record = {'Username': username}
        if not repo: # User has no Repos
            record['Invalid'] = 'Repos'
        else: # Username is invalid
            record['Invalid'] = 'Username'

    col.insert_one(record)


# For all user's repos find total bytes of every language used
def add_to_list(langs, langs_used):

    for key in langs.keys():
        if key in langs_used.keys():
            langs_used[key] = langs.get(key) + langs_used[key]
        else:
            langs_used[key] = langs.get(key)

    return langs_used
