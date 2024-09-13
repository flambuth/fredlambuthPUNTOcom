import plotly.express as px

def track_history_line_plot(track_history_df):
    '''
    Accepts a Polars dataframe.
    Returns a plotly figure
    '''

    fig = px.line(
        track_history_df,
        x='snapshot_date',
        y='daily_rank',
        color = 'name',
        hover_data=['primary_artist','name'],
        template='plotly_dark',
    )
    fig.update_yaxes(autorange="reversed",)
    fig.update_layout(
        yaxis_title=" ",
        xaxis_title=" ",
        height=880, 
        annotations=[
            dict(
                text="Artist name can be found in hover text. Double Legend to Isolate Line",
                x=0.5,
                y=-0.12,
                showarrow=False,
                xref="paper",
                yref="paper",
                font=dict(
                    size=8,
                    color="limegreen"
                )
            )
        ],
        hovermode="x unified",
        showlegend=False,
    )

    fig.update_traces(
        hovertemplate='%{y}<br>Artist= %{customdata[0]}<br>Song= %{customdata[1]}<br><extra></extra>'
    )
    return fig