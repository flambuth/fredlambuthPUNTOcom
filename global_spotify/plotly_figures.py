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
    fig.update_yaxes(
        autorange="reversed",
    )
    fig.update_layout(
        yaxis_title="Daily Rank",
        xaxis_title=" ",
        height=880, 
        hovermode="x unified",
        showlegend=False,
        
        title=dict(    
            text=track_history_df.country.iloc[0],
            font=dict(size=30),
            x=0.5,              # Horizontal centering (0.5 means center)
            xanchor='center',    # Align the title text to the center
            y=0.95,             # Adjust the vertical position (optional)
            yanchor='top',       # Ensure it stays at the top
            automargin=True),
        )

    fig.update_traces(
        hovertemplate='%{y}<br>Artist= %{customdata[0]}<br>Song= %{customdata[1]}<br><extra></extra>'
    )
    return fig