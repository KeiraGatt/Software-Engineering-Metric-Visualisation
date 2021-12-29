#
# SOFTWARE ENGINEERING (CSU33012)
#
# Data Visualisation Project
#
# Create Geo Map for Country's Top Github Repository
#
# Keira Gatt (#19334557)
#

import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output,State
import requests
from apps import global_vars as gl
from apps import Country_List as country_list
from app import app

db = gl.mongo_client[gl.db_name]  # Access DB
col = db[gl.map_col]


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

    docs.to_csv(gl.map_csv, ",") # Create CSV file
    df = pd.read_csv(gl.map_csv)
    df.reset_index(inplace=True)

    return df

# App layout
layout=html.Div([

    html.H1("Country's Top Repository", style={'text-align': 'center', 'background-color': gl.colours['blue'], 'font-family': gl.font}), # html header title
    html.Br(),

    html.Div( [
        dcc.Dropdown( id='dropdown', options=country_list.country_array, value='Ireland', placeholder='Select a Country...', style={'top': '5%',
                    'height': '25px', 'position': 'relative', 'left': '2%', 'font-family': gl.font}),
        ],

        style={"width": "15%", 'float': 'left', 'margin': 'auto'},
    ),

    html.Div( [
        html.Button('Submit', id='input_button1', n_clicks=0,
                style={'background-color': gl.colours['orange'], 'height': '32px', 'margin': 'auto',
                       'position': 'relative', 'left': '1.5%', 'border-radius': '8px', 'font-family': gl.font}),

        dcc.Link(html.Button('Home', id='input_button2',
                         style={'background-color': gl.colours['orange'], 'height': '32px', 'margin': 'auto',
                            'position': 'relative', 'left': '2.5%', 'border-radius': '8px', 'font-family': gl.font}), href=gl.refs['home']),
        ],
    ),

    html.Br(),
    html.Label("Select Country from Drop Down List",
               style={'text-align': 'left', 'background-color': gl.colours['blue'], 'position': 'relative', 'left' : '1%', 'font-family': gl.font}),

    html.Br(),
    html.Hr(style={'border-top': '3px solid #bbb'}),
    html.Br(),

    html.Div(id='Top_Repos_container', children=[], style={'width': '80vw', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto', 'font-family': gl.font}),
    html.Br(),

    dcc.Graph(id='Top_Repos_map', figure={}, style={'width': '80vw', 'height': '70vh', 'display': 'block', 'margin-left': 'auto',
                                                    'margin-right': 'auto', 'font-family': gl.font, 'font-weight': 'bold', 'font-size': '100%'})

])


# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='Top_Repos_container', component_property='children'),
     Output(component_id='Top_Repos_map', component_property='figure')],
    [Input(component_id='input_button1', component_property='n_clicks'),
     State(component_id='dropdown', component_property='value'),
    Input(component_id='input_button2', component_property='n_clicks')]
)


def update_graph(n_clicks1, option_slctd, n_clicks2):

    update_flag = False

    gl.delete_docs(col)  # Delete redundant docs after use

    if option_slctd is not None:

        get_Github_data(option_slctd)     # Call function to retrieve & process Github API data
        df = connect_Mongo()            # Connect to Client-side copy of DB

        dff = df.copy()                 # Make a copy of dataframe

        if "invalid" in dff:            # check if user input was invalid
            container = "** Cannot retrieve data for Country! [Displaying results for default Country (Ireland)]"
        else:
            update_flag = True
            container = "Displaying results for Country : {}".format(option_slctd)

    else:                               # Empty input string
        container = "** Country not specified! [Displaying results for default Country (Ireland)]"

    if not update_flag:                 # On error, use default values

        gl.delete_docs(col)
        option_slctd = "Ireland"
        get_Github_data(option_slctd)  # Call function to retreive & process Github API data
        df = connect_Mongo()  # Connect to Client-side copy of DB

        dff = df.copy()  # Make a copy of dataframe

    dff = dff[dff["country"] == option_slctd]  # Retrieve Country field in dataframe

    # Display Map

    fig = px.choropleth(
        data_frame=dff,
        locationmode="country names",
        locations= dff["country"],
        hover_data=dff[['name', 'language']],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        template='plotly_dark'
    )

    # Increase map resolution
    fig.update_layout({
        'geo': {
            'resolution': 50
        }
     })

    fig.update_layout(showlegend=False)

    return container, fig


# find top user from country
def get_top_user(country):

    url = "https://api.github.com/search/users?q=location:" + country + "&sort=stars&page=1&per_page=1"

    return requests.get(url, headers=gl.headers).json()

# find top user's top repo
def get_top_repo(username):

    url = "https://api.github.com/search/repositories?q=user:" + username + "&sort=stars&per_page=1"
    return requests.get(url, headers=gl.headers).json()


def error_check(repo):
    flag = True  # check if info is valid for user
    if "items" in repo:
        if not repo['items']:
            flag = False
    else:
        flag = False

    return flag


def tidy_repo(repo):
    repo.pop("total_count")  # remove irrelevant repo details
    repo.pop("incomplete_results")
    record = repo["items"][0] # dictionary containing info about user's repo
    if record['language'] is None: # if no language is specified for the repo -> set to unspecified
        record['language'] = "Unspecified"

    return record


# Connect to Github REST API and process data
def get_Github_data(country_choice):

    top_user = get_top_user(country_choice)

    # check all necessary data is present
    if error_check(top_user): # country is valid

        repos_dicts = top_user['items']
        top_repo = {}           # initialise empty dict
        top_repo = get_top_repo(repos_dicts[0]['login']) # get top user's top repo

        if error_check(top_repo): # user is valid
            record = tidy_repo(top_repo)  # get repo ready to add to collection
            col.insert_one(record)  # add to collection
            col.update_many({"country": {"$exists": False}}, {"$set": {"country": country_choice}})
        else: # user invalid
            record = {'invalid': 'True'}
            col.insert_one(record)

    else: # country is invalid
        record = {'invalid' : 'True'}
        col.insert_one(record)
