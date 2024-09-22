import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import html, Dash, dcc
from dash.dependencies import Input, Output
import sys
sys.path.append('/home/flambuth/fredlambuthPUNTOcom')
from app.dash_plotlys import global_stats
from app.dash_plotlys import layouts
from global_spotify.plotly_figures import track_history_line_plot
##################
load_figure_template('VAPOR')
navbar = layouts.create_navbar()

db = '/home/flambuth/fredlambuthPUNTOcom/data/global.db'

dropdown_options = [
    {'label': v, 'value': k} for k,v in global_stats.country_dict.items()
]

def Add_Dash_today_tracks_in_country(flask_app):
    dash_app = Dash(
        server=flask_app, name="country", 
        url_base_pathname="/spotify/global/",
        external_stylesheets=layouts.external_stylesheets,
        external_scripts=layouts.external_scripts
    )
    
    # NZ is the fill-in
    nz_components = global_stats.Country_Dash_Components(
        'NZ',
        db
    )
    
    # Extract the date from one of the datasets (e.g., df_top10_songs_today)
    date_today = nz_components.df_top10_songs_today['snapshot_date'].iloc[0]

    # App layout
    the_layout = html.Div([
        navbar,

        # Wrap everything below the navbar inside a dbc.Container
        dbc.Container([

            # Title Row
            dbc.Row(
                dbc.Col(
                    html.Div(
                        "Top 10 Songs Today on Spotify in 73 Countries",
                        style={
                            'font-size': '36px',
                            'font-weight': 'bold',
                            'text-align': 'center',
                            'color': '#00CC96',  # Accent color
                            'background-color': '#343a40',  # Background color already used
                            'padding': '10px',
                            'border-radius': '10px',  # Rounded corners for style
                            'border': '2px solid #238a6b'  # Same border style as others
                        }
                    ),
                    width=12
                ),
                style={'margin-bottom': '20px'}  # Adds spacing between the title and the rest of the layout
            ),

            # Content Row with dropdown and graph
            dbc.Row(
                [
                    # Left column: Date and Dropdown (centered vertically)
                    dbc.Col(
                        html.Div(
                            [
                                # Digital readout style for the date
                                html.Div(
                                    id='date-display',
                                    style={
                                        'font-size': '30px',  # Adjust for larger text
                                        'font-weight': 'bold',
                                        'text-align': 'center',
                                        'font-family': 'Courier New, monospace',  # Digital style font
                                        'height': '4em',  # Twice the height of dropdown
                                        'line-height': '4em',  # Vertically center the text
                                        'background-color': '#343a40',  # Light background to stand out
                                        'border': '2px solid black',  # Border for effect
                                        'border-radius': '5px',  # Rounded corners for style
                                    }
                                ),
                                dcc.Dropdown(
                                    id='category-dropdown',
                                    options=dropdown_options,
                                    value='US',
                                    style={'color': 'black'},
                                ),
                                dbc.Table(                    
                                    bordered=True,
                                    hover=True,
                                    responsive=True,
                                    id='top10-today-list',
                                    style={'background-color': '#343a40'}
                                ),
                            ],
                            className="d-flex flex-column justify-content-center h-100"  # Flexbox centering
                        ),
                        style={
                                'border': '2px solid #238a6b',  # Border color and width
                                'border-radius': '5px',      # Optional: rounded corners
                                'padding': '10px'            # Optional: spacing between border and content
                            },
                        width=12, lg=3
                    ),

                    # Right column: Line plot
                    dbc.Col(
                            html.Div(
                            dcc.Graph(id='line-plot'),  # Use dcc.Graph to render plotly figures
                            style={
                                'border': '2px solid #238a6b',  # Border color and width
                                'border-radius': '5px',      # Optional: rounded corners
                                'padding': '10px'            # Optional: spacing between border and content
                            }
                        ),  # Use dcc.Graph to render plotly figures
                        width=12, lg=9
                    ),
                ],
                className="h-100",  # Make the row take up the full height
                style={'min-height': '80vh'}  # Ensures the row has a minimum height for centering
            ),

            layouts.my_icon,
            dcc.Interval(id='interval-component', interval=3600000, n_intervals=0),  # 1 hour interval

        ], fluid=True)  # Makes the container fluid, adjusting its width to the screen size
    ])


    dash_app.layout = the_layout

    dash_app.title = 'Top 10 Tracks In Each Country'

    # Callback to update the table and graph based on dropdown selection
    @dash_app.callback(
            [Output('top10-today-list', 'children'),
            Output('line-plot', 'figure'),
            Output('date-display', 'children')],
            [Input('category-dropdown', 'value'),
            Input('interval-component', 'n_intervals')]
    )
    def dropdown_change_all_output(selected_country, n_intervals):
        country_components = global_stats.Country_Dash_Components(
            selected_country,
            db
        )
        
        # Fetch and filter today's data
        df_today = country_components.df_top10_songs_today 

        date_today = df_today['snapshot_date'].iloc[0]

        df_today = df_today[['daily_rank', 'name', 'primary_artist', 'daily_movement', 'weekly_movement', 'is_explicit']]
        df_today_data = country_components.df_top10_songs_data

        

        plotly_colors = [
            '#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
            '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'
        ]
        color_map = {i[0]: i[1] for i in zip(df_today['name'], plotly_colors)}
        
        # Create the table
        table_body = layouts.todays_table_div(df_today, color_map)
        
        # Create the figure
        fig1 = track_history_line_plot(
            df_today_data # [df_today_data.daily_rank < 48]
        )
        
        return table_body, fig1, f"Date: {date_today}"

    return dash_app
