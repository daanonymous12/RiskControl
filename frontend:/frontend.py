#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from cassandra.cluster import Cluster
import pandas as pd 
import plotly.tools as tls
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_table

cluster = Cluster(["<IP of cassandra DB>"])
conn=cluster.connect('users')
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}])
server = app.server

app.layout = html.Div([
        html.H1("RiskControl", style={'backgroundColor':'grey','textAlign': 'center','font_size': '40px'}),
        dcc.Store(id='memory'),
                html.Div([
                        html.P('Enter Unique Username:',style={'display': 'inline-block'}),
                        dcc.Input(id='my-id', value='CFVFR8B', type='text'),
                        html.Div([html.H1('Ticker:',style={'display':'inline-block','fontsize':30}),
                        html.Div(id='my-div', style={'display':'inline-block','color': 'blue', 'fontSize': 30})],style={
                                'fontsize':30}),
                        dcc.Interval(id="interval", interval=6* 1000, n_intervals=0)],style=
                            {
                                "height": "25x",
                                #"width": "auto"
                                #"margin-top": "25px",
                            }),
                html.Div([dash_table.DataTable(id='current-data',columns=[{'name':'Last Transaction Time(HH/MM/Seconds)',
                                                                          'id':'time'},
                                                                        {'name':'Trade Price','id':'previous_price'},
                                                                        {'name':'Cash on Hand','id':'cash'},
                                                                        {'name':'Number of shares holding','id':'numb_share'},
                                                                        {'name':'Buy','id':'buy'},
                                                                        {'name':'Sell','id':'sell'},
                                                                        {'name':'Profit','id':'profit'},
                                                                        {'name':'Total Value in Hand','id':'total_value'}],
                                                                        style_cell={
                                                                                'height': 'auto',
                                                                            'minWidth': '0px', 'maxWidth': '180px',
                                                                            'whiteSpace': 'normal',
                                                                        'textOverflow': 'ellipsis',
                                                                        'textAlign':'center',
                                                                        'font_size': '20px'},
                                )]),
                html.Div([html.P('Graph Category:',style={'display': 'inline-block'}),
                          #[dash.dependencies.Input('demo-dropdown', 'value')]
                          dcc.Dropdown(id='drop-down',
                                      options=[{'label': 'All', 'value': 'All'},
                                               {'label': 'Cash on Hand', 'value': 'cash'},
                                               {'label': 'Shares Holding', 'value': 'numb_share'},
                                               {'label': 'Stock Price', 'value': 'price'},
                                               {'label': 'Profit', 'value': 'profit'},
                                               {'label': 'Value Holding', 'value': 'total_value'}
                                              ],
                                      value='All'),
                        ]),
                html.Div([dcc.Graph(
                        id='crossfilter-indicator-scatter',
                        hoverData={'points': [{'customdata': 'Japan'}]}),
                        ], style={'width': '95%', 'display': 'inline-block', 'padding': '0 20',"color": "#7fafdf"})

])                  
@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
def update_output_div(value):
    user=conn.execute("""select * from users.directory_data where user=%(user)s""",{'user':value},trace=False)
    user=pd.DataFrame(user)    
    return user['ticker'].iloc[0]

@app.callback( 
        Output('current-data','data'),
        [Input('my-id','value'),
         Input('my-div','children'),
         Input("interval", "n_intervals")])
def get_table_data(user,ticker,_):
    table_data=conn.execute("""select * from users.user_data100k where ticker=%(ticker)s and user=%(user)s""",{'ticker':ticker
                            ,'user':user},trace=False)
    table_data=pd.DataFrame(table_data)
    updated=table_data[['time','previous_price','cash','numb_share','buy','sell','profit','total_value']] 
    updated['previous_price']=round(updated['previous_price'],2)
    updated['cash']=round(updated['cash'],2)
    updated['numb_share']=int(updated['numb_share'])
    updated['buy']=round(updated['buy'],2)
    updated['sell']=round(updated['sell'],2)
    updated['profit']=round(updated['profit'],2)
    updated=updated.astype(str)
    return updated.to_dict('records')

@app.callback(Output('memory','data'),[
                Input(component_id='my-id', component_property='value'),
                Input("interval", "n_intervals")])
def get_graph_table(value,_):
    historical=conn.execute("""select * from users.graph_data where user=%(user)s""",{'user':value},trace=False)
    historical=pd.DataFrame(historical)
    historical['time_new']=historical['time_new'].astype(int)/100
    historical['time_new']=pd.to_datetime(historical['time_new'], format='%H%M%f').dt.time
    #historical['time_new']=historical['time_new'].astype('str')
    graph_data=historical[['time_new','cash','numb_share','price','profit','total_value']].copy()
    return graph_data.to_dict('list') 

@app.callback(Output('crossfilter-indicator-scatter','figure'),
              [Input('drop-down','value'),
               Input('memory','data')])
def draw_data(value,data):
    if value=='All':
        fig = tls.make_subplots(rows=1, cols=1, shared_xaxes=True,vertical_spacing=0,horizontal_spacing=0)
        fig['layout']['margin'] = {'l': 30, 'r': 10, 'b': 10, 't': 40}
        fig.append_trace({'x':data['time_new'],'y':data['cash'],'type':'scatter','name':'Cash'},1,1)
        fig.append_trace({'x':data['time_new'],'y':data['numb_share'],'type':'scatter','name':'Numb of Shares Holding'},1,1)
        fig.append_trace({'x':data['time_new'],'y':data['price'],'type':'scatter','name':'Price'},1,1)
        fig.append_trace({'x':data['time_new'],'y':data['profit'],'type':'scatter','name':'Profit'},1,1)
        fig.append_trace({'x':data['time_new'],'y':data['total_value'],'type':'scatter','name':'Total Value in Hand'},1,1)
    else:
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(
                go.Scatter(x=data['time_new'], y=data[value]),
                row=1, col=1)
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_yaxes(title_text="USD", row=1, col=1)
    return fig        
if __name__ == '__main__':
    app.run_server(debug=True,port=80,host="0.0.0.0")

    