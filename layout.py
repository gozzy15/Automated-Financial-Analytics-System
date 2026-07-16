import dash_bootstrap_components as dbc

from dash import html
from dash import dcc
from dash import dash_table
from datetime import datetime, timedelta

from system_config import LIVE_UPDATE_SECONDS, APP_NAME, APP_VERSION, AUTHOR, LINK

def create_layout(
        tickers,
        latest_data,
        overall_metrics,
        ticker_metrics
    ):

    return dbc.Container([
        # Header
        # ===========================
        # Professional Header
        # ===========================

        # Header
        dbc.Row(

            [

                dbc.Col(

                    [

                        html.H1(

                            "📊 Financial Analytics Dashboard",

                            className="display-5 fw-bold text-primary"

                        ),

                        html.P(

                            "Professional Investment • Risk • Market Intelligence Platform",

                            className="text-muted fs-5"

                        )

                    ],

                    width=8

                ),

                dbc.Col(

                    [

                        html.Div(

                            [

                                html.Small(

                                    "Current Time",

                                    className="text-muted"

                                ),

                                html.H4(

                                    id="current-time",

                                    className="fw-bold"

                                )

                            ],

                            className="text-end"

                        )

                    ],

                    width=4

                )

            ],

            className="mb-4 mt-3 align-items-center"

        ),
        
        # Top Metrics Cards
        dbc.Row([
            dbc.Col(

                dbc.Card(

                    dbc.CardBody([

                        html.Div(

                            [

                                html.H6(
                                    "📈 SELECTED STOCK(S)",
                                    className="metric-title"
                                ),

                                html.H1(
                                    id="kpi-total-tickers",
                                    style={
                                        "fontWeight": "bold",
                                        "color": "#1565C0",
                                        "fontSize": "42px",
                                        "textAlign": "center"
                                    }
                                ),

                            ]

                        )

                    ]),

                    className="metric-card"
                )

            , width=3),
            
            dbc.Col(

                dbc.Card(

                    dbc.CardBody([

                        html.H6(
                            "📊 TRADING RECORDS",
                            className="metric-title"
                        ),

                        html.H1(
                            id="kpi-total-records",
                            style={
                                "fontWeight": "bold",
                                "color": "#28A745",
                                "fontSize": "42px",
                                "textAlign": "center"
                            }
                        ),

                        html.P(
                            "Historical Data Points",
                            className="metric-footer"
                        )

                    ]),

                    className="metric-card"

                )

            , width=3),
            
            dbc.Col(

                dbc.Card(

                    dbc.CardBody([

                        html.H6(
                            "📅 SELECTED PERIOD",
                            className="metric-title"
                        ),

                        html.H4(
                            id="kpi-start-date",
                            style={
                                "color": "#17A2B8",
                                "fontWeight": "bold", 
                                "textAlign": "center"
                            }
                        ),

                        html.H5(
                            "to",
                            style={
                                "color": "#999",
                                "textAlign": "center"
                                
                            }
                        ),

                        html.H4(
                            id="kpi-end-date",
                            style={
                                "color": "#17A2B8",
                                "fontWeight": "bold", 
                                "textAlign": "center"
                            }
                        )

                    ]),

                    className="metric-card"

                )

            , width=3),
            
            dbc.Col(

                dbc.Card(

                    dbc.CardBody([

                        html.H6(
                            "💰 AVERAGE DAILY RETURN",
                            className="metric-title"
                        ),

                        html.H1(
                            id="kpi-average-return",
                            style={
                                "fontWeight": "bold",
                                "color": "#FFC107",
                                "fontSize": "42px", 
                                "textAlign": "center"
                                
                            }
                        ),

                        html.P(
                            "Across Selected Stocks",
                            className="metric-footer"
                        )

                    ]),

                    className="metric-card"
                )

            , width=3),
        ], className="mb-4"),
        
        dbc.Row([

            dbc.Col([

                dbc.Card(

                    dbc.CardBody([

                        html.H4(
                            "📈 Executive Summary",
                            className="text-primary mb-4 fw-bold"
                        ),

                        dbc.Row([

                            dbc.Col([
                                html.H6(id="label-1"),
                                html.P(
                                    id="best-performer",
                                    className="fw-bold text-success"
                                )
                            ], width=4),

                            dbc.Col([
                                html.H6(id="label-2"),
                                html.P(
                                    id="worst-performer",
                                    className="fw-bold text-danger"
                                )
                            ], width=4),

                            dbc.Col([
                                html.H6(id="label-3"),
                                html.P(
                                    id="most-volatile",
                                    className="fw-bold text-warning"
                                )
                            ], width=4),

                        ]),

                        html.Hr(),

                        dbc.Row([

                            dbc.Col([
                                html.H6(id="label-4"),
                                html.P(
                                    id="highest-volume",
                                    className="fw-bold text-info"
                                )
                            ], width=6),

                            dbc.Col([
                                html.H6(id="label-5"),
                                html.P(
                                    id="average-return",
                                    className="fw-bold text-primary"
                                )
                            ], width=6),

                        ])

                    ]),

                    className="dashboard-card"

                )

            ])

        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4(
                            "💡 Market Insights",
                            className="text-primary fw-bold mb-3"
                        ),
                        html.Ul(
                            id="market-insights",
                            className="mb-0"
                        )
                    ]),
                    className="dashboard-card"
                )
            ])
        ], className="mb-4"),

        # Add this to your layout after the metrics cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("⚡ Live Market Data", className="card-title"),
                        html.Div(id='live-quotes'),
                        dcc.Interval(
                            id='interval-component',
                            interval= LIVE_UPDATE_SECONDS * 1000,  # in milliseconds (30 seconds)
                            n_intervals=0
                        ),
                        dcc.Interval(
                            id="clock-interval",
                            interval=1000,
                            n_intervals=0
                ),
                    ])
                ], # className="mb-3",
                                className="metric-card")
            ])
        ], className="mb-4"),
        
        # Control Panel
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardBody([

                            html.Div(

                                [

                                    html.H4(
                                        "⚙️ Control Panel",
                                        style={
                                            "color": "white",
                                            "fontWeight": "bold",
                                            "textAlign": "center"
                                        }
                                    )

                                ],

                                className="sidebar"

                            ),
                            
                            # Stock Selection
                            dbc.Card(

                                dbc.CardBody(

                                    [

                                        html.H6(

                                            "📈 Stock Selection",

                                            className="fw-bold",

                                            style={

                                                "color": "#0F4C81"

                                            }

                                        ),

                                        html.P(

                                            "Choose one or more stocks to analyse.",

                                            className="text-muted mb-2",

                                            style={

                                                "fontSize": "13px"

                                            }

                                        ),

                                        dcc.Dropdown(

                                            id="ticker-dropdown",

                                            options=[
                                                {"label": t, "value": t}
                                                for t in tickers
                                            ],

                                            value=tickers[:1] if tickers else [],

                                            multi=True,

                                            placeholder="Select ticker(s)...",

                                            style={

                                                "borderRadius": "10px"

                                            }

                                        )

                                    ]

                                ),

                                style={

                                    "borderRadius": "14px",

                                    "border": "1px solid #E3E8EF",

                                    "boxShadow": "0px 2px 10px rgba(0,0,0,0.06)",

                                    "marginBottom": "20px"

                                }

                            ),
                            
                            # Date Range
                            dbc.Card(

                                dbc.CardBody(

                                    [

                                        html.H6(

                                            "📅 Time Period",

                                            className="fw-bold",

                                            style={
                                                "color": "#0F4C81"
                                            }

                                        ),

                                        html.P(

                                            "Select the historical period for analysis.",

                                            className="text-muted mb-3",

                                            style={
                                                "fontSize": "13px"
                                            }

                                        ),

                                        dcc.DatePickerRange(

                                            id="date-picker",

                                            start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),

                                            end_date=datetime.now().strftime("%Y-%m-%d"),

                                            display_format="YYYY-MM-DD",

                                            style={
                                                "width": "100%"
                                            }

                                        )

                                    ]

                                ),

                                style={

                                    "borderRadius": "14px",

                                    "border": "1px solid #E3E8EF",

                                    "boxShadow": "0px 2px 10px rgba(0,0,0,0.06)",

                                    "marginBottom": "20px"

                                }

                            ),
                            
                            # Analysis Type
                            dbc.Card(

                                dbc.CardBody(

                                    [

                                        html.H6(

                                            "📊 Analysis Type",

                                            className="fw-bold",

                                            style={
                                                "color": "#0F4C81"
                                            }

                                        ),

                                        html.P(

                                            "Choose the type of financial analysis to display.",

                                            className="text-muted mb-3",

                                            style={
                                                "fontSize": "13px"
                                            }

                                        ),

                                        dcc.Dropdown(

                                            id="analysis-type",

                                            options=[

                                                {
                                                    "label": "📈 Price Trends",
                                                    "value": "price"
                                                },

                                                {
                                                    "label": "📊 Technical Indicators",
                                                    "value": "technical"
                                                },

                                                {
                                                    "label": "📉 Returns Analysis",
                                                    "value": "returns"
                                                },

                                                {
                                                    "label": "💼 Portfolio View",
                                                    "value": "portfolio"
                                                },

                                                {
                                                    "label": "📦 Volume Analysis",
                                                    "value": "volume"
                                                }

                                            ],

                                            value="price",

                                            style={

                                                "borderRadius": "10px"

                                            }

                                        )

                                    ]

                                ),

                                style={

                                    "borderRadius": "14px",

                                    "border": "1px solid #E3E8EF",

                                    "boxShadow": "0px 2px 10px rgba(0,0,0,0.06)",

                                    "marginBottom": "20px"

                                }

                            ),
                            
                                html.Hr(),

                                html.Div(

                                    [

                                        html.Div(
                                            "✓ Live Dashboard",
                                            style={
                                                "fontWeight": "bold",
                                                "color": "#2E7D32",
                                                "fontSize": "16px"
                                            }
                                        ),

                                        html.Small(
                                            "Charts, tables and insights update automatically whenever you change a filter.",
                                            style={
                                                "color": "#6c757d"
                                            }
                                        )

                                    ],

                                    style={
                                        "padding": "10px 5px"
                                    }

                                )
                                        ])

                            ],

                            className="shadow border-0 rounded-4",

                            style={

                                "backgroundColor": "#ffffff",

                                "padding": "10px"

                            }

                        )
                    ], width=3),
            
            # Main Content Area
            dbc.Col([
                # Tabbed Content
                dbc.Tabs([
                    # Chart Tab
                    dbc.Tab([

                        dcc.Loading(

                            id="loading-charts",

                            type="dot",

                            color="#0F4C81",

                            fullscreen=False,

                            children=[

                                dbc.Card(

                                    [

                                        dbc.CardBody(

                                            [

                                                html.H4(

                                                    id="main-chart-title",

                                                    className="fw-bold text-primary"

                                                ),

                                                html.P(

                                                    id="main-chart-description",

                                                    className="text-muted"

                                                ),

                                                dcc.Graph(

                                                    id="main-chart"

                                                )

                                            ]

                                        )

                                    ],

                                    className="shadow-sm border-0 rounded-4 mb-4"

                                ),

                                dbc.Card(

                                    [

                                        dbc.CardBody(

                                            [

                                                html.H4(

                                                    id="secondary-chart-title",

                                                    className="fw-bold text-primary"

                                                ),

                                                html.P(

                                                    id="secondary-chart-description",

                                                    className="text-muted"

                                                ),

                                                dcc.Graph(

                                                    id="secondary-chart"

                                                )

                                            ]

                                        )

                                    ],

                                    className="shadow-sm border-0 rounded-4"

                                )

                            ]

                        )

                    ], label="📈 Charts"),
                    
                    # Data Tab
                    dbc.Tab([
                        dcc.Loading(
                            id="loading-data",
                            type="dot",
                            children=[
                                html.H5("📋Financial Data", className="mt-3"),
                                dash_table.DataTable(

                                    id='data-table',

                                    columns=[],

                                    data=[],

                                    page_size=10,

                                    sort_action="native",

                                    filter_action="native",

                                    page_action="native",

                                    style_table={
                                        'overflowX': 'auto',
                                        'borderRadius': '15px',
                                        'overflow': 'hidden'
                                    },

                                    style_cell={
                                        'textAlign': 'center',
                                        'padding': '12px',
                                        'fontFamily': 'Segoe UI',
                                        'fontSize': '14px',
                                        'border': '1px solid #EAEAEA',
                                        'minWidth': '120px',
                                        'maxWidth': '200px',
                                        'whiteSpace': 'normal'
                                    },

                                    style_header={
                                        'backgroundColor': '#0F4C81',
                                        'color': 'white',
                                        'fontWeight': 'bold',
                                        'fontSize': '15px',
                                        'border': 'none'
                                    },

                                    style_data={
                                        'backgroundColor': 'white',
                                        'color': '#2C3E50'
                                    },

                                    style_data_conditional=[

                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': '#F8F9FA'
                                        },

                                        {
                                            'if': {'state': 'active'},
                                            'backgroundColor': '#D6EAF8',
                                            'border': '1px solid #0F4C81'
                                        },

                                        {
                                            'if': {'state': 'selected'},
                                            'backgroundColor': '#AED6F1',
                                            'border': '1px solid #0F4C81'
                                        }

                                    ],

                                    fixed_rows={'headers': True}

                                ),
                                dbc.Button(
                                        "📥 Download CSV",
                                        id="download-button",
                                        color="success",
                                        className="mt-3 w-100",
                                        style={
                                            "borderRadius": "10px",
                                            "fontWeight": "bold",
                                            "padding": "12px"
                                        }
                                    ), dcc.Download(id="download-data")
                            ]
                        )
                    ], label="📋 Data", tab_id="data"),
                    
                    # Metrics Tab
                    dbc.Tab([
                        dcc.Loading(
                            id="loading-metrics",
                            type="dot",
                            children=[
                                html.H5("📊 Performance Metrics", className="mt-3"),
                                dash_table.DataTable(
                                    id='metrics-table',
                                    columns=[
                                        {'name': 'Ticker', 'id': 'Ticker'},
                                        {'name': 'Avg Return (%)', 'id': 'Avg_Return'},
                                        {'name': 'Volatility (%)', 'id': 'Volatility'},
                                        {'name': 'Period High', 'id': 'Period_High'},
                                        {'name': 'Period Low', 'id': 'Period_Low'},
                                        {'name': 'Avg Volume', 'id': 'Avg_Volume'}
                                    ],
                                    data=ticker_metrics.to_dict('records'),

                                    page_size=10,

                                    sort_action="native",

                                    filter_action="native",

                                    page_action="native",

                                    style_table={
                                        'overflowX': 'auto',
                                        'borderRadius': '15px',
                                        'overflow': 'hidden'
                                    },

                                    style_cell={
                                        'textAlign': 'center',
                                        'padding': '12px',
                                        'fontFamily': 'Segoe UI',
                                        'fontSize': '14px',
                                        'border': '1px solid #EAEAEA',
                                        'minWidth': '120px',
                                        'maxWidth': '200px',
                                        'whiteSpace': 'normal'
                                    },

                                    style_header={
                                        'backgroundColor': '#0F4C81',
                                        'color': 'white',
                                        'fontWeight': 'bold',
                                        'fontSize': '15px',
                                        'border': 'none'
                                    },

                                    style_data={
                                        'backgroundColor': 'white',
                                        'color': '#2C3E50'
                                    },

                                    style_data_conditional=[

                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': '#F8F9FA'
                                        },

                                        {
                                            'if': {'state': 'active'},
                                            'backgroundColor': '#D6EAF8',
                                            'border': '1px solid #0F4C81'
                                        },

                                        {
                                            'if': {'state': 'selected'},
                                            'backgroundColor': '#AED6F1',
                                            'border': '1px solid #0F4C81'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{Avg_Return} > 0',
                                                'column_id': 'Avg_Return'
                                            },
                                            'color': '#28A745',
                                            'fontWeight': 'bold'
                                        },

                                        {
                                            'if': {
                                                'filter_query': '{Avg_Return} < 0',
                                                'column_id': 'Avg_Return'
                                            },
                                            'color': '#DC3545',
                                            'fontWeight': 'bold'
                                        }

                                    ],

                                    fixed_rows={'headers': True}

                                )
                            ]
                        )
                    ], label="📊 Metrics", tab_id="metrics"),
                    
                    # Correlation Tab
                    dbc.Tab([
                        dcc.Loading(
                            id="loading-correlation",
                            type="dot",
                            children=[
                                html.H5("🔗 Correlation Matrix", className="mt-3"),
                                    dbc.Card(
                                        dbc.CardBody(
                                            dcc.Graph(id='correlation-heatmap'),
                                        ),

                                            className="dashboard-card mb-3"

                                        ),
                                html.H5("📊 Scatter Matrix", className="mt-4"),
                                    dbc.Card(
                                        dbc.CardBody(
                                            dcc.Graph(id='scatter-matrix')
                                        ),

                                            className="dashboard-card mb-3"

                                        ),
                            ]
                        )
                    ], label="🔗 Correlation", tab_id="correlation"),

                    dbc.Tab(

                        [

                            dbc.Row(

                                [

                                    dbc.Col(

                                        dbc.Card(

                                            dbc.CardBody([

                                                html.H5("📈 Sharpe Ratio"),

                                                html.H3(id="sharpe-ratio")

                                            ]),

                                            className="display-3 text-center mt-4" #"dashboard-card"

                                        ),

                                        width=3

                                    ),

                                    dbc.Col(

                                        dbc.Card(

                                            dbc.CardBody([

                                                html.H5("📉 Maximum Drawdown"),

                                                html.H3(id="max-drawdown")

                                            ]),

                                            className="display-3 text-center mt-4"

                                        ),

                                        width=3

                                    ),

                                    dbc.Col(

                                        dbc.Card(

                                            dbc.CardBody([

                                                html.H5("📊 Annual Volatility"),

                                                html.H3(id="annual-volatility")

                                            ]),

                                            className="display-3 text-center mt-4"

                                        ),

                                        width=3

                                    ),

                                    dbc.Col(

                                        dbc.Card(

                                            dbc.CardBody([

                                                html.H5("⚠️ VaR (95%)"),

                                                html.H3(id="value-at-risk")

                                            ]),

                                            className="display-3 text-center mt-4"

                                        ),

                                        width=3

                                    )

                                ],

                                className="mt-3"

                            ),
                                dbc.Row(

                                    [

                                        dbc.Col(

                                            dbc.Card(

                                                dbc.CardBody([

                                                    html.H3(
                                                        "🛡 Portfolio Health Score",
                                                        className="text-center text-primary fw-bold"
                                                    ),

                                                    html.H1(
                                                        id="portfolio-score",
                                                        className="display-3 text-center mt-4"
                                                    ),

                                                    html.H4(
                                                        id="portfolio-rating",
                                                        className="text-center text-success"
                                                    ),

                                                    html.Hr(),

                                                    html.P(
                                                        id="portfolio-comment",
                                                        className="text-center fs-5"
                                                    )

                                                ]),

                                                className="dashboard-card"

                                            ),

                                            width=12

                                        )

                                    ],

                                    className="mt-4"

                                ),

                                    dbc.Row(

                                        [

                                            dbc.Col(

                                                dbc.Card(

                                                    dbc.CardBody([

                                                        html.H3(
                                                            "💡 Portfolio Recommendation",
                                                            className="text-center text-primary fw-bold"
                                                        ),

                                                        html.H2(
                                                            id="portfolio-action",
                                                            className="text-center mt-4"
                                                        ),

                                                        html.P(
                                                            id="portfolio-reason",
                                                            className="text-center fs-5"
                                                        )

                                                    ]),

                                                    className="dashboard-card"

                                                ),

                                                width=12

                                            )

                                        ],

                                        className="mt-4"

                                    ),

                        ],

                        label="⚠️ Risk Analytics",

                        tab_id="risk"

                    ),
                ], id="tabs", active_tab="charts")
            ], width=9)
        ]),
        
        # Hidden div for storing intermediate values
        dcc.Store(id='data-store'),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P([
                    f"{APP_NAME} • Built with Dash, Plotly & Python • {APP_VERSION} • Built by {AUTHOR}",
                    html.Br(),
                    html.A(
                        "View Source on GitHub",
                        href=LINK,
                        target="_blank",
                        style={"textDecoration": "none"}
                    )
                ],
                className="text-center text-muted small")
            ])
        ], className="mt-4")
    ], fluid=True,
    style={
        "backgroundColor": "#eef4d9",
        "minHeight": "100vh",
        "padding": "20px"
    })