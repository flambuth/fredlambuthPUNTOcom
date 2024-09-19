import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import html, Dash, dcc
import sys
sys.path.append('/home/flambuth/fredlambuthPUNTOcom')
from app.dash_plotlys import global_stats
from app.dash_plotlys import layouts
from global_spotify.plotly_figures import track_history_line_plot
##################
load_figure_template('VAPOR')
navbar = layouts.create_navbar()

#################
# data
db = '/home/flambuth/fredlambuthPUNTOcom/data/global_TEST.db'
country = 'NZ'
stats_obj = global_stats.Country_Dash_Components(
            country,
            db
            )
df_today = stats_obj.df_top10_songs_today 
df_today = df_today[['daily_rank','name','primary_artist','daily_movement','weekly_movement','is_explicit']]

df_today_data = stats_obj.df_top10_songs_data

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
# layout components
line_plot_fig = track_history_line_plot(df_today_data)


table_rows = df_today.apply(
    lambda row: html.Tr(
        [
            html.Td(f"{row['daily_rank']}.", style={'font-weight': 'bold'}),
            html.Td(row['name'], style={'font-weight': 'bold', 'color': color_map[row['name']]}),
            html.Td(row['primary_artist']),
            html.Td(f"{row['daily_movement']}" if row['daily_movement'] != 0 else "", 
                     style={'color': 'green' if row['daily_movement'] > 0 else 'red' if row['daily_movement'] < 0 else 'black'}),
            html.Td(
                html.I(className="fas fa-exclamation-triangle", style={'color': 'yellow'})
                if row['is_explicit'] else ""
            ),
        ]
    ), 
    axis=1
).tolist()

table_body = html.Tbody(table_rows)

# Define the table without an extra level of list nesting
table = dbc.Table(
    [table_body],  # Make sure the children is a flat list with table_header and table_body
    bordered=True,
    hover=True,
    responsive=True,
    style={'background-color': '#343a40'}
)

# Update the layout

temp_layout = html.Div(
    [
        navbar,
        dbc.Row(
            [
                # Table in 3/12 of the row
                dbc.Col(
                    table,
                    width=3),
                
                # Line plot in 9/12 of the row
                dbc.Col(
                    dcc.Graph(figure=line_plot_fig),  # Use dcc.Graph to render plotly figures
                    width=9
                ),
            ]
        ),
        layouts.my_icon
    ]
)


###########################
# app
app = Dash(
    f'once_upon_a_time_in_{stats_obj.country}',
    external_stylesheets=layouts.external_stylesheets,
    external_scripts=layouts.external_scripts
    )

app.layout = temp_layout

if __name__ == '__main__':
    
    app.run(debug=True)