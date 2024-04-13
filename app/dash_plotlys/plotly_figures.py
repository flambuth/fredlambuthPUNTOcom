import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

###########################
#used to to plot artist history
def chart_scatter_plotly(
        dates,
        positions,
        songs_or_arts,
):
    '''
    Accepts a ACE.chart_hits object.
    Returns a plotly line figure
    '''
    fig = px.scatter(
    x=dates,
    y=positions,
    color=songs_or_arts,
    )
    
    fig.update_layout(yaxis=dict(autorange="reversed"))

    # Add titles to the x and y axes
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Chart Position",
        template='plotly_dark',
        legend_title_text='',
    )
    
    return fig

######################
#Used in /spotify/monthly view.
def year_month_line_chart(
        dates,
        positions,
        art_names
):
    
    year_month = dates[0].strftime("%Y-%b")

    fig = px.line(
    x=dates,
    y=positions,
    color=art_names,
    )
    #print("Creating figure with x:", dates, "y:", positions, "colors:", art_names)
    fig.update_layout(yaxis=dict(autorange="reversed"))

    # Add titles to the x and y axes
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Chart Position",
        template='plotly_dark',
        showlegend=False,
        title=year_month,
        title_font=dict(size=20, family='Arial', color='#CEFCBA'),
    )

    
    return fig


##############################
#global dash figures

def songs_line_chart(df):
    '''
    Returns a line chart of the input df. Uses
    '''
    cut_off_at=30
    #df['name_truncated'] = df['name'].str.slice(0, 30)
    df['name_truncated'] = df['name'].apply(lambda x: x[:cut_off_at] if '(' not in x else x.split('(')[0][:cut_off_at])
    df['name_artists'] = df['name_truncated']# + ' - ' + df['artists']
    first_date = min(df.snapshot_date)
    last_date = max(df.snapshot_date)

    fig = px.line(
        data_frame=df,
        x=df.snapshot_date,
        y=df.daily_rank,
        color=df.name_artists,
        hover_data={'name_artists': True, 'artists': True},
        template='plotly_dark',
        #title=f"The Top 10 Songs Since {first_date}"
    )

    fig.update_layout(
        yaxis_title=" ",
        xaxis_title=" ",
        height=880, 
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            title_text=f"The Top 10 Songs from {first_date} - {last_date}",
            traceorder="normal",  # Stack legend title on top of legend items
            itemsizing="constant",  # Ensure constant item size across legends
            itemwidth=31,
            tracegroupgap=20,
        ),
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
    )
    # Invert the y-axis
    fig.update_yaxes(autorange="reversed",)

    return fig


def artists_hbar_chart(df_top_artists):
    '''
    Returns a line chart of the input df. Uses
    '''

    fig = px.bar(
        y=df_top_artists.artist,
        x=df_top_artists.appearances,
        color=df_top_artists.unique_songs,
        orientation='h',
        template='plotly_dark',
        color_continuous_scale='darkmint',  # You can customize the color scale here
        range_color=[0, 10],
    )

    fig.update_layout(
        yaxis_title="",
        xaxis_title="",
        title='Most Chart Appearances',
        xaxis=dict(range=[0, max(df_top_artists['appearances']) + 1]),  # Set the range_x parameter
        
    )

    # Invert the y-axis
    fig.update_yaxes(autorange="reversed")
    fig.update(layout_coloraxis_showscale=False)

    annotation_text = "Color Represents Unique Song Count"
    annotation_x = 5  # X-coordinate of the annotation
    annotation_y = 0  # Y-coordinate of the annotation

    fig.add_annotation(
        text=annotation_text,
        x=annotation_x,
        y=annotation_y,
        #showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-30,
        font=dict(size=8)
    )

    return fig

#######################
#big dashboard figures
def day_of_week_bars(
     datetimes,
     y_threshold   
):
    series_dts = pd.Series(datetimes)
    n_weeks = int(series_dts.dt.date.nunique() / 7)
    if n_weeks == 0:
        n_weeks = 1
    grouped_by_day_count = series_dts.groupby(series_dts.dt.day_name()).count()
    grouped_by_day = grouped_by_day_count / n_weeks
    # Convert the index (day names) to strings
    grouped_by_day.index = grouped_by_day.index.astype(str)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # Create bar chart using Plotly Express
    fig = px.bar(
        x=grouped_by_day.index, 
        y=grouped_by_day.values, 
        template='plotly_dark',
        color_discrete_sequence=['green'])
    fig.update_layout(
        title='Average Songs By Day of Week',
        xaxis={'categoryorder': 'array', 'categoryarray': day_order},
        #displayModeBar=False,
    )
    fig.update_xaxes(title='')
    fig.update_yaxes(title='')
    fig.add_hline(y=y_threshold, 
                  line_dash='dot', 
                  line_color='red', 
                  annotation_text=f'Avg: {y_threshold}', 
                  annotation_position='top right')
    return fig


def un_known_pie_chart(known, unknown):
    names = ['Known', 'Unknown']
    lengths = [len(known), len(unknown)]
    
    # Create a pie chart using Plotly Graph Objects
    fig = go.Figure(data=[go.Pie(labels=names, values=lengths, hole=0.3, marker=dict(colors=['palegreen', 'darkgreen']))])
    
    # Update layout to remove the legend outside the figure
    fig.update_layout(
        showlegend=False, 
        template='plotly_dark', 
        title=f'{len(known) + len(unknown)} distinct artists', 
        #width=330,
        #height=400,
        #displayModeBar=False
        )
    
    # Add text labels inside each pie slice
    fig.update_traces(textinfo='percent+label', textposition='inside')
    
    return fig


def hourly_listening_line_chart(series_of_avgs):

    fig = px.line(
        x=series_of_avgs.index, 
        y=series_of_avgs.values,
        height=200, 
    )
    # Update layout to remove the legend outside the figure
    fig.update_layout(
        showlegend=False, 
        template='plotly_dark', 
        title='Daily Listening Pattern',
        xaxis=dict(showgrid=False, title='Hour of Day', linecolor='rgba(0,0,0,0)'),  # Remove x-axis grid lines and set title
        yaxis=dict(showgrid=False, title='Songs', linecolor='rgba(0,0,0,0)'),  # Remove y-axis grid lin
        #displayModeBar=False,
        )   
    return fig