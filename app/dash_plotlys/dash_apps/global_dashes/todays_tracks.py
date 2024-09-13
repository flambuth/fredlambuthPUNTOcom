import dash_bootstrap_components as dbc
from dash import html, Dash, dash_table, dcc

import sys
sys.path.append('/home/flambuth/fredlambuthPUNTOcom')
from app.dash_plotlys import global_stats
from app.dash_plotlys.layouts import external_stylesheets
from global_spotify.plotly_figures import track_history_line_plot

#################
# data
db = '/home/flambuth/fredlambuthPUNTOcom/data/global_TEST.db'
country = 'NZ'
df_today = global_stats.Country_Dash_Components(
            country,
            db
            ).df_top10_songs_today 
df_today = df_today[['daily_rank','name','primary_artist','daily_movement','weekly_movement','is_explicit']]

df_today_data = global_stats.Country_Dash_Components(
            country,
            db
            ).df_top10_songs_data

plotly_colors = [
    '#636EFA',
    '#EF553B',
    '#00CC96',
    '#AB63FA',
    '#FFA15A',
    '#19D3F3',
    '#FF6692',
    '#B6E880',
    '#FF97FF',
    '#FECB52'
]
color_map = {i[0]:i[1] for i in zip(df_today.name,plotly_colors)}
###############
# layout
line_plot_fig = track_history_line_plot(df_today_data)


list_items = df_today.apply(
    lambda row: dbc.ListGroupItem(
        [
            html.Span(f"{row['daily_rank']}. ", style={'font-weight': 'bold'}),
            html.Span(row['name'], style={'font-weight': 'bold', 'color': color_map[row['name']]}),  # Apply color here
            html.Span(f" - {row['primary_artist']}"),
        ],
        style={'background-color': '#343a40'}  # Optional: Dark background for all items
    ), 
    axis=1
).tolist()


listgroup = [dbc.ListGroupItem(
    "Top 10 Today", 
    style={'font-weight': 'bold', 'color': 'teal', 'background-color': '#343a40'})
    ] + list_items

temp_layout = html.Div(
    [
        dbc.Row(
            [
                # Table in 3/12 of the row
                dbc.Col(
                    dbc.ListGroup(
                        id='top10-today-list',
                        children=[dbc.ListGroupItem("Top 10 Songs Today", style={'font-weight': 'bold', 'color': 'teal',})]+listgroup,
                    ), 
                    width=3),
                
                # Line plot in 9/12 of the row
                dbc.Col(
                    dcc.Graph(figure=line_plot_fig),  # Use dcc.Graph to render plotly figures
                    width=9
                ),
            ]
        ),
    ]
)


###########################
# app
app = Dash(__name__,external_stylesheets=external_stylesheets)

app.layout = temp_layout

if __name__ == '__main__':
    
    app.run(debug=True)