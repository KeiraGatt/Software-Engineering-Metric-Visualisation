#
# SOFTWARE ENGINEERING (CSU33012)
#
# Data Visualisation Project
#
# Present Github User Repo Language Breakdown as Pie Charts
#
# Keira Gatt (#19334557)
#

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State
from plotly.subplots import make_subplots
import requests
import json
from apps import global_vars as gl
from app import app

db = gl.mongo_client[gl.db_name]  # Access DB
col = db[gl.piechart_col]


# Connect Frontend to local host MongoDB
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

    docs.to_csv(gl.piechart_csv, ",") # Create CSV file
    df = pd.read_csv(gl.piechart_csv)
    df.reset_index(inplace=True)

    return df

# App layout
layout=html.Div([

    html.H1("Repo Language Breakdown", style={'text-align': 'center', 'background-color': gl.colours['blue'], 'font-family': gl.font}), # html header title
    html.Br(),

    dcc.Textarea(id='username', placeholder='Enter a username...', value='KeiraGatt', style={'width': '10%', 'height': '25px','position': 'relative', 'left': '20px', 'font-family': gl.font}),
    dcc.Textarea(id='repo_name',placeholder='Enter a Github repo...',value='LowestCommonAncestor',style={'width': '15%', 'height': '25px', 'position': 'relative', 'left': '55px','font-family': gl.font}),

    html.Button('Submit', id='input_button1', n_clicks=0, style={'background-color': gl.colours['orange'], 'top': '-10px', 'height': '32px', 'position':'relative', 'left': '90px', 'border-radius': '8px', 'font-family': gl.font}),

    dcc.Link(html.Button('Home', id='input_button2', style={'background-color': gl.colours['orange'] , 'top': '-10px', 'height': '32px', 'position': 'relative', 'left': '110px',
                                                                                                                                                        'border-radius': '8px', 'font-family': gl.font}), href=gl.refs['home']),
       
    html.Br(),

    html.Label("Enter a Github Username and any number of their Github Repos separated by commas",
               style={'text-align': 'left', 'background-color': gl.colours['blue'], 'position': 'relative', 'left' : '20px', 'font-family': gl.font}),

    html.Br(),
    html.Hr(style={'border-top': '3px solid #bbb'}),
    html.Br(),
   
    html.Div(id='User_Repos_container', children=[], style={'width': '50vw', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto', 'font-family': gl.font}),
    html.Br(),

    dcc.Graph(id='User_Repos_piechart', figure={}, style={'width': '50vw', 'height': '70vh', 'display': 'block', 'margin-left': 'auto',
                                                          'margin-right': 'auto', 'font-family': gl.font, 'font-weight': 'bold', 'font-size': '100%'})

])

# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='User_Repos_container', component_property='children'),
     Output(component_id='User_Repos_piechart', component_property='figure')],
    [Input(component_id='input_button1', component_property='n_clicks'),
    Input(component_id='input_button2', component_property='n_clicks'),
    State(component_id='username', component_property='value'),
    State(component_id='repo_name', component_property='value')]
)
def update_graph(n_clicks1, n_clicks2, username, repo_name):

    update_flag = True

    if len(repo_name) > 0 and len(username) > 0:
        repo_name = repo_name.replace(' ', '')
        repo_name = repo_name.split(',')        # Seperate each repo inputted by user
        get_Github_data(username, repo_name)    # Call function to retreive & process Github API data
        df = connect_Mongo()                    # Connect to Client-side copy of DB
        dff = df.copy()                         # Make a copy of dataframe

        container = "The following data was found for {} : {}".format(username, list_to_string(repo_name))

        if "Invalid" in dff:  # check if user input was invalid
            update_flag = False

            if "Repo" in dff.values:
                container = "** These repositories are empty! [Displaying results for default Username & Repo (KeiraGatt : LowestCommonAncestor)]"
            elif "Username" in dff.values:
                container = "** The Username/Repo is incorrect! [Displaying results for default Username & Repo (KeiraGatt : LowestCommonAncestor)]"
            else:
                container = "** Username/Repo cannot be resolved! [Displaying results for default Username & Repo (KeiraGatt : LowestCommonAncestor)]"

    else: # Empty input strings
        update_flag = False
        container = "** The Username/Repo is missing! [Displaying results for default Username & Repo (KeiraGatt : LowestCommonAncestor)]"

    if not update_flag:         # On error, use default values
        username = 'KeiraGatt'
        repo_name = ['LowestCommonAncestor']

        gl.delete_docs(col)
        get_Github_data(username, repo_name)  # Call function to retreive & process Github API data
        df = connect_Mongo()  # Connect to Client-side copy of DB
        dff = df.copy()  # Make a copy of dataframe

    list_lang = list((dff['Languages']))    # Retrieve Language field in dataframe

    up_list_lang = [0] * len(list_lang) # Initialise 2 empty arrays to be used for formatting data
    dict_list_lang = [0] * len(list_lang)

    my_specs = []
    temp_speclist = [{"type": "Pie"}]

    # Create sub plots

    for y in range(len(list_lang)):
        my_specs.append(temp_speclist)

    fig = make_subplots(rows=len(list_lang), cols=1, specs=my_specs, subplot_titles=repo_name)

    for x in range(len(list_lang)):
        up_list_lang[x] = list_lang[x].replace("'", '"')
        dict_list_lang[x] = json.loads(up_list_lang[x])

        fig.add_trace(go.Pie(
            values=list(dict_list_lang[x].values()), labels=list(dict_list_lang[x].keys())
        ), row=(x+1), col=1)

        fig['data'][x]['hoverinfo'] = 'label'

    fig.update_layout(height=690)
    fig.update_annotations(yshift=20, xshift=200)
    fig.update_traces(hole=0.4)

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.01
    ))

    gl.delete_docs(col)  # Delete redundant docs from data frame

    return container, fig


# Covert list of strings to a string
def list_to_string(str_lst):
    # initialize an empty string
    str1 = ""

    # traverse list
    for x in range(len(str_lst)):
        if x is len(str_lst) - 1:
            str1 += str_lst[x]
        else:
            str1 += str_lst[x] + ', '

    return str1 # return string


# Retrieve data from GitHub API and insert into Mongo Atlas collection
def get_Github_data(username, repo_name):

    # For every repo specified; retrieve language breakdown
    for single_repo in repo_name:
        url = "https://api.github.com/repos/" + username + "/" + single_repo + "/languages"
        repo = requests.get(url, headers=gl.headers).json()

        if "message" in repo:
            record = {'Invalid': 'Username'} # invalid user or repo
        elif not repo:
            record = {'Invalid': 'Repo'} # empty repo found
        else:
            record = {'Languages': repo}

        col.insert_one(record)

