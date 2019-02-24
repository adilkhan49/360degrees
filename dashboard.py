import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_table

from werkzeug.serving import run_simple


import pandas as pd
import numpy as np
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1TXvsECM537MMj1nVL-wcpXbSUbOj2-S6JVndcb2mOTE'
SAMPLE_RANGE_NAME = 'New typeform!A:Z'

prod = False

def refresh():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    df = pd.DataFrame(values[1:], columns=values[0])
    df['Submitted At'] = pd.to_datetime(df['Submitted At'])

# from pyproj import Proj, transform
# geolocator = Nominatim(user_agent="none")
# def LongLat_to_EN(long, lat):
#         easting, northing = transform(
#         Proj(init='epsg:4326'), Proj(init='epsg:3857'), long, lat)
#         return easting, northing
    lats, longs = [], []

    for loc in df["Where do you live? Give me your postcode, please"]:
        try:
            location = geolocator.geocode(loc)
            lats.append(location.latitude)
            longs.append(location.longitude)
        except:
            lats.append(np.nan)
            longs.append(np.nan)

    # coordsEN=[LongLat_to_EN(longs[i],lats[i]) for i in range(len(df))]
    # x = [coordsEN[i][0] for i in range(len(coordsEN))]
    # y =[ coordsEN[i][1] for i in range(len(coordsEN))]
    df['x'], df['y'] = longs, lats

    return df



image_filename = '/Users/Adil/Documents/Data Science/NLTK/wc.png'
df = refresh()
if prod:
    app = dash.Dash()
# app = dash.Dash(__name__, external_stylesheets='external_css.css')
if not prod:
    app = dash.Dash(__name__, external_stylesheets=['external_css.css'])
contact = pd.read_csv('contact.csv')

options = [{'label': i, 'value': i} for i in df["What's your name?"].unique()]

    
app.layout = html.Div([
    
    html.H1(
        '360 Degrees'
    ),
    
    html.Div(
        '\nInsights and analytics dashboard\n'
    ),
    
    html.Div([
        dcc.Dropdown(
            id='my-dropdown1',
            options=options,
            multi=False,
            placeholder='Please select a client'

    ),
        
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in contact.columns],
    data=contact.to_dict("rows"),
)        
        
    ]
        
        , style={'width': '20%', 'display': 'inline-block','vertical-align': 'middle'}),    

    html.H3(
        'Hours Spent Researching.'
    ),
    
    
    html.Div(
        id='my-graph1'
    , style={'width': '50%', 'display': 'inline-block','vertical-align': 'right'}),

    html.Div(
        id='my-graph2'
    , style={'width': '50%', 'display': 'inline-block','vertical-align': 'right'})
    
    
])

@app.callback(
    Output(component_id='table', component_property='data'),
    [Input(component_id='my-dropdown1', component_property='value'),
    ]
)

def update_graph(selected_dropdown_value):

    data=pd.read_csv('contact.csv')
    return data[data['NAME']==selected_dropdown_value].to_dict("rows")



@app.callback(
    Output(component_id='my-graph1', component_property='children'),
    [Input(component_id='my-dropdown1', component_property='value'),
    ]
)

def update_graph(selected_dropdown_value):
    df=refresh()
    
    end=df[df["What's your name?"]==selected_dropdown_value]['Submitted At'].max()
    periods = len(df[df["What's your name?"]==selected_dropdown_value])
    try:
        data=[go.Scatter(
            x=pd.date_range(end=end, periods=periods, freq='1W'),
            y=df[df["What's your name?"]==selected_dropdown_value][df.columns[2]],
                        )]
    
        return     dcc.Graph(id='outgraph1',
            figure=go.Figure(data=data,
            layout=go.Layout(margin= {'l': 10, 'b': 20, 't': 0, 'r': 0})
  
                            ))
    except TypeError:
        return None 
    
@app.callback(
    Output(component_id='my-graph2', component_property='children'),
    [Input(component_id='my-dropdown1', component_property='value'),
    ]
)

def update_graph(selected_dropdown_value):
    df=refresh()
    
    end=df[df["What's your name?"]==selected_dropdown_value]['Submitted At'].max()
    periods = len(df[df["What's your name?"]==selected_dropdown_value])
    try:
        data=[go.Scatter(
            x=pd.date_range(end=end, periods=periods, freq='1W'),
            y=df[df["What's your name?"]==selected_dropdown_value][df.columns[3]],
                        )]
    
        return     dcc.Graph(id='outgraph2',
            figure=go.Figure(data=data,
            layout=go.Layout(margin= {'l': 10, 'b': 20, 't': 0, 'r': 0})
  
                            ))
    except TypeError:
        return None     

#   if prod:


if prod:
    run_simple('localhost', 8080, app.server, use_reloader=True, use_debugger=True)
else:
    run_simple('localhost', 8080, app.server,
               use_reloader=True, use_debugger=True)
# if __name__ != '__main__':
#     app.run_server(debug=True,port=8056)    
# if __name__ == '__main__':
#     app.run_server(port = 8052)
