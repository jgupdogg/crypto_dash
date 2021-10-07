import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import pandas_datareader.data as web
import time


# https://stooq.com/

df = pd.read_csv('crypto_prices')
cycles = pd.read_csv('btc_cycles')
dom=pd.read_csv('market_dom')

# https://www.bootstrapcdn.com/bootswatch/
app = dash.Dash(__name__,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

colors = {
    'background': '#120221',
    'text': '#f1b633'
}
color_map={'BTC':'darkorange',
            'ETH':'blue',
            'BNB':'gold',
            'ADA':'darkblue',
            'USDT':'green',
            'XRP':'white',
            'SOL':'blueviolet',
            'DOGE':'yellow',
            'USDC':'lime',
            'DOT':'deeppink',
            'Other':'red',
            'matic':'purple'}

layout = dict(plot_bgcolor = colors['background'],
             paper_bgcolor = 'rgba(0,0,0,0)',
             font = {'color' : colors['text']},
             xaxis = dict(
                        gridcolor = 'grey',
                        zeroline=False
                        ),
             yaxis = dict(
                        gridcolor='grey',
                        zeroline=False
                        ),
             title = dict(x = 0.5, xanchor = 'center')
             )

# Layout section: Bootstrap (https://hackerthemes.com/bootstrap-cheatsheet/)
# ************************************************************************
app.layout = dbc.Container([

    dbc.Row(
        dbc.Col(html.H1("Crypto  Dash Live ",
                        style = {'color':'#f1b633', 'text-align':'center', 'padding':25}
                        )
                )
    ),
    dbc.Row(
        dbc.Col([
            html.Div([
                html.H5("Top 10 Coin Market Dominance",
                        style={'color': colors['text'], 'text-align': 'center'}
                        ),
                html.Label(['Select Date'],
                           style={'color': colors['text']
                                  }
                           )
            ]),
            dcc.Dropdown(id='my-dpdn3', multi=False, value=['today'],
                             options=[{'label':'today', 'value':'today'}],
                             style={'backgroundColor':'rgba(0,0,0,0)',
                                    },
                             ),
            dcc.Graph(
                id='pie-fig',
            )
            ],
            width={'size':6, 'offset': 3},
            style = {'padding':50}
        )
        ),

    dbc.Row([

        dbc.Col([
            html.Div([
                html.H5("Bitcoin Halving Cycle Comparison",
                        style={'color': colors['text'], 'text-align': 'center'}
                        ),
                html.Label(['Select cycle(s)'],
                           style={'color': colors['text']
                                  }
                           )
            ]),
            dcc.Dropdown(id='my-dpdn', multi=True, value=[3, 4],
                         options=[{'label': x, 'value': x,}
                                  for x in sorted(cycles['cycle'].unique())],
                         style={'backgroundColor':'rgba(0,0,0,0)',
                                },
                         ),
            dcc.Graph(
                id='line-fig',
                        ),
            html.Div([
                html.Label(['Select days range'],
                           style = {'color':colors['text']
                                   }
                           )
            ]),
            dcc.RangeSlider(id='my-slide',
                            #title='select range',
                            marks={
                                0:'0',
                                250:'250',
                                500:'500',
                                750:'750',
                                1000:'1,000',
                                1250:'1,250',
                                1400:'max'
                            },
                            step=25,
                            min = 0,
                            max = 1400,
                            value=[0, 1400],
                            allowCross=False,
                            updatemode='drag',
                            tooltip={'always_visible':False,
                                     'placement':'bottom'},
                            className='rangeSlider'
                            ),
            ],
            xs=12, sm=12, md=12, lg=6, xl=6
        ),

        dbc.Col([

            html.Div([
                html.H5("Top Coin Comparison",
                        style={'color': colors['text'], 'text-align': 'center'}
                        ),
                html.Label(['Select Coin(s)'],
                           style={'color': colors['text']
                                  }
                           )
            ]),
            dcc.Dropdown(id='my-dpdn2', multi=True, value=['BTC', 'ETH'],
                         options=[{'label': x, 'value': x}
                                  for x in sorted(df['Symbols'].unique())],
                        style={'backgroundColor':'rgba(0,0,0,0)',
                               }
                         ),
            dcc.Graph(id='line-fig2', figure={}
                      ),
            html.Div([
                html.Label(['Select date range'],
                           style={'color': colors['text']
                                  }
                           )
            ]),
            dcc.RangeSlider(id='my-slide2',
                            marks={
                                1420088400: '2015',
                                1451624400: '2016',
                                1483246800: '2017',
                                1514782800: '2018',
                                1546318800: '2019',
                                1577854800: '2020',
                                1609477200: '2021'
                            },
                            step=1,
                            min= 1420088400,
                            max =  int(time.time()),
                            value=[1577854800, int(time.time())],
                            allowCross=False,
                            updatemode='drag',
                            # tooltip={'always_visible': False,
                            #          'placement': 'bottom'},
                            className='rangeSlider'
                            ),
        ],
            xs=12, sm=12, md=12, lg=6, xl=6
        ),

    ], style = {'padding':75},
       no_gutters=True, justify='start'), # Horizontal:start,center,end,between,around
    dbc.Row(
        dbc.Col([
            html.H5("Price Action Chart",
                        style = {'color':colors['text'], 'text-align':'center'}
                        ),
            html.H6("Identify Key Resistance and Support Levels by Volume",
                    style={'color': colors['text'], 'text-align': 'center'}
                    )
                ])
    ),
    dbc.Row(
        dbc.Col([
            html.Div([
                html.Label(['Select Coin'],
                           style={'color': colors['text']
                                  }
                           )
            ]),
            dcc.Dropdown(id='my-dpdn4', multi=False, value='BTC',
                         options=[{'label': x, 'value': x}
                                  for x in sorted(df['Symbols'].unique())],
                         style={'backgroundColor': 'rgba(0,0,0,0)',
                                }
                         ),
            dcc.Graph(id='bar-fig', figure={}
                      ),
            dcc.RangeSlider(id='my-slide3',
                            marks={
                                1420088400: '2015',
                                1451624400: '2016',
                                1483246800: '2017',
                                1514782800: '2018',
                                1546318800: '2019',
                                1577854800: '2020',
                                1609477200: '2021'
                            },
                            step=1,
                            min= 1420088400,
                            max =  int(time.time()),
                            value=[1609477200, int(time.time())],
                            allowCross=False,
                            updatemode='drag',
                            # tooltip={'always_visible': False,
                            #          'placement': 'bottom'},
                            className='rangeSlider'
                            ),
            ])

    ),

], fluid=True)


# Callback section: connecting the components
# ************************************************************************
# Line chart - Single
@app.callback(
    Output('pie-fig', 'figure'),
    Input('my-dpdn3', 'value')
    )
def update_graph(date):
    labels = dom['symbol']
    sizes = dom['mrkt_dom']
    figpie = px.pie(dom, values=sizes, names=labels,
                 color='symbol', color_discrete_map=color_map, hole=0.3)
    figpie.update_layout(layout)
    figpie.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=18,
                      texttemplate='%{percent:.1%}',
                      marker=dict(line=dict(color='#000000', width=2)))
    return figpie

@app.callback(
    Output('line-fig', 'figure'),
    [Input('my-dpdn', 'value'),
     Input('my-slide', 'value')]
)
def update_graph(cycle_slctd, date_range):
    dff = cycles[cycles['cycle'].isin(cycle_slctd)]
    dff = dff[(dff['days_since_halving'] >= date_range[0]) & (dff['days_since_halving'] <= date_range[1])]

    figln = px.line(dff, x='days_since_halving', y='por_increase', color = 'cycle', log_y = True
                    )
    figln.update_layout(layout)
    figln.update_layout(
                        yaxis = dict(title='Proportional Increase'),
                        xaxis = dict(title='Days Since Halving'),
                        legend = dict(title='Cycles')
                        )

    return figln


# Line chart - multiple
@app.callback(
    Output('line-fig2', 'figure'),
    [Input('my-dpdn2', 'value'),
     Input('my-slide2', 'value')]
)
def update_graph(stock_slctd, date_range):
    dff = df[df['Symbols'].isin(stock_slctd)]
    dff = dff[(dff['unix'] >= date_range[0]) & (dff['unix'] <= date_range[1])]
    for coin in stock_slctd:
        data = dff[dff['Symbols'] == coin].sort_values('Date')
        initial = data['Open'].iloc[0]
        data['pct_chng'] = [((x - initial) / initial) * 100 for x in data['Open']]
        if coin == stock_slctd[0]:
            response = data
        else:
            response = pd.concat([response, data])

    figln2 = px.line(response, x='Date', y='pct_chng', color='Symbols',color_discrete_map=color_map
                     )
    figln2.update_layout(layout)
    figln2.update_layout(
                        yaxis=dict(title='Percent Increase'),
                        xaxis=dict(title='Date'),
                        legend=dict(title = 'Coins')
                        )


    return figln2

# Bar chart - multiple
@app.callback(
    Output('bar-fig', 'figure'),
    [Input('my-dpdn4', 'value'),
     Input('my-slide3', 'value')]
)
def update_graph(stock_slctd, date_range):
    dff = df[df['Symbols']==stock_slctd]
    dff = dff[(dff['unix'] >= date_range[0]) & (dff['unix'] <= date_range[1])]
    top = dff['Open'].max()
    resistance = dff.groupby(pd.cut(dff['Open'], 30)).sum()['Volume'].reset_index(drop=False)
    resistance['Price'] = [x.mid for x in resistance['Open']]
    figbar = px.bar(resistance, x='Volume', y='Price', orientation='h')
    figbar.update_layout(layout)
    figbar.update_traces(marker_color = color_map[stock_slctd])

    return figbar



if __name__ == '__main__':
    app.run_server(debug=True, port=8000)

# https://youtu.be/0mfIK8zxUds