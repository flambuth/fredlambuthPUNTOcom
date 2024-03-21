from dash import Dash
from dash import dcc
from dash import html
from dash import Input, Output
from datetime import date, timedelta

#from dash import url
from app.dash_plotlys.layouts import create_navbar, my_icon, artist_card_row, external_scripts, external_stylesheets

import dash_bootstrap_components as dbc

from app.dash_plotlys import data_sources, plotly_figures

from dash_bootstrap_templates import load_figure_template
load_figure_template('VAPOR')

navbar = create_navbar()

def Add_Dash_year_month(flask_app):
    dash_app = Dash(
        server=flask_app, name="art_cat", 
        url_base_pathname="/spotify/monthly/",
        external_stylesheets=external_stylesheets,
        external_scripts=external_scripts,
        )
    dash_app.layout = html.Div(
        style={'backgroundColor': 'black'},
        children=[
            dcc.Location(id='url', refresh=False),
            navbar,
            dcc.DatePickerSingle(
                id='date_picker',
                placeholder='Choose Month',
                initial_visible_month='2023-12-01',
                style={
                    'margin': 'auto', 
                    'display': 'block', 
                    'textAlign': 'center',
                    'width': '22%',},
            ),
            
            dcc.Graph(
                id="month_line_chart",
                config={'displayModeBar': False},
            ),
            html.Div(id='selected_month_info'),
            my_icon
        ]
    )
    dash_app.title = 'My Top 5 Artists of The Month'

    ########################################################
    ##callbacks
    @dash_app.callback(
        Output(component_id='url', component_property='pathname'),
        #Output(component_id='selected_month_info', component_property='children'),
        Input('date_picker', 'date'), prevent_initial_call=True,
        
    )
    def update_url(selected_date):
        selected_year, selected_month, _ = selected_date.split('-')
        return f"/spotify/monthly/{selected_year}/{selected_month}"

    #the component_ids are referenced in the dash_app.layout. There are dcc or html objects that have 
    #the same id as the component ids in this dash callback.
    @dash_app.callback(
        Output(component_id='month_line_chart', component_property='figure'),
        Output(component_id='selected_month_info', component_property='children'),
        #Input(component_id='my_input', component_property='value'),
        Input('url', 'pathname'),  # This input captures the URL pathname
    )
    def update_graph(pathname):
        '''
        This does all the HTML work that isn't done by the Dashboard itself imported from Chartsie
        '''
        #art_cat_data = char.art_cat_entry(input_art_name)[0]
        input_month = pathname.split('/')[-1]
        input_year = pathname.split('/')[-2]

        if input_month is None:
            input_month = date.today().month - 1
            input_year = date.today().year

        dash_app.layout['date_picker'].initial_visible_month = f'{input_year}-{input_month}-01'

        month_arts = data_sources.Chart_Year_Month_Stats(input_year,input_month)
        x,y,z=month_arts.line_chart_components()
        fig = plotly_figures.year_month_line_chart(x,y,z)
        totem_div = artist_card_row(month_arts.top_5_artcats)

        #if fig is None:
        #    placeholder_text = "No data available"
        #    return dcc.Markdown(f"**{placeholder_text}**")
        #else:
        return fig, totem_div
        #return fig, totem_div
    return dash_app