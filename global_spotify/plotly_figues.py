import plotly.express as px

def track_history_line_plot(track_history_df):
    '''
    Accepts a Polars dataframe.
    Returns a plotly figure
    '''

    prim_arts = track_history_df.select('primary_artist').to_series().to_list()
    feat_arts = track_history_df.select('featured_artists').to_series().to_list()
    song_names = track_history_df.select('name').to_series().to_list()
    fig = px.line(
        x=track_history_df.select('snapshot_date').to_series().to_list(),
        y=track_history_df.select('daily_rank').to_series().to_list(),
        color = track_history_df.select('name').to_series().to_list(),
        hover_data={'primary_artists': prim_arts, 'featured_artists': feat_arts, 'songs': song_names},
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
        hovertemplate='%{y}<br>Artist= %{customdata[0]}<br>Song= %{customdata[2]}<br><extra></extra>'
    )
    return fig