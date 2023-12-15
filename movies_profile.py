from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from app import app
from apps import dbconnect as db
from urllib.parse import urlparse, parse_qs

layout = html.Div(
    [
        html.Div(
            [
                dcc.Store(id='movieprofile_toload', storage_type='memory', data=0),
            ]
        ),

        html.H2('Movie Details'),
        html.Hr(),
        dbc.Alert(id='movieprofile_alert', is_open=False),
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Title", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text',
                                id='movieprofile_title',
                                placeholder="Title"
                            ),
                            width=5
                        )
                    ],
                    className = 'mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Genre", width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id='movieprofile_genre',
                                placeholder='Genre'
                            ),
                            width=5
                        )
                    ],
                    className = 'mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Release Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='movieprofile_releasedate',
                                placeholder='Release Date',
                                month_format='MMM Do, YY',
                            ),
                            width=5
                        )
                    ],
                    className = 'mb-3'
                ),
            ]
        ),
        html.Div(
        dbc.Row(
            [
                dbc.Label("Wish to delete?", width=1),
                dbc.Col(
                    dbc.Checklist(
                        id='movieprofile_removerecord',
                        options=[
                            {
                                'label': "Mark for Deletion",
                                'value': 1
                            }
                        ],
                        style={'fontWeight': 'bold'},
                    ),
                    width=5,
                ),
            ],
            className="mb-3",
        ),
        id='movieprofile_removerecord_div'
    ),
   
        dbc.Button(
            'Submit',
            id='movieprofile_submit',
            n_clicks=0
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    [
                        'Message here! Edit me please!'
                    ], 
                    id = 'movieprofile_feedback_message'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/movies',
                        id = 'movieprofile_btn_modal'
                    )
                )
            ],
            centered=True,
            id='movieprofile_successmodal',
            backdrop='static'
        )
    ]
)

@app.callback(
    [
        Output('movieprofile_genre', 'options'),
        Output('movieprofile_toload', 'data'),
        Output('movieprofile_removerecord_div', 'style'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def movieprof_loaddropdown(pathname, search):

    if pathname == '/movies/movies_profile':
        sql = """
            SELECT genre_name as label, genre_id as value
            FROM genres
            WHERE genre_delete_ind = False
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        genre_options = df.to_dict('records')

        parsed = urlparse(search)
        create_mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if create_mode == 'edit' else 0
        removediv_style = {'display': 'none'} if not to_load else None
    
    else:
        raise PreventUpdate
    
    return [genre_options, to_load, removediv_style]

@app.callback(
        [
            Output('movieprofile_title', 'value'),
            Output('movieprofile_genre', 'value'),
            Output('movieprofile_releasedate', 'date'),
        ],
        [
            Input('movieprofile_toload', 'modified_timestamp')
        ],
        [
            State('movieprofile_toload', 'data'),
            State('url', 'search'),
        ]
)
def movieprofile_loadprofile(timestamp, toload, search):
    if toload:

        parsed = urlparse(search)
        movieid = parse_qs(parsed.query)['id'][0]

        sql = """
            SELECT movie_name, genre_id, movie_release_date
            FROM movies
            WHERE movie_id = %s
        """
        values = [movieid]
        col = ['moviename', 'genreid', 'releasedate']

        df = db.querydatafromdatabase(sql, values, col)

        moviename = df['moviename'][0]
        genreid = int(df['genreid'][0])
        releasedate = df['releasedate'][0]

        return [moviename, genreid, releasedate]
    
    else:
        raise PreventUpdate
    

def movieprofile_populategenres(pathname):
    if pathname == '/movies/movies_profile':
        sql = """
        SELECT genre_name as label, genre_id as value
        FROM genres
        WHERE genre_delete_ind = False
        """
        values = []
        cols = ['label', 'value']

        df = db.querydatafromdatabase(sql, values, cols)

        genre_options = df.to_dict('records')
        print(genre_options)
        return [genre_options]
    else:
        raise PreventUpdate
    
@app.callback(
    [
        Output('movieprofile_alert', 'color'),
        Output('movieprofile_alert', 'children'),
        Output('movieprofile_alert', 'is_open'),
        
        Output('movieprofile_successmodal', 'is_open'),
        Output('movieprofile_feedback_message', 'children'),
        Output('movieprofile_btn_modal', 'href'),
    ],
    [
        Input('movieprofile_submit', 'n_clicks'),
        Input('movieprofile_btn_modal', 'n_clicks'),
    ],
    [
        State('movieprofile_title', 'value'),
        State('movieprofile_genre', 'value'),
        State('movieprofile_releasedate', 'date'),
        State('url', 'search'),
        State('movieprofile_removerecord', 'value'),
    ]
)
def movieprof_submitprocess(submitbtn, closebtn,
                            
                            title, genre, releasedate,
                            search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'movieprofile_submit' and submitbtn:
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not title:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the movie title.'

            elif not genre:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the movie genre.'

            elif not releasedate:
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the movie release date.'
            else:
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                print('here')
                
                if create_mode == 'add':
                    sql = """INSERT INTO movies(
                            movie_name,
                            genre_id,
                            movie_release_date,
                            movie_delete_ind
                    )
                    VALUES (%s, %s, %s, %s)
                    """
                    values = [title, genre, releasedate, False]
                    db.modifydatabase(sql, values)

                    feedbackmessage = "Movie has been saved."
                    okay_href = '/movies'
                    modal_open = True
                
                elif create_mode == 'edit':

                    parsed = urlparse(search)
                    movieid = parse_qs(parsed.query)['id'][0]

                    sqlcode = """UPDATE movies
                    SET
                        movie_name = %s,
                        genre_id = %s,
                        movie_release_date = %s,
                        movie_delete_ind = %s
                    WHERE
                        movie_id = %s
                    """
                    to_delete = bool(removerecord)
                    values = [title, genre, releasedate, to_delete, movieid]

                    db.modifydatabase(sqlcode, values)

                    feedbackmessage = "Movie has been updated."
                    okay_href = '/movies'
                    modal_open = True
                else:
                    raise PreventUpdate
            
            return [alert_color, alert_text, alert_open, modal_open, feedbackmessage, okay_href]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate
            