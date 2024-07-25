import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import timedelta

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

###############################
#POLAR CHART of 24 Hrs of Listening

def polar_chart_of_am_pm(
    date_obj,
    am_values,
    pm_values,
    am_hours = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
):
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=am_values,
        theta=am_hours,
        fill='toself',
        name='A.M.',
        line=dict(color='chartreuse'),  # Set line color to red
        marker=dict(color='chartreuse')  # Set marker color to red
    ))
    fig.add_trace(go.Scatterpolar(
        r=pm_values,
        theta=am_hours,
        fill='toself',
        name='P.M.',
        line=dict(color='green'),  # Set line color to blue
        marker=dict(color='green')  # Set marker color to blue
    ))

    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=False,
          range=[0, 5]
        )),
      showlegend=False
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, max(max(am_values), max(pm_values))]
            ),
            angularaxis=dict(
                tickmode='array',
                tickvals=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
                ticktext=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
                direction='clockwise',
                rotation=90
            )
        ),
        showlegend=True,
        template='plotly_dark',
        title = f"{ date_obj.strftime('%A') }, { date_obj.isoformat() }"
    )

    return fig


def seven_days_of_polar_charts(week_of_figs, date_obj, max_range):
    '''
    Takes a 7 item list of plotly figures and places them in a 3x3 grid of subplots
    with two blank spots on the second and third rows, and adds horizontal spacing
    between subplots.
    '''
    # Define subplot titles for the three rows
    subplot_titles = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "", ""]

    fig = make_subplots(
        rows=3, cols=3,
        specs=[[{'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}],
               [{'type': 'polar'}, {'type': 'polar'}, None],
               [{'type': 'polar'}, {'type': 'polar'}, None]],
        subplot_titles=subplot_titles,
        horizontal_spacing=0.1,  # Adjust this value for horizontal spacing
        vertical_spacing=0.1     # Adjust this value for vertical spacing
    )

    # Add each figure to the subplot
    for i, day_fig in enumerate(week_of_figs):
        row = 1 if i < 3 else (2 if i < 5 else 3)
        col = i + 1 if i < 3 else (i - 2 if i < 5 else i - 4)
        for trace in day_fig.data:
            trace.showlegend = (i == 0)  # Show legend only for the first subplot
            fig.add_trace(trace, row=row, col=col)
    
    # Define a consistent angular and radial axis configuration
    angularaxis = dict(
        tickmode='array',
        tickvals=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
        ticktext=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
        direction='clockwise',
        rotation=90
    )

    midpoint = max_range / 2
    radialaxis = dict(
        visible=True,
        range=[0, max_range],
        showgrid=False,
        tickmode='array',
        tickvals=[0, midpoint, max_range],
        ticktext=['0', f'{midpoint:.0f}', str(max_range)]
    )

    # Apply the same axis configuration to each subplot
    for row in range(1, 4):
        for col in range(1, 4):
            if row == 3 and col == 3:
                continue
            fig.update_polars(angularaxis=angularaxis, radialaxis=radialaxis, row=row, col=col)

    # Update layout for better readability and legend positioning

    six_days_from_now = timedelta(days=6)
    end_date_obj = date_obj + six_days_from_now

    fig.update_layout(
        height=1100, 
        width=900, 
        title_text=f"My Spotify Listening Pattern for {date_obj.strftime('%Y-%m-%d')} - {end_date_obj.strftime('%Y-%m-%d')}",
        title_x=0.5,
        title_font_color="lightgreen",
        title_font_family='Arial',
        template='plotly_dark',
        legend=dict(
        x=0.8,
        y=0.55,
        xanchor='left',
        yanchor='bottom',
        bgcolor='DarkGray',
        bordercolor='lightgreen',
        borderwidth=2,  # Add border to the legend
        font=dict(
            size=12,
            color='white'  # Change legend font color for better contrast
        )
    ),
    )

        # Add annotation below the legend
    fig.add_annotation(
        text='Range from center represents song per hour',
        xref='paper',
        yref='paper',
        x=1.01,
        y=0.52,
        showarrow=False,
        font=dict(
            size=10,
            color='lightgreen',
            family='Arial, sans-serif'  # Change font family if desired
        ),
        bgcolor='rgba(0,0,0,0.5)',  # Semi-transparent background for better readability
        borderpad=4,  # Padding between text and border
        bordercolor='lightgreen',  # Border color
        borderwidth=2  # Border width
    )

        # Add annotation for the data source
    fig.add_annotation(
        text='Data Source: Spotify API currently_playing endpoint: https://developer.spotify.com/documentation/web-api/reference/get-the-users-currently-playing-track',
        xref='paper',
        yref='paper',
        x=0.5,
        y=-0.05,
        showarrow=False,
        font=dict(
            size=10,
            color='gray',
            family='Arial, sans-serif'  # Change font family if desired
        ),
    )

    fig.update_layout(
        title=dict(font=dict(size=22), yref='paper')
    )

    fig.update_layout(
        margin=dict(l=50, r=50, t=100, b=50),  # Adjust as needed
    )
    return fig

