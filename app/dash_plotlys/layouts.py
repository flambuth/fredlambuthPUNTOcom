import dash_bootstrap_components as dbc
from dash import html
#from flask import url_for
from datetime import datetime

this_year = datetime.today().year
image_url = "/static/favicon.ico"
image_alt = "Howdy!"

colors = {
    'background': '#111111',
    'text': '#238a6b'
}
external_stylesheets=[
    dbc.themes.VAPOR, 
    '/static/css/style.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css']
external_scripts=[
    'https://code.jquery.com/jquery-3.5.1.slim.min.js',
    'https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.3/dist/umd/popper.min.js',
    'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js']

my_icon = html.Header([
            html.Link(
                rel='icon',
                href=image_url, 
                type='image/x-icon'
            ),
        ])



def create_navbar():
    navbar = html.Nav(className="navbar navbar-expand-lg navbar-dark bg-dark", children=[
        html.A(className="navbar-brand", href="https://fredlambuth.com", children=[
            html.Img(src=image_url, height="30px", title=image_alt),
            html.Span("fredlambuth", className="pill-text"),  # Apply custom class to this part
            html.Span(".com", className="nav-link-text")      # Keep the default class for this part
        ]),
        html.Button(className="navbar-toggler", type="button", **{'data-toggle': "collapse", 'data-target': "#navbarNav", 'aria-controls': "navbarNav", 'aria-expanded': "false", 'aria-label': "Toggle navigation"}, children=[
            html.Span(className="navbar-toggler-icon")
        ]),
        html.Div(id="navbarNav", className="collapse navbar-collapse justify-content-end", children=[
            dbc.Nav(className="navbar-nav", children=[
                dbc.NavItem(html.A([
                    html.I(className="fab fa-spotify"),
                    html.Span(" Spotify", className="nav-link-text"),
                ], className="nav-link", href="/spotify")),
                dbc.NavItem(html.A([
                    html.I(className="fas fa-book-open"),
                    html.Span(" Blog", className="nav-link-text"),
                ], className="nav-link", href="/blog")),
                dbc.NavItem(html.A([
                    html.I(className="fas fa-bullhorn"),
                    html.Span(" Contact", className="nav-link-text"),
                ], className="nav-link", href="/contact")),
                dbc.NavItem(html.A([
                    html.I(className="fas fa-user"),
                    html.Span(" Account", className="nav-link-text"),
                ], className="nav-link", href="/account")),
                # Add more links as needed
            ]),
        ])
    ])

    return navbar


########################
#Monthly view
def artist_card_row(art_cats):
    '''
    List comprehension of the input art_cats. Creates a row with the layout.artist_card, for each
    art_cat from the parameter.
    '''
    colors = ['blue', 'red', 'green', 'gold', 'cyan']

    totem_div = html.Div(children=[
        dbc.Row(
            justify="center",  # Center the contents horizontally
            children=[
                dbc.Col(
                    [
                        artist_card(artist),
                    ],
                    xs=12,
                    md=5,
                    lg=2,
                    style={
                        'border': f'2px solid {colors[i % len(colors)]}',  # Border style with color
                        'border-radius': '10px',  # Optional: Add rounded corners
                        'padding': '10px',
                        'height': '60%',
                    }
                )  
                for i, artist in enumerate(art_cats)
            ]
        )
    ])
    return totem_div


def artist_card(art_cat):
    '''
    Returns a DBC.card object. Accepts the art_cat models as input
    '''
    this_card = dbc.Card([
        dbc.CardImg(
            src=f"https://i.scdn.co/image/{art_cat.img_url_mid}",
            top=True,
            style={'opacity': 0.3, 'width': '100%', 'height':'80%',},  # Set width to 100%
        ),
        dbc.CardImgOverlay(
            dbc.CardBody(
                [
                    html.H4(
                        html.A(
                            children=art_cat.art_name,
                            href=f"https://fredlambuth.com/spotify/art_cat/artist/{art_cat.art_id}"
                        ),
                        className="card-title",
                    ),
                    html.P(
                        art_cat.genre,
                        className="card-text",
                    ),
                    dbc.Button(
                        art_cat.master_genre,
                        color='primary',
                        href='https://fredlambuth.com/spotify/art_cat/genre/'+art_cat.master_genre),
                ]
            ),
        ),
    ])
    return this_card

####################################
##########################
#the big dash figures
def side_card(headline, img_url, title, url_link, art_name):
    """
    One of the three HTML cards used in the side of the weekly_big_dash app
    """
    card_content = [
        html.H4(headline, className="card-headline", style={'color':'palegreen'}),
        html.Hr(),
        dbc.Row(
            #justify="center",
            children=[
                dbc.Col(
                    dbc.CardImg(
                        src=f'https://i.scdn.co/image/{img_url}',
                        top=True,
                        title=art_name,
                        style={'opacity': 0.9, 'width': '99%', 'height': '99%', 'max-height': '150px', 'max-width':'320px',}  
                    )
                )
            ]
        ),
        dbc.CardImgOverlay(
            dbc.CardBody([
                html.A(title, href=url_link)
            ])
        )
    ]
    return dbc.Card(card_content, style={'backgroundColor':colors['background']})



def multiple_side_cards(cards):
    """
    Generate a column with multiple cards.
    
    Args:
    - cards (list): List of cards to be included in the column.
    
    Returns:
    - dbc.Col: Column containing the specified cards.
    """
    column_content = [dbc.Row(dbc.Col(card, width=12)) for card in cards]
    return dbc.Col(column_content, width=2, className="dash-div")


#############
#bottom row of weekly big_dash
def rp_artists_card(truple):
    '''
    the ones at the bottom of the dash
    '''
    this_card = html.A(
        dbc.Card(
            style={'background-color': colors['background']},
            children=[
                dbc.CardImg(
                    src=truple[3],
                    top=True,
                    style={'opacity': 0.9, 'width': '99%', 'height':'99%','max-height': '150px'},
                ),
                html.H4(truple[0]),
                dbc.CardImgOverlay(
                    dbc.CardBody(
                        [
                            html.P(
                                truple[1],
                                style={'font-size': '14px', 'color':'wheat','text-shadow': '0px 2px 25px black'},
                            ),
                        ]
                    ),
                ),
            ]
        ),
        href=truple[4],
        target="_blank",
        title="Link to song from artist in Spotify",
    )
    return this_card


def top_artists_imgs(truples):
    '''
    Iterates through rp_artists_cards. Adds a headline.
    '''
    totem_div = html.Div(children=[
        html.H4('Top Artists'),
        dbc.Row([
            dbc.Col([
                rp_artists_card(truple),
            ])  
            for truple in truples
        ][::-1])
    ])
    return totem_div



#############################
#Artist History
def notable_tracks_html(notable_tracks):
    '''
    TBA
    '''
    if len(notable_tracks) == 0:
        return (None, None)
    track_hits_heading = html.H5(children='Notable Tracks', style={'textAlign':'left', 'font-weight':'bold','color':colors['text']})
    list_group = dbc.ListGroup(
    [html.Div(children=song, style={'textAlign':'left'}) for song in notable_tracks]
)
    return (track_hits_heading, list_group)

def longest_artist_streak_html(longest_streak):
    if longest_streak == None:
        return (None, None)

    html_line = html.Div(children=f'{longest_streak[1]} days beginning on {longest_streak[0]}', style={'padding-bottom':'5px'})

    heading = html.H5(children='Longest Streak', style={'textAlign':'left', 'font-weight':'bold','color':colors['text']})

    return (heading, html_line)

def artist_history_stats_html(art_cat_data):
    #will display all genres if available, or jsut 1 or 2
    genres = [art_cat_data.art_cat.genre, art_cat_data.art_cat.genre2, art_cat_data.art_cat.genre3]
    genre_divs = []
    #iterates the genre attributes to make a list of up to 3
    for genre in genres:
        if genre:
            genre_divs.append(html.Div(children=genre, style={'margin-right': '20px'}))

    totem_div = html.Div(children=[
        dbc.Container(
            fluid=True,
            style={'maxWidth':'800px'},
            children=[
            dbc.Row([
                html.H1(children=art_cat_data.art_cat.art_name,
                        style={'color':'green', 'textAlign':'center'}),
                html.Div(children=genre_divs, style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-top':'10px', 'margin-bottom':'10px'}),
            ]),
            dbc.Row([
                dbc.Col([                        
                    html.H5(children='First Appearance', style={'textAlign':'left', 'font-weight':'bold', 'color':colors['text']}),
                    html.Div(children=art_cat_data.first_and_last_appearance()[0], style={'padding-bottom':'5px'}),
                    longest_artist_streak_html(art_cat_data.longest_streak)[0],
                    longest_artist_streak_html(art_cat_data.longest_streak)[1],
                    html.H5(children='Latest Appearance', style={'textAlign':'left', 'font-weight':'bold', 'color':colors['text']}),
                    art_cat_data.first_and_last_appearance()[1],
                ]),
                dbc.Col(
                    html.Img(src=f"https://i.scdn.co/image/{art_cat_data.art_cat.img_url}", style={'width':260,'border': f'2px solid {colors["text"]}', 'border-radius': '10px'})
                )
            ])
        ])
    ])
    return totem_div

#######################

def todays_table_div(today_top10_df, color_map):
    '''
    Creates the dash.html div that holds the top10 tracks for today
    '''
    # Apply function to create table rows with dotted borders and centered text
    table_rows = today_top10_df.apply(
        lambda row: html.Tr(
            [
                html.Td(f"{row['daily_rank']}.", style={'font-weight': 'bold', 'border': '1px dotted gray', 'text-align': 'center', 'vertical-align': 'middle'}),
                html.Td(row['name'], style={'font-weight': 'bold', 'color': color_map[row['name']], 'border': '1px dotted gray', 'text-align': 'center', 'vertical-align': 'middle'}),
                html.Td(row['primary_artist'], style={'border': '1px dotted gray', 'text-align': 'center', 'vertical-align': 'middle'}),
                html.Td(
                    f"{row['daily_movement']}" if row['daily_movement'] != 0 else "", 
                    style={'color': 'green' if row['daily_movement'] > 0 else 'red' if row['daily_movement'] < 0 else 'black',
                           'border': '1px dotted gray', 'text-align': 'center', 'vertical-align': 'middle', 'width': '40px'}  # Adjusted width
                ),
                html.Td(
                    html.I(className="fas fa-exclamation-triangle", style={'color': 'yellow'}) if row['is_explicit'] else "",
                    style={'border': '1px dotted gray', 'text-align': 'center', 'vertical-align': 'middle', 'width': '50px'}
                ),
            ],
            style={'border': '1px dotted gray'}
        ), 
        axis=1
    ).tolist()

    # Return the table body with the dotted border and centered text
    table_body = html.Tbody(table_rows)

    # Return the full table (with header) as children, with tiny header text and narrow columns
    return [
        html.Thead(
            html.Tr(
                [
                    html.Th("Position", style={'font-weight': 'bold', 'font-size': '12px', 'text-align': 'center'}),
                    html.Th("Name", style={'font-weight': 'bold', 'font-size': '12px', 'text-align': 'center'}),
                    html.Th("Artist", style={'font-weight': 'bold', 'font-size': '12px', 'text-align': 'center'}),
                    html.Th("▲▼", style={'font-weight': 'bold', 'font-size': '12px', 'text-align': 'center', 'width': '40px'}),  # Narrow column
                    html.Th("Explicit", style={'font-weight': 'bold', 'font-size': '12px', 'text-align': 'center', 'width': '50px'}),  # Narrow column
                ]
            ),
        ),
        table_body
    ]
