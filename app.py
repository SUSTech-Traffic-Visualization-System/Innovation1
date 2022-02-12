# Created by zyd on 2021/11/29 22:53.
import numpy as np
import plotly.graph_objects as go
from dash import dcc, State
from dash import html
from dash_extensions.enrich import MultiplexerTransform, DashProxy, Input, Output
import pydeck
import dash_deck as dd
import dash_uploader as du
import pandas as pd
import json
import os
import shpToJson as stj
import threePoint as tp
import pointToline2 as ptl2
import bufferSHP as bf
import planBProcessing as preB
import POLYGONshpSJOIN as pjs
import PointToPolygon as p2p
import LineToPolygon as l2p
from preprocessing import gps2grid

class layerObj:
    def __init__(self, name, layer: pydeck.Layer):
        self.name = name
        self.content = layer

pd.set_option('display.max_columns', None)
mapbox_api_token = os.getenv("MAPBOX_ACCESS_TOKEN")
lat = []
lon = []
xBNum = 0
yBNum = 0
fileUp = []
csvFileUp = []
layerList = []
gridLayer = []
chosenBarLayer = []
stackBarLayer = []
barMap = []
csvData = []
chosenData = []
barNP = []
barNPtmp = []
chosenBarNP = []
chosenBarNPtmp = []
number_out = []
number_in = []
flow_out = []
flow_in = []
has_changed = True
clickTime = -1
color_idx = 0
otherData = []
show_chos = False

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])
du.configure_upload(app, './DataUploadStorage/', use_upload_id=True)

def color_scale(val, maxVal):
    global color_idx
    per = 1.0 * val / maxVal
    if color_idx % 2 == 0:
        R = 255
        G = int((1 - per) * (244 - 31) + 31)
        B = 30
    elif color_idx % 2 == 1:
        R = 31
        G = int((1 - per) * (255 - 34) + 34)
        B = 255
    else:
        R = 125
        G = 125
        B = 125
    return [R, G, B]

INITIAL_VIEW_STATE = pydeck.ViewState(
    latitude=40.8,
    longitude=-74.00,
    zoom=8,
    max_zoom=16,
    pitch=45,
    bearing=0
)

r = pydeck.Deck(
    layers=[],
    initial_view_state=INITIAL_VIEW_STATE,
)

mapCom = dd.DeckGL(r.to_json(), id='deck_gl',
                   style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
                   mapboxKey=mapbox_api_token, tooltip=True)


lst = np.zeros(31)
for i in range(31):
    lst[i] = i

# Initialize Diagram 1
fig0 = go.Figure()
fig0.update_layout(
    xaxis_title = "Time",
    yaxis_title = "Flow"
)
fig0 = fig0.update_layout(height=200)
fig0.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99
))
fig0 = fig0.update_layout(height=230)
fig0 = fig0.update_layout(margin_l = 0, margin_r = 0, margin_t = 0, margin_b = 0)
fig0 = fig0.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

# Initialize Diagram 2
fig1 = go.Figure()
fig1.update_layout(
    xaxis_title = "The number of people in a grid in a month",
    yaxis_title = "The number of the grid"
)
fig1 = fig1.update_layout(height=300)
fig1.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99
))
fig1 = fig1.update_layout(margin_l = 0, margin_r = 0, margin_t = 0, margin_b = 0)
fig1 = fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

app.layout = html.Div(
    children=[
        html.Div(
            [
                html.Div(
                    [
                        # the logo image
                        html.Img(
                            src=app.get_asset_url("LOGO.png"),
                            id="plotly-image",
                            style={
                                "height": "auto",
                                "width": "350px",
                                "margin-bottom": "25px",
                                'position': 'relative'
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                # the title
                                html.H4(
                                    "Multi-Data Taxi Visualization System",
                                    style={"font-weight": "bold"},
                                ),
                            ]
                        )
                    ],
                    className="three column",
                    id="title",
                ),
                html.Div(
                    className="one-third column",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "5px"},
        ),
        html.Div(
            [
                # the map
                html.Div(
                    mapCom,
                    id='mapContainer'
                ),

            ],
            className="row flex-display",
        ),

        html.Div(
            [
                # Point Data To Point Data
                html.Div(
                    [
                        # the first method
                        html.H6("Point Data To Point Data",
                                style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),
                        html.Div(
                            [
                                # CSV File Uploader
                                html.B(' CSV File Uploader'),
                                du.Upload(id='csv_uploader',
                                          default_style={'height': '25px'},
                                          text='Click or drag file in to the square to upload a CSV file.',
                                          max_file_size=4096, filetypes=['csv'],
                                          cancel_button=True, pause_button=True, upload_id='csv'),
                                # GeoJSON File Uploader
                                html.B(' GeoJSON File Uploader'),
                                du.Upload(id='json_uploader',
                                          default_style={'height': '25px'},
                                          text='Click or drag file in to the square to upload a GeoJSON/JSON file.',
                                          max_file_size=2048, filetypes=['geojson'],
                                          cancel_button=False, pause_button=False, upload_id='geojson'),
                                # dropdown to choose geojson file
                                dcc.Dropdown(id="geoJsonFile",
                                             options=[]),
                                # the button to update all dropdowns
                                html.Button(id='update-dropdown', children='update dropdown',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                                # the button to show the chosen dropdown
                                html.Button(id='showGeoJson', children='show chosen GeoJson',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                                html.Br()
                            ],
                            style={'display': 'inline'}
                        ),

                        html.Div([
                                # Initial the longitude and the latitude of three point
                                html.I(' Origin point:'),
                                html.Br(),
                                dcc.Input(id='originLat', value=40.7062855, type='number',
                                          style={'height': '30px', 'width': '120px'}),
                                html.I('Latitude', style={"margin-right": "80px"}),
                                dcc.Input(id='originLon', value=-74.0315102, type='number',
                                          style={'height': '30px', 'width': '120px'}),
                                html.I('Longitude'),
                                html.Br(),
                                html.I(' Right-bottom corner:'),
                                html.Br(),
                                dcc.Input(id='xLat', value=40.6937655, type='number',
                                          style={'height': '30px', 'width': '120px'}),
                                html.I('Latitude', style={"margin-right": "80px"}),
                                dcc.Input(id='xLon', value=-73.9871323, type='number',
                                          style={'height': '30px', 'width': '120px'}),
                                html.I('Longitude'),
                                html.Br(),
                                html.I(' Left-upper corner:'),
                                html.Br(),
                                dcc.Input(id='yLat', value=40.7738362, type='number',
                                          style={'height': '30px', 'width': '120px'}),
                                html.I('Latitude', style={"margin-right": "80px"}),
                                dcc.Input(id='yLon', value=-73.9985950, type='number',
                                          style={'height': '30px', 'width': '120px'}),
                                html.I('Longitude'),
                                html.Br(),
                                # set the number of grids
                                dcc.Input(id='xBlockNum', value=8, type='number',
                                          style={'height': '30px', 'width': '60px'}),
                                html.I('Block number along X-axis',
                                       style={"margin-right": "15px"}),
                                dcc.Input(id='yBlockNum', value=16, type='number',
                                          style={'height': '30px', 'width': '60px'}),
                                html.I('Block number along Y-axis'),
                                html.Br(),
                                # the button to show the grids
                                html.Button(id='submit-button', type='submit', children='Submit',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                                # the button to show bar in the map
                                html.Button(id='display-bar-button', children='show bar',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                                # the button to reset all files and actions
                                html.Button(id='reset-button', children='Reset',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                                # the button to show the chosen bar in the map
                                html.Button(id='hide-data-button', children='show chosen bar',
                                        style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                            ],
                            style={'display': 'inline'}
                        ),
                        # the dropdown to choose data for showing the bar
                        html.Div(
                            id='third',
                            children=[
                                dcc.Dropdown(id="choose",
                                             options=[{'label': idx + 1, 'value': idx} for idx in range(len(csvData))],
                                             multi=True),
                                html.Div(id='output_div'),
                            ],
                            style={'display': 'inline'}
                        ),
                        html.Div(
                            id='nouse',
                            children='',
                            style={'display': 'none'}
                        ),
                        # the second method
                        html.Div(
                            id='planB',
                            children=[
                                html.B("----------------------------------------------------------------------------------------------------------------------------------------------------------------------"),
                                html.Br(),
                                html.B('Radius:  '),
                                dcc.Input(id='clusterRadius', value=0.05, type='number',
                                          style={"margin-right": "20px"}),
                                html.B('Minimum Sample Number:  '),
                                dcc.Input(id='minSamples', value=3, type='number'),
                                html.Br(),
                                html.B('Choose Base Data:  '),
                                dcc.Dropdown(id="baseDataC",
                                             options=[{'label': x, 'value': x} for x in csvFileUp]),
                                html.B('Choose Input Data:  '),
                                dcc.Dropdown(id="inDataC",
                                             options=[{'label': x, 'value': x} for x in csvFileUp]),
                                html.Button(id='showClusterButton', children='show Clustering Result',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                            ],
                            style={'display': 'inline'}
                        ),
                        # the third method
                        html.Div(
                            id='planC',
                            children=[
                                html.Br(),
                                html.B("----------------------------------------------------------------------------------------------------------------------------------------------------------------------"),
                                html.Br(),
                                html.B('Radius:(Miles)  '),
                                dcc.Input(id='bufferRadius', value=50, type='number'),
                                html.Br(),
                                html.B('Choose Base Data:  '),
                                dcc.Dropdown(id="baseDataB",
                                             options=[{'label': x, 'value': x} for x in csvFileUp]),
                                html.B('Choose Input Data:  '),
                                dcc.Dropdown(id="inDataB",
                                             options=[{'label': x, 'value': x} for x in csvFileUp]),
                                html.Button(id='showBufferButton', children='show Buffer Result',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                            ],
                            style={'display': 'inline'}
                        )
                    ],
                    className="pretty_container four columns",

                ),

                html.Div(
                    [
                        # Point Data To Polygon
                        html.H6("Point Data To Polygon",
                                style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),
                        html.Div(
                            id='pointToPolygon',
                            children=[
                                html.B('Choose GeoJson Data:  '),
                                dcc.Dropdown(id="geoJsonFile2",
                                             options=[{'label': x, 'value': x} for x in fileUp]),
                                html.B('Choose Input Data:  '),
                                dcc.Dropdown(id="chooseCsvP2P",
                                             options=[{'label': x, 'value': x} for x in csvFileUp],
                                             multi=False),
                                html.Button(id='showChosenP2PButton', children='show Chosen Result',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                                html.Br(),
                                html.Br(),
                                html.B("----------------------------------------------------------------------------------------------------------------------------------------------------------------------"),
                                html.Br(),
                            ],
                            style={'display': 'inline'}
                        ),

                        # Point Data to Line Data
                        html.H6("Point Data to Line Data",
                                style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),
                        html.Div(
                            id='pointToLine',
                            children=[
                                html.B('Choose Point Data:  '),
                                dcc.Dropdown(id="P2LDataPoint",
                                             options=[{'label': x, 'value': x} for x in csvFileUp]),
                                html.B('Choose Line Data:  '),
                                html.B('From:  '),
                                dcc.Dropdown(id="P2LDataFrom",
                                             options=[{'label': x, 'value': x} for x in csvFileUp]),
                                html.B('To:  '),
                                dcc.Dropdown(id="P2LDataTo",
                                             options=[{'label': x, 'value': x} for x in csvFileUp]),
                                html.Button(id='showP2LGButton', children='Show Grid Line Result!',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                                html.Br(),
                                html.B('Choose Input Data:  '),
                                html.Br(),
                                html.B('Radius:  '),
                                dcc.Input(id='clusterRadiusP2L', value=0.15, type='number'),
                                html.Br(),
                                html.B('Minimum Sample Number:  '),
                                dcc.Input(id='minSamplesP2L', value=3, type='number'),
                                html.Br(),
                                html.Button(id='showP2LCButton', children='Show Clustered Line Result!',
                                            style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),
                                html.Br(),
                                html.B('Min Line Count:  '),
                                dcc.Input(id='minCountL', value=0, type='number'),
                                html.Br(),
                                html.Br(),
                                html.B("----------------------------------------------------------------------------------------------------------------------------------------------------------------------"),
                                html.Br()
                            ],
                            style={'display': 'inline'}
                        ),
                # Line Data To Polygon
                html.H6("Line Data To Polygon",
                        style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),
                html.Div(
                    id='LineToPolygon',
                    children=[
                        html.B('Choose GeoJson Data:  '),
                        dcc.Dropdown(id="geoJsonFile3",
                                     options=[{'label': x, 'value': x} for x in fileUp]),
                        html.B('Choose Input Line Data:  '),
                        html.B('From:  '),
                        dcc.Dropdown(id="chooseFromCsvL2P",
                                     options=[{'label': x, 'value': x} for x in csvFileUp],
                                     multi=False),
                        html.B('To:  '),
                        dcc.Dropdown(id="chooseToCsvL2P",
                                     options=[{'label': x, 'value': x} for x in csvFileUp],
                                     multi=False),
                        html.B('Min Line Count:  '),
                        dcc.Input(id='minCountLP', value=0, type='number'),
                        html.Br(),
                        html.Button(id='showChosenL2PButton', children='show Chosen Result',
                                    style={'height': '30px', 'line-height': '30px', "margin-right": "12px"}),

                    ],
                    style={'display': 'inline'}
                ),
                    ],
                    className="pretty_container eight columns",

                ),
            ],
            className="row flex-display",
        ),

        # show the first diagram
        html.Div(
            [
                html.Div(
                    [
                        html.H6("Taxi Data Line Chart",
                                style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),

                        html.P("Select a grid", style={"font-weight": "bold", "text-align": "center"}),
                        dcc.Dropdown(id='grid_option'),

                        html.Div([dcc.Graph(id="line_chart", figure=fig0)],
                                 className="pretty_container twelve columns"),
                    ],
                    className="pretty_container four columns",

                ),
                # show the second diagram
                html.Div(
                    [html.H6("Taxi Data Histogram",
                             style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),

                    html.Div([dcc.Graph(id="histogram", figure=fig1)],
                             className="pretty_container twelve columns"),
                     ],

                    className="pretty_container eight columns",
                ),

            ],
            className="row flex-display",
        ),

        # the authors
        html.Div(
            [
                html.H6("Authors", style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),

                html.P(
                    "Zhang Yingdong (11910709@mail.sustech.edu.cn)  -  Chen Yonghao (11912203@mail.sustech.edu.cn)  -  Hu Wei (11912210@mail.sustech.edu.cn)",
                    style={"text-align": "center", "font-size": "10pt"}),

            ],
            className="row pretty_container",
        ),
        # the references
        html.Div(
            [
                html.H6("Sources", style={"margin-top": "0", "font-weight": "bold", "text-align": "center"}),
                dcc.Markdown(
                    """\
                         - 金思辰, 陶煜波, 严宇宇, & 戴浩然. (2019). 基于多维时空数据可视化的传染病模式分析. 计算机辅助设计与图形学学报, 31(2), 15.
                         - 余乐伟, 孙国道, 何贤国, & 梁荣华. (2013). 基于组件协同的时空数据可视分析系统. 浙江工业大学学报, 41(1), 10.
                         - Keim, D. A. ,  Hao, M. C. , &  Dayal, U. . (2002). Hierarchical Pixel Bar Charts. IEEE Educational Activities Department.
                         - Zhou, L. , &  Weiskopf, D. . (2018). Indexed-points parallel coordinates visualization of multivariate correlations. IEEE Transactions on Visualization and Computer Graphics, 1997-2010.
                         - Yuan, X. ,  Ren, D. ,  Wang, Z. , &  Guo, C. . (2013). Dimension projection matrix/tree: interactive subspace visual exploration and analysis of high dimensional data. IEEE Transactions on Visualization & Computer Graphics, 19(12), 2625.
                         - Guo, D. ,  Chen, J. ,  Maceachren, A. M. , &  Liao, K. . (2006). A visualization system for space-time and multivariate patterns (vis-stamp). IEEE Transactions on Visualization & Computer Graphics, 12(6), 1461-1474.
                        """
                    , style={"font-size": "10pt"}),

            ],
            className="row pretty_container",
        ),

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# reset all actions and files
@app.callback(
    Output('mapContainer', 'children'),
    Output('originLat', 'value'),
    Output('originLon', 'value'),
    Output('xLat', 'value'),
    Output('xLon', 'value'),
    Output('yLat', 'value'),
    Output('yLon', 'value'),
    Output('xBlockNum', 'value'),
    Output('yBlockNum', 'value'),
    Output('clusterRadius', 'value'),
    Output('minSamples', 'value'),
    Output('baseDataB', 'options'),
    Output('inDataB', 'options'),
    Output('choose', 'options'),
    Output('line_chart', 'figure'),
    Output('histogram', 'figure'),
    Output('grid_option', 'options'),
    Input(component_id='reset-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def reset(clicks):
    global has_changed, color_idx
    if clicks is not None:
        has_changed = True
        lat.clear()
        lon.clear()
        fileUp.clear()
        csvFileUp.clear()
        layerList.clear()
        gridLayer.clear()
        stackBarLayer.clear()
        csvData.clear()
        chosenBarNP.clear()
        chosenBarNPtmp.clear()
        chosenBarLayer.clear()
        chosenData.clear()
        barNP.clear()
        number_out.clear()
        number_in.clear()
        flow_out.clear()
        flow_in.clear()
        color_idx = 0
        otherData.clear()
    return mapCom, 40.7062855, -74.0315102, 40.6937655, -73.9871323, 40.7738362, -73.9985950, 8, 16, 1.5, 1, None, None, None, fig0, fig1, []


def make_new_CSV_layer(filename: str):
    print('make csv layer')
    p = './{}'.format(filename.replace('\\', '/'))
    print(p)
    try:
        data = pd.read_csv(p, parse_dates=['time'])
        csvData.append(data[['time', 'longitude', 'latitude']].copy())
    except ValueError:
        data = pd.read_csv(p, encoding='gbk')
        otherData.append(data.copy())
    print(0)


@app.callback(
    Output('mapContainer', 'children'),
    Input(component_id='showGeoJson', component_property='n_clicks'),
    State(component_id='geoJsonFile', component_property='value'),
    prevent_initial_call=True)
def update_Map(click, file):
    if file is not None and click is not None:
        print('make new map')
        try:
            with open(file, 'r') as f:
                newjs = json.load(f)
            newjson = pydeck.Layer(
                'GeoJsonLayer',
                newjs,
                opacity=0.8,
                stroked=True,
                filled=True,
                extruded=False,
                wireframe=False,
                lineWidthMinPixels=1,
                get_fill_color='[255, 255,146]',
                get_line_color=[0, 0, 0],
                pickable=True
            )
            t = pydeck.Deck(
                layers=[newjson],
                initial_view_state=INITIAL_VIEW_STATE,
            )
        except TypeError:
            t = None
        except IndexError:
            t = None
        tCom = dd.DeckGL(t.to_json(), id='deck_gl',
                         style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
                         mapboxKey=mapbox_api_token, tooltip=True)
        print('finish making new map')
        return tCom

# upload the geojson file
@du.callback(
    Output('nouse', 'children'),
    id='json_uploader',
)
def uploadedJsonFile(filenames):
    print('uploaded file:', filenames)
    if filenames is not None and len(filenames) > 0:
        fileUp.append(filenames[0])
    return 0

# upload the csv file
@du.callback(
    Output('nouse', 'children'),
    id='csv_uploader',
)
def uploadedCSVFile(filenames):
    global has_changed
    has_changed = True
    print('uploaded file:', filenames)
    if filenames is not None and len(filenames) > 0:
        make_new_CSV_layer(filenames[0])
        csvFileUp.append(filenames[0])
    print(len(csvData))
    print(len(csvFileUp))
    return 0

# update all dropdown
@app.callback(
    Output(component_id='baseDataC', component_property='options'),
    Output(component_id='inDataC', component_property='options'),
    Output(component_id='baseDataB', component_property='options'),
    Output(component_id='inDataB', component_property='options'),
    Output(component_id='choose', component_property='options'),
    Output(component_id='geoJsonFile', component_property='options'),
    Output(component_id='baseDataC', component_property='options'),
    Output(component_id='geoJsonFile2', component_property='options'),
    Output(component_id='chooseCsvP2P', component_property='options'),
    Output(component_id='P2LDataPoint', component_property='options'),
    Output(component_id='P2LDataFrom', component_property='options'),
    Output(component_id='P2LDataTo', component_property='options'),
    Output(component_id='geoJsonFile3', component_property='options'),
    Output(component_id='chooseFromCsvL2P', component_property='options'),
    Output(component_id='chooseToCsvL2P', component_property='options'),
    Input(component_id='update-dropdown', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_dropdown2(clicks):
    if clicks is not None:
        return [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': idx + 1, 'value': idx} for idx in range(len(csvData))], \
               [{'label': x, 'value': x} for x in fileUp], \
               [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': x, 'value': x} for x in fileUp], \
               [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': x, 'value': x} for x in fileUp], \
               [{'label': x, 'value': x} for x in csvFileUp], \
               [{'label': x, 'value': x} for x in csvFileUp]

# update the grids
@app.callback(Output('mapContainer', 'children'),
              Input('submit-button', 'n_clicks'),
              State('originLat', 'value'),
              State('originLon', 'value'),
              State('xLat', 'value'),
              State('xLon', 'value'),
              State('yLat', 'value'),
              State('yLon', 'value'),
              State('xBlockNum', 'value'),
              State('yBlockNum', 'value'),
              prevent_initial_call=True
              )
def update_Grid(clicks, input1, input2, input3, input4, input5, input6, input7, input8):
    global xBNum, yBNum, has_changed
    if clicks is not None:
        has_changed = True
        barNP.clear()
        gridLayer.clear()
        lat.clear()
        lat.append(input1)
        lat.append(input3)
        lat.append(input5)
        lon.clear()
        lon.append(input2)
        lon.append(input4)
        lon.append(input6)
        xBNum = input7
        yBNum = input8
        print('''Origin\'s coordinate: {}, {}\n
                Left-upper corner\'s coordinate: {}, {}\n
                Right-bottom corner\'s cooridinate: {}, {}\n
                X-Axis has {} blocks.\n
                Y-Axis has {} blocks.'''.format(lat[0], lon[0], lat[2], lon[2], lat[1], lon[1], xBNum, yBNum))
        tp.threePoint((lon[0], lat[0]), (lon[1], lat[1]), (lon[2], lat[2]), xBNum, yBNum)
        with open('./gridFile/POLYGON.geojson', 'r') as file:
            gridjs = json.load(file)
        upGrid = pydeck.Layer(
            'GeoJsonLayer',
            gridjs,
            opacity=0.8,
            stroked=True,
            filled=False,
            extruded=False,
            wireframe=False,
            lineWidthMinPixels=1,
            get_line_color=[255, 255, 120],
            pickable=True
        )
        gridLayer.clear()
        gridLayer.append(layerObj('grid', upGrid))
        print('make new map')
        try:
            t = pydeck.Deck(
                layers=[gridLayer[0].content],
                initial_view_state=INITIAL_VIEW_STATE,
            )
        except TypeError:
            print('error')
        except IndexError:
            print('error')
        else:
            tCom = dd.DeckGL(t.to_json(), id='deck_gl',
                             style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
                             mapboxKey=mapbox_api_token, tooltip=True)
            print('finish making new map')
            return tCom

# display the bar
@app.callback(
    Output(component_id='mapContainer', component_property='children'),
    Output(component_id='histogram', component_property='figure'),
    Output(component_id='grid_option', component_property='options'),
    Output(component_id='line_chart', component_property='figure'),
    Input(component_id='display-bar-button', component_property='n_clicks')
)
def display_bar(clicks):
    global xBNum, yBNum, has_changed, barMap, color_idx, number_out, number_in, fig_new1, fig_new2, Flow0, Flow1, show_chos
    show_chos = False
    if clicks is not None:
        if has_changed:
            color_idx = 0
            barMap.clear()
            if len(csvData) == 1:
                Flow0 = makeStackBarLayer(csvData[0])
                color_idx += 1
            else:
                Flow0 = makeStackBarLayer(csvData[0])
                color_idx += 1
                Flow1 = makeStackBarLayer(csvData[1])
                color_idx += 1
            barNP.clear()
            stackBarLayer.reverse()
            newMap = pydeck.Deck(
                layers=stackBarLayer,
                initial_view_state=INITIAL_VIEW_STATE,
            )
            stackBarMap = dd.DeckGL(newMap.to_json(), id='deck_gl',
                                    style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
                                    mapboxKey=mapbox_api_token, tooltip=True)
            if len(csvData) == 1:
                hist = go.Histogram(x=number_out, xbins={'size': 10}, marker={"opacity": 0.5})
                fig_new1 = go.Figure(hist)
                fig_new1.update_layout(
                    xaxis_title="The number of people in a grid in a month",
                    yaxis_title="The number of the grid"
                )
                fig_new1 = fig_new1.update_layout(height=300)
                fig_new1 = fig_new1.update_layout(margin_l=0, margin_r=0, margin_t=0, margin_b=0)
                fig_new1 = fig_new1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            else:
                hist1 = go.Histogram(x=number_out, xbins={'size': 10}, name='data1', marker={"opacity": 0.5})
                hist2 = go.Histogram(x=number_in, xbins={'size': 10}, name='data2', marker={"opacity": 0.5})
                fig_new1 = go.Figure(data=[hist1, hist2], layout={"barmode": "overlay"})
                fig_new1.update_layout(
                    xaxis_title="The number of people in a grid in a month",
                    yaxis_title="The number of the grid"
                )
                fig_new1 = fig_new1.update_layout(height=300)
                fig_new1.update_layout(legend=dict(
                    yanchor="top",  # y轴顶部
                    y=0.99,
                    xanchor="right",  # x轴靠右
                    x=0.99
                ))
                fig_new1 = fig_new1.update_layout(margin_l=0, margin_r=0, margin_t=0, margin_b=0)
                fig_new1 = fig_new1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            barMap.append(stackBarMap)
            has_changed = False
            options = []
            for i in range(0, xBNum):
                for j in range(0, yBNum):
                    options.append((i ,j))
            options_new = [("(" + str(x[0]) + "," + str(x[1]) + ")") for x in options]
            return stackBarMap, fig_new1, [{'label': x, 'value': x} for x in options_new], fig0
        else:
            options = []
            for i in range(0, xBNum):
                for j in range(0, yBNum):
                    options.append((i, j))
            options_new = [("(" + str(x[0]) + "," + str(x[1]) + ")") for x in options]
            if len(barMap) == 1:
                return barMap[0], fig_new1, [{'label': x, 'value': x} for x in options_new], fig0
            else:
                color_idx = 0
                barMap.clear()
                if len(csvData) == 1:
                    Flow0 = makeStackBarLayer(csvData[0])
                    color_idx += 1
                else:
                    Flow0 = makeStackBarLayer(csvData[0])
                    Flow1 = makeStackBarLayer(csvData[1])
                    color_idx += 2
                barNP.clear()
                stackBarLayer.reverse()
                newMap = pydeck.Deck(
                    layers=stackBarLayer,
                    initial_view_state=INITIAL_VIEW_STATE,
                )
                stackBarMap = dd.DeckGL(newMap.to_json(), id='deck_gl',
                                        style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
                                        mapboxKey=mapbox_api_token, tooltip=True)
                if len(csvData) == 1:
                    hist = go.Histogram(x=number_out, xbins={'size': 10}, marker={"opacity": 0.5})
                    fig_new1 = go.Figure(hist)
                    fig_new1.update_layout(
                        xaxis_title="The number of people in a grid in a month",
                        yaxis_title="The number of the grid"
                    )
                    fig_new1 = fig_new1.update_layout(height=300)
                    fig_new1 = fig_new1.update_layout(margin_l=0, margin_r=0, margin_t=0, margin_b=0)
                    fig_new1 = fig_new1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                else:
                    hist1 = go.Histogram(x=number_out, xbins={'size': 10}, name='data1', marker={"opacity": 0.5})
                    hist2 = go.Histogram(x=number_in, xbins={'size': 10}, name='data2', marker={"opacity": 0.5})
                    fig_new1 = go.Figure(data=[hist1, hist2], layout={"barmode": "overlay"})
                    fig_new1.update_layout(
                        xaxis_title="The number of people in a grid in a month",
                        yaxis_title="The number of the grid"
                    )
                    fig_new1 = fig_new1.update_layout(height=300)
                    fig_new1.update_layout(legend=dict(
                        yanchor="top",  # y轴顶部
                        y=0.99,
                        xanchor="right",  # x轴靠右
                        x=0.99
                    ))
                    fig_new1 = fig_new1.update_layout(margin_l=0, margin_r=0, margin_t=0, margin_b=0)
                    fig_new1 = fig_new1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                barMap.append(stackBarMap)
                has_changed = False
                return barMap[0], fig_new1, [{'label': x, 'value': x} for x in options_new], fig0

# select grid and show the data in the second diagram
@app.callback(
    Output(component_id='line_chart', component_property='figure'),
    Input(component_id='grid_option', component_property='value')
)
def select_grid(options):
    global flow_out, flow_in, show_chos
    lst1 = []
    for i in range(1,32):
        for j in range(0, 24):
            lst1.append('2014-1-'+str(i)+' '+str(j)+':00')
    lst = np.array(lst1)
    length = len(options)
    value = options[1:length-1]
    list2 = value.split(',')
    y = int(list2[0])
    x = int(list2[1])
    if show_chos:
        if len(chosenData) == 1:
            flow_out = []
            for i in Flow0:
                flow_out.append(i[x][y])
            line1 = go.Scatter(x=lst, y=flow_out, marker={"opacity": 0.5})
            fig_new2 = go.Figure(line1)
        else:
            flow_out = []
            flow_in = []
            for i in Flow0:
                flow_out.append(i[x][y])
            for i in Flow1:
                flow_in.append(i[x][y])
            line1 = go.Scatter(x=lst, y=flow_out, name='data1', marker={"opacity": 0.5})
            line2 = go.Scatter(x=lst, y=flow_in, name='data2', marker={"opacity": 0.5})
            fig_new2 = go.Figure([line1, line2])
    else:
        if len(csvData) == 1:
            flow_out = []
            for i in Flow0:
                flow_out.append(i[x][y])
            line1 = go.Scatter(x = lst, y = flow_out, marker={"opacity": 0.5})
            fig_new2 = go.Figure(line1)
        else:
            flow_out = []
            flow_in = []
            for i in Flow0:
                flow_out.append(i[x][y])
            for i in Flow1:
                flow_in.append(i[x][y])
            line1 = go.Scatter(x=lst, y=flow_out, name='data1', marker={"opacity": 0.5})
            line2 = go.Scatter(x=lst, y=flow_in, name='data2', marker={"opacity": 0.5})
            fig_new2 = go.Figure([line1, line2])
    fig_new2.update_layout(
        xaxis_title="Time",
        yaxis_title="Flow"
    )
    fig_new2.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1d",
                         step="day",
                         stepmode="backward"),
                    dict(count=7,
                         label="7d",
                         step="day",
                         stepmode="backward"),
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    fig_new2 = fig_new2.update_layout(height=230)
    fig_new2 = fig_new2.update_layout(margin_l=0, margin_r=0, margin_t=0, margin_b=0)
    fig_new2 = fig_new2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig_new2


def makeStackBarLayer(data):
    Flow = gps2grid(data, lon[0], lat[0], lon[1], lat[1], lon[2], lat[2], xBNum, yBNum)
    global color_idx
    barNPtmp.clear()
    for j in range(0, yBNum):
        for k in range(0, xBNum):
            sumFlow = 0
            for time in range(0, 744):
                sumFlow += abs(Flow[time][j][k])
            barNPtmp.append(sumFlow)
    print(barNPtmp[0])
    grids = pd.read_json("./gridFile/POLYGON.geojson")
    df = pd.DataFrame()
    scale = 5000.0 / max(barNPtmp)
    if len(barNP) == 0:
        for j in range(0, yBNum):
            for k in range(0, xBNum):
                barNP.append(int(barNPtmp[j * xBNum + k]) * scale + 5)
                for time in range(0, 744):
                    number_in.append(Flow[time][j][k])
    else:
        for j in range(0, yBNum):
            for k in range(0, xBNum):
                barNP[j * xBNum + k] += int(barNPtmp[j * xBNum + k] * scale + 5)
                for time in range(0, 744):
                    number_out.append(Flow[time][j][k])
    print(barNP[0])
    df["coordinates"] = grids["features"].apply(lambda row: row["geometry"]["coordinates"])
    df["elevation"] = grids["features"].apply(
        lambda row: barNP[int(row["properties"]["value"])])

    df["fill_color"] = grids["features"].apply(
        lambda row: color_scale(barNP[int(row["properties"]["value"])], df['elevation'].max())
    )
    bL = pydeck.Layer(
        "PolygonLayer",
        df,
        id="geojson",
        opacity=0.8,
        stroked=False,
        get_polygon="coordinates",
        filled=True,
        extruded=True,
        wireframe=True,
        get_elevation="elevation",
        get_fill_color="fill_color",
        get_line_color=[255, 255, 255],
        auto_highlight=True,
        pickable=True,
    )
    stackBarLayer.append(bL)
    return Flow

def makeChosenBarLayer(data):
    Flow = gps2grid(data, lon[0], lat[0], lon[1], lat[1], lon[2], lat[2], xBNum, yBNum)
    global color_idx
    chosenBarNPtmp.clear()
    for j in range(0, yBNum):
        for k in range(0, xBNum):
            sumFlow = 0
            for time in range(0, 744):
                sumFlow += abs(Flow[time][j][k])
            chosenBarNPtmp.append(sumFlow)
    grids = pd.read_json("./gridFile/POLYGON.geojson")
    df = pd.DataFrame()
    scale = 5000.0 / max(chosenBarNPtmp)
    if len(chosenBarNP) == 0:
        for j in range(0, yBNum):
            for k in range(0, xBNum):
                chosenBarNP.append(int(chosenBarNPtmp[j * xBNum + k]) * scale + 5)
                for time in range(0, 744):
                    number_in.append(Flow[time][j][k])
    else:
        for j in range(0, yBNum):
            for k in range(0, xBNum):
                chosenBarNP[j * xBNum + k] += int(chosenBarNPtmp[j * xBNum + k] * scale + 5)
                for time in range(0, 744):
                    number_out.append(Flow[time][j][k])
    df["coordinates"] = grids["features"].apply(lambda row: row["geometry"]["coordinates"])
    df["elevation"] = grids["features"].apply(
        lambda row: chosenBarNP[int(row["properties"]["value"])])
    df["fill_color"] = grids["features"].apply(
        lambda row: color_scale(chosenBarNP[int(row["properties"]["value"])], df['elevation'].max())
    )
    bL = pydeck.Layer(
        "PolygonLayer",
        df,
        id="geojson",
        opacity=0.8,
        stroked=False,
        get_polygon="coordinates",
        filled=True,
        extruded=True,
        wireframe=True,
        get_elevation="elevation",
        get_fill_color="fill_color",
        get_line_color=[255, 255, 255],
        auto_highlight=True,
        pickable=True,
    )
    chosenBarLayer.append(bL)
    return Flow


@app.callback(
    Output(component_id='mapContainer', component_property='children'),
    Output(component_id='histogram', component_property='figure'),
    Output(component_id='grid_option', component_property='options'),
    Output(component_id='line_chart', component_property='figure'),
    Input(component_id='hide-data-button', component_property='n_clicks'),
    State(component_id='choose', component_property='value')
)
def show_chosen(n_clicks, val):
    global color_idx, number_out, number_in, fig_new1, fig_new2, Flow0, Flow1, show_chos
    show_chos = True
    if n_clicks is not None:
        print(val)
        color_idx = 0
        chosenData.clear()
        for i, data in enumerate(csvData):
            if i in val:
                chosenData.append(csvData[i])
        if len(chosenData) == 1:
            Flow0 = makeChosenBarLayer(chosenData[0])
            color_idx += 1
        else:
            Flow0 = makeChosenBarLayer(chosenData[0])
            Flow1 = makeChosenBarLayer(chosenData[1])
            color_idx += 2
        chosenBarNP.clear()
        chosenBarLayer.reverse()
        newMap = pydeck.Deck(
            layers=chosenBarLayer,
            initial_view_state=INITIAL_VIEW_STATE,
        )
        chosenBarMap = dd.DeckGL(newMap.to_json(), id='deck_gl',
                                 style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
                                 mapboxKey=mapbox_api_token, tooltip=True)
        if len(chosenData) == 1:
            hist = go.Histogram(x=number_out, xbins={'size': 10}, marker={"opacity": 0.5})
            fig_new1 = go.Figure(hist)
            fig_new1.update_layout(
                xaxis_title="The number of people in a grid in a month",
                yaxis_title="The number of the grid"
            )
            fig_new1 = fig_new1.update_layout(height=300)
            fig_new1 = fig_new1.update_layout(margin_l=0, margin_r=0, margin_t=0, margin_b=0)
            fig_new1 = fig_new1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        else:
            hist1 = go.Histogram(x=number_out, xbins={'size': 10}, name='data1', marker={"opacity": 0.5})
            hist2 = go.Histogram(x=number_in, xbins={'size': 10}, name='data2', marker={"opacity": 0.5})
            fig_new1 = go.Figure(data=[hist1, hist2], layout={"barmode": "overlay"})
            fig_new1.update_layout(
                xaxis_title="The number of people in a grid in a month",
                yaxis_title="The number of the grid"
            )
            fig_new1 = fig_new1.update_layout(height=300)
            fig_new1.update_layout(legend=dict(
                yanchor="top",  # y轴顶部
                y=0.99,
                xanchor="right",  # x轴靠右
                x=0.99
            ))
            fig_new1 = fig_new1.update_layout(margin_l=0, margin_r=0, margin_t=0, margin_b=0)
            fig_new1 = fig_new1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        options = []
        for i in range(0, xBNum):
            for j in range(0, yBNum):
                options.append((i, j))
        options_new = [("(" + str(x[0]) + "," + str(x[1]) + ")") for x in options]

        return chosenBarMap, fig_new1, [{'label': x, 'value': x} for x in options_new], fig0


@app.callback(
    Output(component_id='mapContainer', component_property='children'),
    Input(component_id='showClusterButton', component_property='n_clicks'),
    State(component_id='baseDataC', component_property='value'),
    State(component_id='inDataC', component_property='value'),
    State(component_id='minSamples', component_property='value'),
    State(component_id='clusterRadius', component_property='value'),
    prevent_initial_call=True
)
def showClusters(clicks, bData, iData, minSamples, radius):
    print(1)
    if clicks is not None:
        baseData = pd.read_csv(bData)
        inData = pd.read_csv(iData)
        bFrame, iFrame = pjs.Cluster(radius, minSamples, baseData.sample(2500), baseData, inData)
        clusterBarBase = pydeck.Layer(
            "PolygonLayer",
            bFrame,
            id="geojson",
            opacity=0.8,
            stroked=False,
            get_polygon="coordinates",
            filled=True,
            extruded=True,
            wireframe=True,
            get_elevation="count",
            get_fill_color="color",
            get_line_color=[255, 255, 255],
            auto_highlight=True,
            pickable=True,
        )
        clusterBarIn = pydeck.Layer(
            "PolygonLayer",
            iFrame,
            id="geojson",
            opacity=0.8,
            stroked=False,
            get_polygon="coordinates",
            filled=True,
            extruded=True,
            wireframe=True,
            get_elevation="count",
            get_fill_color="color",
            get_line_color=[255, 255, 255],
            auto_highlight=True,
            pickable=True,
        )
        print(0)
        newMap = pydeck.Deck(
            layers=[clusterBarIn, clusterBarBase],
            initial_view_state=INITIAL_VIEW_STATE,
        )
        dMap = dd.DeckGL(
            newMap.to_json(),
            id='deck_gl',
            style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
            mapboxKey=mapbox_api_token, tooltip=True
        )
        return dMap


@app.callback(
    Output(component_id='mapContainer', component_property='children'),
    Input(component_id='showBufferButton', component_property='n_clicks'),
    State(component_id='baseDataB', component_property='value'),
    State(component_id='inDataB', component_property='value'),
    State(component_id='bufferRadius', component_property='value'),
    prevent_initial_call=True
)
def showBuffers(clicks, bData, iData, radius):
    print(2)
    if clicks is not None:
        baseData_All = pd.read_csv(bData,encoding='gbk')
        baseData_Sample = baseData_All.sample(2500)
        inData = pd.read_csv(iData)
        graph = bf.bufferSHP(radius, baseData_Sample, inData)
        bufferBar = pydeck.Layer(
            "PolygonLayer",
            graph,
            id="geojson",
            opacity=0.8,
            stroked=False,
            get_polygon="coordinates",
            filled=True,
            extruded=True,
            wireframe=True,
            get_elevation="count",
            get_fill_color="color",
            # elevation_scale=scale,
            get_line_color=[255, 255, 255],
            auto_highlight=True,
            pickable=True,
        )
        print(0)
        newMap = pydeck.Deck(
            layers=bufferBar,
            initial_view_state=INITIAL_VIEW_STATE,
        )
        dMap = dd.DeckGL(
            newMap.to_json(),
            id='deck_gl',
            style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
            mapboxKey=mapbox_api_token, tooltip=True
        )
        return dMap


@app.callback(
    Output(component_id='mapContainer', component_property='children'),
    Input(component_id='showChosenP2PButton', component_property='n_clicks'),
    State(component_id='chooseCsvP2P', component_property='value'),
    State(component_id='geoJsonFile2', component_property='value'),
    prevent_initial_call=True
)
def showChosenP2P(click, val, file):
    if click is not None and file is not None and len(val) > 0:
        ls = p2p.Point2Polygon(file, val)
        newjson = pydeck.Layer(
            'GeoJsonLayer',
            ls,
            opacity=1,
            stroked=False,
            filled=True,
            extruded=True,
            wireframe=True,
            lineWidthMinPixels=1,
            get_elevation='count',
            get_fill_color='color',
            get_line_color='color',
            pickable=True
        )
        newMap = pydeck.Deck(
            layers=[newjson],
            initial_view_state=INITIAL_VIEW_STATE,
        )
        dMap = dd.DeckGL(
            newMap.to_json(),
            id='deck_gl',
            style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
            mapboxKey=mapbox_api_token, tooltip=True
        )
        return dMap


@app.callback(
    Output('mapContainer', 'children'),
    Input('showP2LCButton', 'n_clicks'),
    State('P2LDataPoint', 'value'),
    State('P2LDataFrom', 'value'),
    State('P2LDataTo', 'value'),
    State('clusterRadiusP2L', 'value'),
    State('minSamplesP2L', 'value'),
    State('minCountL', 'value'),
    prevent_initial_call=True
)
def showP2LC(click, pointData, fromData, toData, rad, m, minL):
    if click is not None:
        region, tmp2 = ptl2.pTOl2(pointData, fromData, toData, rad, m)
        p = pd.DataFrame()
        b = region.to_list()
        stj.trans('./shp/Polygon/Polygon.shp', 'cluster')
        clusterShape = pd.read_json('./shp/Geojson/cluster.geojson')
        p['coordinates'] = clusterShape['features'].apply(lambda row: row['geometry']['coordinates'])
        tmp2['fromLons'] = tmp2.apply(lambda row: float(b[int(row['index_right_x'])].x), axis=1)
        tmp2['fromLats'] = tmp2.apply(lambda row: float(b[int(row['index_right_x'])].y), axis=1)
        tmp2['toLons'] = tmp2.apply(lambda row: float(b[int(row['index_right_y'])].x), axis=1)
        tmp2['toLats'] = tmp2.apply(lambda row: float(b[int(row['index_right_y'])].y), axis=1)
        x = tmp2.loc[(tmp2['time_x'] <= minL)].index
        tmp2 = tmp2.drop(index=x)
        polyLayer = pydeck.Layer(
            "PolygonLayer",
            p,
            id="geojson",
            get_polygon="coordinates",
            stroked=True,
            filled=True,
            extruded=False,
            wireframe=False,
            lineWidthMinPixels=1,
            get_fill_color='[255, 255, 146]',
            get_line_color=[0, 0, 0],
            pickable=True,
        )
        arcLayer = pydeck.Layer(
            "ArcLayer",
            data=tmp2,
            get_width='time_x * 0.01',
            get_source_position=["fromLons", "fromLats"],
            get_target_position=["toLons", "toLats"],
            get_source_color="[240, 100, 0]",
            get_target_color="[0, 255, 0]",
            pickable=True,
            auto_highlight=True,
        )
        lineMap = pydeck.Deck(
            layers=[arcLayer, polyLayer],
            initial_view_state=INITIAL_VIEW_STATE
        )
        lMap = dd.DeckGL(
            lineMap.to_json(),
            id='deck_gl',
            style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
            mapboxKey=mapbox_api_token, tooltip=True
        )
        return lMap


@app.callback(
    Output('mapContainer', 'children'),
    Input('showP2LGButton', 'n_clicks'),
    State('originLat', 'value'),
    State('originLon', 'value'),
    State('xLat', 'value'),
    State('xLon', 'value'),
    State('yLat', 'value'),
    State('yLon', 'value'),
    State('xBlockNum', 'value'),
    State('yBlockNum', 'value'),
    State('P2LDataFrom', 'value'),
    State('P2LDataTo', 'value'),
    State('minCountL', 'value'),
    prevent_initial_call=True
)
def showP2LG(click, input1, input2, input3, input4, input5, input6, input7, input8, dF, dT, minL):
    global xBNum, yBNum
    if click is not None:
        lat.clear()
        lat.append(input1)
        lat.append(input3)
        lat.append(input5)
        lon.clear()
        lon.append(input2)
        lon.append(input4)
        lon.append(input6)
        xBNum = input7
        yBNum = input8
        tp.threePoint((lon[0], lat[0]), (lon[1], lat[1]), (lon[2], lat[2]), xBNum, yBNum)
        region, tmp2 = preB.preprocessingB((input1, input2), (input3, input4), (input5, input6), xBNum, yBNum, dF, dT)
        with open('./gridFile/POLYGON.geojson', 'r') as file:
            gridjs = json.load(file)
        upGrid = pydeck.Layer(
            'GeoJsonLayer',
            gridjs,
            opacity=0.8,
            stroked=True,
            filled=True,
            extruded=False,
            wireframe=False,
            lineWidthMinPixels=1,
            # get_elevation=50,
            get_fill_color='[125, 125,125]',
            get_line_color=[0, 0, 0],
            pickable=True
        )
        tmp2['fromLons'] = tmp2.apply(lambda row: float(region[int(row['grid_x'])][1]), axis=1)
        tmp2['fromLats'] = tmp2.apply(lambda row: float(region[int(row['grid_x'])][0]), axis=1)
        tmp2['toLons'] = tmp2.apply(lambda row: float(region[int(row['grid_y'])][1]), axis=1)
        tmp2['toLats'] = tmp2.apply(lambda row: float(region[int(row['grid_y'])][0]), axis=1)
        x = tmp2.loc[(tmp2['time_x'] <= int(minL))].index
        tmp2 = tmp2.drop(index=x)
        arcLayer = pydeck.Layer(
            "ArcLayer",
            data=tmp2,
            get_width='time_x * 0.5',
            get_source_position=["fromLons", "fromLats"],
            get_target_position=["toLons", "toLats"],
            get_source_color="[240, 100, 0]",
            get_target_color="[0, 255, 0]",
            pickable=True,
            auto_highlight=True,
        )
        lineMap = pydeck.Deck(
            layers=[arcLayer, upGrid],
            initial_view_state=INITIAL_VIEW_STATE
        )
        lMap = dd.DeckGL(
            lineMap.to_json(),
            id='deck_gl',
            style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
            mapboxKey=mapbox_api_token, tooltip=True
        )
        return lMap


@app.callback(
    Output(component_id='mapContainer', component_property='children'),
    Input(component_id='showChosenL2PButton', component_property='n_clicks'),
    State(component_id='chooseFromCsvL2P', component_property='value'),
    State(component_id='chooseToCsvL2P', component_property='value'),
    State(component_id='geoJsonFile3', component_property='value'),
    State('minCountLP', 'value'),
    prevent_initial_call=True
)
def showChosenL2P(click, fromData, toData, geoJson, minl):
    if click is not None and geoJson is not None and fromData is not None and toData is not None:
        region, tmp2 = l2p.lToP(geoJson, fromData, toData)
        b = region.to_list()
        js = json.load(open(geoJson))
        tmp2['fromLons'] = tmp2.apply(lambda row: float(b[int(row['index_right_x'])].x), axis=1)
        tmp2['fromLats'] = tmp2.apply(lambda row: float(b[int(row['index_right_x'])].y), axis=1)
        tmp2['toLons'] = tmp2.apply(lambda row: float(b[int(row['index_right_y'])].x), axis=1)
        tmp2['toLats'] = tmp2.apply(lambda row: float(b[int(row['index_right_y'])].y), axis=1)
        x = tmp2.loc[(tmp2['time_x'] <= minl)].index
        tmp2 = tmp2.drop(index=x)
        newjson = pydeck.Layer(
            'GeoJsonLayer',
            js,
            opacity=1,
            stroked=True,
            filled=True,
            extruded=False,
            wireframe=False,
            lineWidthMinPixels=1,
            # get_elevation='count',
            get_fill_color='[125, 125, 125]',
            get_line_color='[0, 0, 0]',
            pickable=True
        )
        arcLayer = pydeck.Layer(
            "ArcLayer",
            data=tmp2,
            get_width='time_x * 0.01',
            get_source_position=["fromLons", "fromLats"],
            get_target_position=["toLons", "toLats"],
            get_source_color="[240, 100, 0]",
            get_target_color="[0, 255, 0]",
            pickable=True,
            auto_highlight=True,
        )
        newMap = pydeck.Deck(
            layers=[arcLayer, newjson],
            initial_view_state=INITIAL_VIEW_STATE,
        )
        dMap = dd.DeckGL(
            newMap.to_json(),
            id='deck_gl',
            style={'position': 'relative', 'height': '70vh', 'width': '88vw'},
            mapboxKey=mapbox_api_token, tooltip=True
        )
        return dMap


if __name__ == '__main__':
    app.run_server(debug=False, port=8060)
