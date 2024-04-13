from dash import Dash
from dash import dcc
from dash import html
from dash import Input, Output

from datetime import date

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
load_figure_template('VAPOR')
from app.dash_plotlys import data_sources, plotly_figures, layouts
navbar = layouts.create_navbar()
#navbar_style = {
#    'backgroundColor': 'white',  # Change this to your desired color
    # Add other styles as needed
#}
#navbar = dbc.Navbar(navbar, style=navbar_style)

def Add_Big_Dash(flask_app):
    dash_app = Dash(
        server=flask_app, name="big_dash", 
        url_base_pathname="/spotify/big_dash/",
        external_stylesheets=layouts.external_stylesheets,
        external_scripts=layouts.external_scripts,
    )
            
    
    dash_app.layout = dbc.Container([
    navbar,
    # headline row
    dbc.Row([
        dbc.Col([
            html.Label('Week(s) Ago', style={'marginRight': '10px'}),
            dcc.RadioItems(
                options=[
                    {'label': ' One', 'value': '7'},
                    {'label': ' Two', 'value': '14'},
                    {'label': ' Three', 'value': '21'}
                ],
                value='7',
                id='daterange-selection'
            ),
        ], width=12, lg=1, class_name="dash-div"),
        dbc.Col([
            html.H1(
                children='Some Spotify Stats',
                style={'textAlign': 'center'},
                className="dash-div"),
            html.Div(
                id='date-range-info',
                style={'textAlign':'center'}
            ),
            html.Small(
                "Please hit refresh after resizing (or resize after refreshing).",
                style={'display': 'block', 'textAlign': 'center', 'margin-top': '5px', 'color': 'gray'}
            ),
        ], width=12, lg=11),
    ], className="dash-div"),

    # middle row
    dbc.Row([
        dbc.Col([
            html.Div(id='top-subgenre-card', style={'padding':'10px'}),
            html.Div(id='top-master-genre-card', style={'padding':'10px'}),
            html.Div(id='top-song-card', style={'padding':'10px'}),
        ], width=12, lg=2, className="dash-div"),
        dbc.Col([
            # 1 line graph
            dbc.Row([
                dbc.Col(dcc.Graph(id='hourly-line-graph', config={'displayModeBar': False}), style={'padding': '10px'}),  
            ], className="dash-div", style={'margin-bottom': '20px', 'padding': '10px'}),

            # 2 graphs
            dbc.Row([
                dbc.Col(dcc.Graph(
                    id='known-pie-graph', 
                    config={'displayModeBar': False}), 
                    style={'padding': '10px'}, 
                    className="dash-div",
                    width=12,
                    lg=4,
                ),
                dbc.Col(dcc.Graph(
                    id='day-of-week-graph', 
                    config={'displayModeBar': False}), 
                    style={'padding': '10px'}, 
                    class_name="dash-div",
                    width=12,
                    lg=8,
                ),
            ],  style={'margin-bottom': '20px', 'padding': '10px'}),
        ], width=12, lg=10),
    ]),

    # cards row
    dbc.Row([
        dbc.Col(html.Div(id='top-5-cards'), style={'padding': '10px'}),  
    ], className="dash-div", style={'padding': '10px'}),
    layouts.my_icon,
    ], fluid=True,)


    dash_app.title = "The Past Few Weeks Or So"

    #the component_ids are referenced in the dash_app.layout. There are dcc or html objects that have 
    #the same id as the component ids in this dash callback.
    @dash_app.callback(
        Output('day-of-week-graph', 'figure'),
        Output('known-pie-graph', 'figure'),
        Output('top-5-cards', 'children'),
        Output('date-range-info', 'children'),
        Output('hourly-line-graph', 'figure'),
        Output('top-subgenre-card', 'children'),
        Output('top-master-genre-card', 'children'),
        Output('top-song-card', 'children'),
        Input('daterange-selection', 'value'),        
    )
    def update_graph(value):
        '''
        Value is the amount of days. The radio buttons in the layout give 7, 14, or 21
        5 is the amount of artists to put in the bottom row of top artists
        Fred_Big_Dash_Stuff holds attributes and methods to fill each Output in the callback
        '''
        rp_stuff = data_sources.Fred_Big_Dash_Stuff(int(value), 5)

        #the row at the bottom
        top_5_imgs_div = layouts.top_artists_imgs(rp_stuff.top_tuples)

        day_of_week_fig = plotly_figures.day_of_week_bars(rp_stuff.dts, rp_stuff.mean_song_per_day)
        known_pie_fig = plotly_figures.un_known_pie_chart(rp_stuff.known, rp_stuff.unknown)

        hourly_line_fig = plotly_figures.hourly_listening_line_chart(rp_stuff.avg_song_per_hour_Series())

        #date range in headline
        today_string = date.today().strftime("%Y-%m-%d")
        date_range_info = html.H5(f'{rp_stuff.first_day} thru {today_string}')  # New date range info

        #side card column
        top_subgenre_card = layouts.side_card(
            'Top Subgenre',
            rp_stuff.rando_subgenre_ac.img_url,
            rp_stuff.known_genre_counts()[1][0][0],
            f"https://fredlambuth.com/spotify/art_cat/genre/{rp_stuff.known_genre_counts()[1][0][0]}",
            rp_stuff.rando_subgenre_ac.art_name,
            
        )
        top_master_genre_card = layouts.side_card(
            'Top Genre',
            rp_stuff.rando_master_genre_ac.img_url,
            rp_stuff.rando_master_genre_ac.master_genre,
            f"https://fredlambuth.com/spotify/art_cat/genre/{rp_stuff.rando_master_genre_ac.master_genre}",
            rp_stuff.rando_master_genre_ac.art_name,
        )
        top_song_card = layouts.side_card(
            'Top Song',
            rp_stuff.top_rp.image[-40:],
            rp_stuff.top_rp.song_name,
            rp_stuff.top_rp.song_link,
            rp_stuff.top_rp.art_name,
        )

        return day_of_week_fig, known_pie_fig, top_5_imgs_div, date_range_info, hourly_line_fig, top_subgenre_card, top_master_genre_card, top_song_card

    return dash_app.server