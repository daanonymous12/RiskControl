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
conn = cluster.connect('users')
app = dash.Dash(__name__, meta_tags=[{"name": "viewport",
                                      "content": "width=device-width"}])
server = app.server
app.layout = html.Div([
        html.H1("RiskControl", style={'backgroundColor': 'grey', 'textAlign':
                'center', 'font-size': '40px'}),
        dcc.Store(id='memory'),
        html.Div([html.Div([
                        html.Div('Enter Unique Username:',style={'display': 'inline-block','padding': 1}),
                        dcc.Input(id='my-id', value='Z5O2MCN', type='text')],style={
                                'font-size':20}),
                        html.Div([html.P('Ticker:',style={'display':'inline-block'}),
                        html.Div(id='my-div', style={'display':'inline-block','color': 'blue'})],style={
                                'font-size':30}),
                        dcc.Interval(id="interval", interval=6* 1000, n_intervals=0)],style=
                            {
                                #"height": "15x",
                                "width": "auto",
                                "margin-top":"4px",
                            }),
                html.Div([dash_table.DataTable(id='current-data',
                                               columns=[{'name':' Last Transaction Time(HH/MM/Seconds)',
                                                         'id': 'time'},
                                                        {'name': 'Trade Price','id': 'previous_price'}
                                                        {'name':'Cash on Hand','id':'cash'},
                                                        {'name':'Number of shares holding','id':'numb_share'},
                                                        {'name':'Buy','id':'buy'},
                                                        {'name':'Sell','id':'sell'},
                                                        {'name':'Profit','id':'profit'},
                                                        {'name':'Total Value in Hand','id':'total_value'}],
                                               style_cell={'height': 'auto',
                                                           'minWidth': '0px',
                                                           'maxWidth': '180px',
                                                           'whiteSpace': 'normal',
                                                           'textOverflow': 'ellipsis',
                                                           'textAlign': 'center',
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
                                      value='All'), ]),
                html.Div([dcc.Graph(
                        id='crossfilter-indicator-scatter',
                        hoverData={'points': [{'customdata': 'Japan'}]}),
                        ], style={'width': '95%', 'display': 'inline-block', 'padding': '0 20',"color": "#7fafdf"}),
        html.Div([
        html.I("Enter New User Information",style={"width": "auto",'font_size': '70px'}),
        html.Br(),
        dcc.Input(id="Username", type="text", placeholder="Please enter user_name"),
        dcc.Input(id="Ticker", type="text", placeholder="Ticker", debounce=True),
        dcc.Input(id="Buy", type="number", placeholder="Buy Threshold", debounce=True),
        dcc.Input(id="Sell", type="number", placeholder="Sell Threshold", debounce=True),
        dcc.Input(id="cash_start", type="number", placeholder="Starting out Cash", debounce=True),
        html.Div(id="new_user")],style={
                                'font-size': '30px', 'height':'50x','margin-top':'10px'})
])     


@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
def update_output_div(value):
    """
    Takes username input and output the ticker of the said user through callback.
    
    @type  value: string
    @param value: username
    @rtype:       string
    @return:      The ticker of the user in databse
    """
    user = conn.execute("""select * from users.directory_data where
                      user=%(user)s""", {'user': value}, trace=False)
    user = pd.DataFrame(user)
    return user['ticker'].iloc[0]


@app.callback(
        Output('current-data', 'data'),
        [Input('my-id', 'value'),
         Input('my-div', 'children'),
         Input("interval", "n_intervals")])
def get_table_data(user, ticker, _):
    """
    This function takes user infomation including ticker and username and
    queries from cassandra databse for parameters such as outputs the current
    statistics for the users including cash, and profit.
    
    @type  user: string
    @param user: username
    @type  ticker: string
    @param ticker: ticker associated with the user
    @rtype data: User data for table in frontend
    """
    table_data = conn.execute("""select * from users.user_data100k where
                              ticker=%(ticker)sand user=%(user)s""",
                              {'ticker': ticker, 'user': user}, trace=False)
    table_data = pd.DataFrame(table_data)
    updated = table_data[['time', 'previous_price', 'cash', 'numb_share',
                          'buy', 'sell', 'profit', 'total_value']]
    updated['previous_price'] = round(updated['previous_price'], 2)
    updated['cash'] = round(updated['cash'], 2)
    updated['numb_share'] = int(updated['numb_share'])
    updated['buy'] = round(updated['buy'], 2)
    updated['sell'] = round(updated['sell'], 2)
    updated['profit'] = round(updated['profit'], 2)
    updated = updated.astype(str)
    return updated.to_dict('records')


@app.callback(Output('memory', 'data'),
              [Input(component_id='my-id', component_property='value'),
               Input("interval", "n_intervals")])
def get_graph_table(value, _):
    """
    Updates the graph data for the frontend website through query from
    cassandra database and stores it to be used when plotting graph
    It takes in username as well as a interval for updating.
    
    @type  value: string
    @param value: username
    @type      _: number
    @param     _: update interval
    @rtype:       dict
    @return     : dictionary of all values for the user to be used for graphs
    """
    historical = conn.execute("""select * from users.graph_data where
                              user=%(user)s""", {'user': value}, trace=False)
    historical = pd.DataFrame(historical)
    historical['time_new'] = historical['time_new'].astype(int)/100
    historical['time_new'] = pd.to_datetime(historical['time_new'],format='%H%M%f').dt.time
    graph_data = historical[['time_new', 'cash', 'numb_share', 'price',
                             'profit', 'total_value']].copy()
    return graph_data.to_dict('list')


@app.callback(Output('crossfilter-indicator-scatter', 'figure'),
              [Input('drop-down', 'value'),
               Input('memory', 'data')])
def draw_data(value, data):
    """
    This function takes dictionary data stored in memory variable along with 
    graph parameter and returns a graph through use of plotly.tools.
    
    @type  value: string
    @param value: Dropdown bar value to be graphed on the y axis
    @type   data: dict
    @param  data: Dictionary of graph data for user
    @rtyp:        graph
    @return:      plot with time as x-axis and user specified parameter as
                  y parameter. Default value is 'All'
    """
    if value == 'All':
        fig = tls.make_subplots(rows=1, cols=1, shared_xaxes=True,
                                vertical_spacing=0, horizontal_spacing=0)
        fig['layout']['margin'] = {'l': 30, 'r': 10, 'b': 10, 't': 40}
        fig.append_trace({'x': data['time_new'], 'y': data['cash'],
                          'type': 'scatter', 'name': 'Cash'}, 1, 1)
        fig.append_trace({'x': data['time_new'], 'y': data['numb_share'],
                          'type': 'scatter', 'name': 'Numb of Shares Holding'}, 1, 1)
        fig.append_trace({'x': data['time_new'], 'y': data['price'],
                          'type': 'scatter', 'name': 'Price'}, 1, 1)
        fig.append_trace({'x':data['time_new'],'y':data['profit'],
                          'type': 'scatter', 'name': 'Profit'}, 1, 1)
        fig.append_trace({'x': data['time_new'], 'y': data['total_value'],
                          'type':'scatter', 'name': 'Total Value in Hand'}, 1, 1)
    else:
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(
                go.Scatter(x=data['time_new'], y=data[value]),
                row=1, col=1)
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_yaxes(title_text="USD", row=1, col=1)
    return fig


@app.callback(Output('new_user', 'children'),
              [Input('Username', 'value'),
               Input('Ticker', 'value'),
               Input('Buy', 'value'),
               Input('Sell', 'value'),
               Input('cash_start', 'value')])
def new_user(user, ticker, buy, sell, cash_start):
    """
    Inserts new user into 2 cassandra databse, one for directory and other is
    for user data.
    @type  user: string
    @param user: username
    @type  ticker: string
    @param ticker: stock picked
    @type  buy: number
    @param buy: threshold,in dollar, when exceeded, will trigger a buy
    @type  sell: number
    @param sell: threshold,in dollar, when exceeded, will trigger a sell
    @type  cash_start: number
    @param cash_start: starting capital in dollars
    @rtype: string
    @return: text notifying user that information has been inputted
    """
    if cash_start is None:
        return []
    else:
        # need to write 2 queries
        conn.execute("""insert into users.directory_data(user,ticker) values
                     (%(user)s,%(ticker)s)""", {'user': user, 'ticker': ticker})
        conn.execute("""insert into users.user_data100k(time,user,ticker,numb_share
                        ,profit,buy,sell,previous_price,total_value,cash) values
                        (%(time)s,%(user)s,%(ticker)s,
                        %(numb_share)s,%(profit)s,%(buy)s,%(sell)s,
                        %(previous_price)s,%(total_value)s,%(cash)s)""",
                     {'time': 0, 'user': user, 'ticker': ticker, 'numb_share': 0,
                      'profit': 0, 'buy': float(buy), 'sell': float(sell),
                      'previous_price': 0, 'total_value': 0, 'cash': float(cash_start)})
    return 'Information has been entered into database'


if __name__ == '__main__':
    app.run_server(debug=True, port=80, host="0.0.0.0")
    