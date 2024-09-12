from dash import Dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import app.dash_plotlys.global_stats as global_stats
from app.dash_plotlys.layouts import create_navbar, my_icon, external_scripts, external_stylesheets
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
load_figure_template('VAPOR')
navbar = create_navbar()

countries = list(global_stats.country_codes.values())
dropdown_options = [{'label': category, 'value': category} for category in countries]

def Add_Dash_global_view_lite(flask_app):
    dash_app = Dash(
        server=flask_app, name="global", 
        url_base_pathname="/spotify/global/",
        external_stylesheets=external_stylesheets,
        external_scripts=external_scripts)
# App layout
    dash_app.layout = html.Div(style={'height': '100vh'}, children=[
        navbar,
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='category-dropdown',
                        options=dropdown_options,
                        value=countries[4],
                        style={'color': 'black'},
                    ),
                    dcc.Graph(id='hbar-plot', config={'displayModeBar': False}),
                    dbc.ListGroup(
                        id='top10-today-list',
                        children=[dbc.ListGroupItem("Top 10 Songs Today", style={'font-weight': 'bold', 'color': 'teal',})],  # Title
                        #style={'height': '400px', 'overflowY': 'auto',}
                    ),
                ], width=12, lg=4,),
                dbc.Col([
                    dcc.Graph(id='line-plot', config={'displayModeBar': False}),
                ], style={'border':'2px solid teal'}, width=12, lg=8,),
        ]),
    ]),
    my_icon
    ])

    dash_app.title = 'Spotify Data Around The World in 90 Days'


# Callback to update the graph based on dropdown selection
    @dash_app.callback(
        Output('top10-today-list', 'children'),
        Output('hbar-plot', 'figure'),
        Output('line-plot', 'figure'),
        [Input('category-dropdown', 'value')]
    )
    def dropdown_change_all_output(selected_country):
        #big_df = global_stats.cleaned_df()
        blob = global_stats.Country_Dash_Components(selected_country)
        
        top10_today_data = blob.df_top10_songs_today
        
        list_items = top10_today_data.apply(lambda row: dbc.ListGroupItem([
            html.Span(f"{row['daily_rank']}. ", style={'font-weight': 'bold'}),
            html.Span(row['name'], style={'font-weight': 'bold'}),
            html.Span(f" - {row['artists']}")
        ]), axis=1).tolist()


        fig1 = blob.fig_top10_artists
        fig2 = blob.fig_top10_song
        listgroup = [dbc.ListGroupItem("Top 10 Today", style={'font-weight': 'bold', 'color': 'teal', 'background-color': '#343a40'})] + list_items
        return listgroup, fig1, fig2

    return dash_app