import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app
from apps import dbconnect as db

layout = html.Div(
    [
        html.H2('Movies'),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Records')
                    ]
                ),
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    'Add Movie', color = 'secondary',
                                    href='/movies/movies_profile?mode=add'
                                ),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Movies'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Title", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='moviehome_titlefilter',
                                                        placeholder='Movie Title'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                            className = 'mb-3'
                                        )
                                    )
                                ),
                                html.Div(
                                    "Table with movies will go here.",
                                    id='moviehome_movielist'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
    )
@app.callback(
        [
            Output('moviehome_movielist', 'children')
        ],
        [
            Input('url', 'pathname'),
            Input('moviehome_titlefilter', 'value'),
        ]
)
def moviehome_loadmovielist(pathname, searchterm):
    if pathname == '/movies':
        sql = """ SELECT movie_name, genre_name, movie_id
            FROM movies m
                INNER JOIN genres g ON m.genre_id = g.genre_id
            WHERE
                NOT movie_delete_ind
        """
        values = []
        cols = ['Movie Title', 'Genre', "ID"]

        if searchterm:
            sql += " AND movie_name ILIKE %s"
            values += [f"%{searchterm}%"]

        df = db.querydatafromdatabase(sql, values, cols)

        if df.shape:

            buttons = []
            for movie_id in df['ID']:
                buttons += [
                    html.Div(
                        dbc.Button('Edit',
href=f'movies/movies_profile?mode=edit&id={movie_id}',
                                    size='sm', color='warning'),
                        style={'text-align': 'center'}            
                    )
                ]
            df['Action'] = buttons

            df = df[['Movie Title', 'Genre', "Action"]]

            table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
                    hover=True, size='sm')
            return [table]
        else:
            return ["No records to display"]
    else:
        raise PreventUpdate
