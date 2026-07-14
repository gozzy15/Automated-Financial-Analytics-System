import plotly.graph_objects as go


def apply_dashboard_style(
    fig: go.Figure,
    *,
    title: str,
    height: int,
    xaxis_title: str | None = None,
    yaxis_title: str | None = None,
    hovermode: str = "x unified",
    legend_orientation: str = "v"
) -> go.Figure:
    """
    Apply a consistent dashboard theme to a Plotly figure.
    """

    fig.update_layout(

        title={
            "text": title,
            "x": 0.5,
            "font": {
                "size": 24,
                "color": "#0F4C81"
            }
        },

        height=height,

        template="plotly_white",

        paper_bgcolor="#ffffff",

        plot_bgcolor="#ffffff",

        font={
            "family": "Segoe UI",
            "size": 14,
            "color": "#2c3e50"
        },

        legend={
            "orientation": legend_orientation,
            "y": 1.00,
            "x": 1.00
        },

        hovermode=hovermode,

        margin={
            "l": 50,
            "r": 30,
            "t": 80,
            "b": 50
        }
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

        hoverlabel={

            "bgcolor": "white",

            "font_size": 14,

            "font_family": "Segoe UI"

        }

    )

    if xaxis_title:

        fig.update_xaxes(title_text=xaxis_title)

    if yaxis_title:

        fig.update_yaxes(title_text=yaxis_title)

    return fig