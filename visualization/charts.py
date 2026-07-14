import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

PRIMARY_COLOR = "#0F4C81"
TEXT_COLOR = "#2C3E50"
GRID_COLOR = "#ECECEC"
BACKGROUND = "#FFFFFF"
FONT = "Segoe UI"

def apply_axis_style(fig):

    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        zeroline=False
    )

    return fig

def apply_hover_style(fig):

    fig.update_traces(

        hoverlabel=dict(

            bgcolor="white",

            font_family=FONT,

            font_size=14

        )

    )

    return fig

def apply_chart_theme(fig, title, height, legend=True):
    """
    Apply a consistent professional theme to Plotly figures.
    """

    fig.update_layout(

        height=height,

        template="plotly_white",

        paper_bgcolor=BACKGROUND,

        plot_bgcolor=BACKGROUND,

        font=dict(
            family=FONT,
            size=14,
            color=TEXT_COLOR
        ),

        title=dict(
            text=title,
            x=0.5,
            font=dict(
                size=24,
                color=PRIMARY_COLOR
            )
        ),

        margin=dict(
            l=50,
            r=30,
            t=80,
            b=50
        )

    )

    if legend:

        fig.update_layout(

            legend=dict(

                orientation="v",

                y=1.00,

                x=1.00

            )

        )

    return fig


def create_main_chart(
        data_dict,
        analysis_type,
        latest_prices=None
    ):
    """Create main chart based on analysis type"""
    
    if analysis_type == 'price':
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price Movement', 'Volume'),
            row_heights=[0.7, 0.3]
        )
        
        for ticker, df in data_dict.items():
            # Price chart
            fig.add_trace(
                go.Candlestick(
                    x=df['Date'],
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name=ticker,
                    showlegend=True
                ),
                row=1, col=1
            )
            
            # Volume chart
            colors = ['red' if row['Close'] < row['Open'] else 'green' 
                     for _, row in df.iterrows()]
            
            fig.add_trace(
                go.Bar(
                    x=df['Date'],
                    y=df['Volume'],
                    name=f"{ticker} Volume",
                    marker_color=colors,
                    showlegend=False,
                    opacity=0.5
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=600,
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(
                family="Segoe UI",
                size=14,
                color="#2c3e50"
            ),
            title=dict(
                text="Price and Volume Analysis",
                x=0.5,
                font=dict(
                    size=24,
                    color="#0F4C81"
                )
            ),
            legend=dict(
                orientation="v",
                y=1.00,
                x=1.00
            ),
            hovermode="x unified",
            margin=dict(
                l=50,
                r=30,
                t=80,
                b=50
            ),
            xaxis_rangeslider_visible=False
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False
        )

        fig.update_traces(
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Segoe UI"
            )
        )
    
    elif analysis_type == 'technical':
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price with MAs', 'RSI', 'Daily Returns'),
            row_heights=[0.4, 0.3, 0.3]
        )
        
        for ticker, df in data_dict.items():
            # Price with Moving Averages
            fig.add_trace(
                go.Scatter(x=df['Date'], y=df['Close'], 
                          name=f'{ticker} Close', 
                          mode='lines',
                          line=dict(width=2)),
                row=1, col=1
            )
            
            if 'SMA_20' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['Date'], y=df['SMA_20'], 
                              name=f'{ticker} SMA 20',
                              mode='lines',
                              line=dict(dash='dash', width=1)),
                    row=1, col=1
                )
            
            if 'SMA_50' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['Date'], y=df['SMA_50'], 
                              name=f'{ticker} SMA 50',
                              mode='lines',
                              line=dict(dash='dot', width=1)),
                    row=1, col=1
                )
            
            # RSI
            if 'RSI' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['Date'], y=df['RSI'], 
                              name=f'{ticker} RSI',
                              mode='lines'),
                    row=2, col=1
                )
            
            # Daily Returns
            if 'Daily_Return' in df.columns:
                colors = ['green' if x >= 0 else 'red' for x in df['Daily_Return']]
                fig.add_trace(
                    go.Bar(x=df['Date'], y=df['Daily_Return']*100, 
                          name=f'{ticker} Returns',
                          marker_color=colors),
                    row=3, col=1
                )
        
        # Add RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     opacity=0.5, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     opacity=0.5, row=2, col=1)
        
        fig.update_layout(
            height=700,
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(
                family="Segoe UI",
                size=14,
                color="#2c3e50"
            ),
            title=dict(
                text="Technical Indicators",
                x=0.5,
                font=dict(
                    size=24,
                    color="#0F4C81"
                )
            ),
            legend=dict(
                orientation="v",
                y=1.00,
                x=1.00
            ),
            hovermode="x unified",
            margin=dict(
                l=50,
                r=30,
                t=80,
                b=50
            )
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False
        )

        fig.update_traces(
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Segoe UI"
            )
        )
    
    elif analysis_type == 'returns':
        fig = go.Figure()
        
        for ticker, df in data_dict.items():
            if 'Cumulative_Return' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['Date'], 
                              y=df['Cumulative_Return']*100,
                              name=ticker,
                              mode='lines+markers',
                              line=dict(width=2))
                )
        
        fig.update_layout(
            height=500,
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(
                family="Segoe UI",
                size=14,
                color="#2c3e50"
            ),
            title=dict(
                text="Cumulative Returns (%)",
                x=0.5,
                font=dict(
                    size=24,
                    color="#0F4C81"
                )
            ),
            xaxis_title="Date",
            yaxis_title="Cumulative Return (%)",
            legend=dict(
                orientation="h",
                y=1.05,
                x=0.01
            ),
            hovermode="x unified",
            margin=dict(
                l=50,
                r=30,
                t=80,
                b=50
            )
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False,
            title_font=dict(
                size=16,
                color="#2c3e50"
            )
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False,
            title_font=dict(
                size=16,
                color="#2c3e50"
            )
        )

        fig.update_traces(
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Segoe UI"
            )
        )
    
    elif analysis_type == 'portfolio':
        # Create pie chart of current allocations
        if latest_prices is None:
            latest_prices = pd.DataFrame()

        portfolio_df = latest_prices[
            latest_prices["Ticker"].isin(list(data_dict.keys()))
        ]
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'pie'}, {'type': 'bar'}]],
            subplot_titles=('Portfolio Allocation', 'Performance Comparison')
        )
        
        # Pie chart
        fig.add_trace(
            go.Pie(
                labels=portfolio_df['Ticker'],
                values=portfolio_df['Close'],
                hole=0.3,
                textinfo='label+percent'
            ),
            row=1, col=1
        )
        
        # Bar chart
        for ticker, df in data_dict.items():
            if not df.empty:
                total_return = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / 
                               df['Close'].iloc[0] * 100)
                fig.add_trace(
                    go.Bar(
                        x=[ticker],
                        y=[total_return],
                        name=ticker,
                        text=f"{total_return:.1f}%",
                        textposition='auto'
                    ),
                    row=1, col=2
                )
        
        fig.update_layout(
            height=500,
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(
                family="Segoe UI",
                size=14,
                color="#2c3e50"
            ),
            title=dict(
                text="Portfolio Analysis",
                x=0.5,
                font=dict(
                    size=24,
                    color="#0F4C81"
                )
            ),
            legend=dict(
                orientation="v",
                y=1.00,
                x=1.00
            ),
            hovermode="closest",
            margin=dict(
                l=50,
                r=30,
                t=80,
                b=50
            )
        )

        fig.update_traces(
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Segoe UI"
            )
        )
    
    else:  # volume analysis
        fig = go.Figure()
        
        for ticker, df in data_dict.items():
            fig.add_trace(
                go.Scatter(x=df['Date'], y=df['Volume'],
                          name=ticker,
                          mode='lines',
                          line=dict(width=1),
                          opacity=0.7)
            )
        
        fig.update_layout(
            height=500,
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(
                family="Segoe UI",
                size=14,
                color="#2c3e50"
            ),
            title=dict(
                text="Volume Analysis",
                x=0.5,
                font=dict(
                    size=24,
                    color="#0F4C81"
                )
            ),
            xaxis_title="Date",
            yaxis_title="Volume",
            legend=dict(
                orientation="v",
                y=1.00,
                x=1.00
            ),
            hovermode="x unified",
            margin=dict(
                l=50,
                r=30,
                t=80,
                b=50
            )
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False,
            title_font=dict(
                size=16,
                color="#2c3e50"
            )
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False,
            title_font=dict(
                size=16,
                color="#2c3e50"
            )
        )

        fig.update_traces(
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Segoe UI"
            )
        )
    
    return fig

def create_secondary_chart(data_dict, analysis_type):
    """Create secondary chart"""
    
    if len(data_dict) > 1:
        # Compare closing prices
        fig = go.Figure()
        
        for ticker, df in data_dict.items():
            # Normalize prices for comparison
            if not df.empty:
                normalized_price = df['Close'] / df['Close'].iloc[0] * 100
                fig.add_trace(
                    go.Scatter(x=df['Date'], y=normalized_price,
                              name=ticker,
                              mode='lines',
                              line=dict(width=2))
                )
        
        fig.update_layout(
            height=400,
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(
                family="Segoe UI",
                size=14,
                color="#2c3e50"
            ),
            title=dict(
                text="Normalized Price Comparison (Base = 100)",
                x=0.5,
                font=dict(
                    size=24,
                    color="#0F4C81"
                )
            ),
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            legend=dict(
                orientation="v",
                y=1.00,
                x=1.00,
                bgcolor="rgba(255,255,255,0.8)"
            ),
            hovermode="x unified",
            margin=dict(
                l=50,
                r=30,
                t=80,
                b=50
            )
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False,
            title_font=dict(
                size=16,
                color="#2c3e50"
            )
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False,
            title_font=dict(
                size=16,
                color="#2c3e50"
            )
        )

        fig.update_traces(
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Segoe UI"
            )
        )
    else:
        # Show volatility or other single-stock analysis
        fig = go.Figure()
        
        for ticker, df in data_dict.items():
            if 'Daily_Return' in df.columns:
                # Histogram of returns
                fig.add_trace(
                    go.Histogram(
                        x=df['Daily_Return']*100,
                        name=ticker,
                        nbinsx=30,
                        opacity=0.7
                    )
                )
        
        fig.update_layout(
            height=400,
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(
                family="Segoe UI",
                size=14,
                color="#2c3e50"
            ),
            title=dict(
                text="Returns Distribution",
                x=0.5,
                font=dict(
                    size=24,
                    color="#0F4C81"
                )
            ),
            xaxis_title="Daily Return (%)",
            yaxis_title="Frequency",
            hovermode="closest",
            bargap=0.1,
            margin=dict(
                l=50,
                r=30,
                t=80,
                b=50
            )
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False,
            title_font=dict(
                size=16,
                color="#2c3e50"
            )
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#ECECEC",
            zeroline=False,
            title_font=dict(
                size=16,
                color="#2c3e50"
            )
        )

        fig.update_traces(
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Segoe UI"
            )
        )
    
    return fig

def create_correlation_heatmap(returns):
    # Correlation matrix heatmap
    corr_matrix = returns.corr()
    
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        text=corr_matrix.round(2).values,
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    heatmap_fig.update_layout(
        height=500,
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(
            family="Segoe UI",
            size=14,
            color="#2c3e50"
        ),
        title=dict(
            text="Correlation Matrix of Returns",
            x=0.5,
            font=dict(
                size=24,
                color="#0F4C81"
            )
        ),
        margin=dict(
            l=50,
            r=30,
            t=80,
            b=50
        )
    )

    heatmap_fig.update_xaxes(
        showgrid=False,
        title_font=dict(
            size=16,
            color="#2c3e50"
        )
    )

    heatmap_fig.update_yaxes(
        showgrid=False,
        title_font=dict(
            size=16,
            color="#2c3e50"
        )
    )

    heatmap_fig.update_traces(
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Segoe UI"
        )
    )
    return heatmap_fig

def create_scatter_matrix(returns):
    # Scatter matrix
    if len(returns.columns) <= 5:  # Limit to 5 for performance
        scatter_fig = px.scatter_matrix(
            returns,
            dimensions=returns.columns,
            title="Scatter Matrix of Returns"
        )
        scatter_fig.update_layout(height=600)
    else:
        # If too many tickers, show sample
        scatter_fig = px.scatter(
            returns,
            x=returns.columns[0],
            y=returns.columns[1],
            title=f"Scatter Plot: {returns.columns[0]} vs {returns.columns[1]}"
        )
        scatter_fig.update_layout(height=500)

    return scatter_fig