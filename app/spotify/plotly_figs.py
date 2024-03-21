from app.spotify import daily_funcs
from app.models.charts import daily_artists, daily_tracks
from app.dash_plotlys.plotly_figures import chart_scatter_plotly


def top_5_artists_fig():
    top_5_names = [i[0] for i in daily_funcs.top_ever_daily_artists(5)]
    top_5_data = daily_artists.query.filter(
        daily_artists.art_name.in_(top_5_names)
    ).all()
    x = [i.date for i in top_5_data]
    y = [i.position for i in top_5_data]
    z = [i.art_name for i in top_5_data]
    fig = chart_scatter_plotly(
        x,y,z
    )
    return fig

def top_5_tracks_fig():
    top_5_names = [i[0] for i in daily_funcs.top_ever_daily_tracks(5)]

    top_5_data = daily_tracks.query.filter(
        daily_tracks.song_name.in_(top_5_names)
    ).all()

    x = [i.date for i in top_5_data]
    y = [i.position for i in top_5_data]
    z = [f"{i.art_name}-{i.song_name}" for i in top_5_data]
    fig = chart_scatter_plotly(
        x,y,z
    )
    return fig