#
# SOFTWARE ENGINEERING (CSU33012)
#
# Data Visualisation Project
#
# Container for shared Global Variables
#
# Keira Gatt (#19334557)
#

import pymongo as py

font = 'cursive'
colours = {'blue' : 'rgb(0, 170, 255)', 'orange' : 'rgb(255, 119, 0)', 'black' : 'rgb(0,0,0)'}
refs = {'home' : "/", 'piechart' : "/apps/piechart", 'barchart' : "/apps/barchart", 'map' : "/apps/map"}

db_name = 'Data_Vis'
barchart_col = 'Barchart'
map_col = 'Map'
piechart_col = 'Piechart'

# Placeholders for access control and authorisation tokens

# mongo_client = py.MongoClient('mongodb+srv://<username:password>@datavisualization.gpyo0.mongodb.net/' + db_name + '?retryWrites=true&w=majority')
# access_token = '<GitHub Access Token'

headers = {'Authorization':"Token " + access_token}

barchart_csv = 'Barchart.csv'
map_csv = 'Map.csv'
piechart_csv = 'Piechart.csv'


# Delete all docs from specified collection
def delete_docs(col):
    col.delete_many({})
