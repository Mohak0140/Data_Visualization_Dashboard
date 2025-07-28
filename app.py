import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime

# App initialization with Bootstrap themes for light/dark mode
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.DARKLY])
app.title = 'Data Visualization Dashboard'

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2('📊 Data Visualization Dashboard'), width=8),
        dbc.Col(
            dbc.ButtonGroup([
                dbc.Button('Light', id='light-btn', color='secondary', outline=True),
                dbc.Button('Dark', id='dark-btn', color='secondary', outline=True)
            ], size='sm'), width=4, style={'textAlign': 'right'}
        )
    ], align='center', className='my-2'),
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin': '10px 0'
                },
                multiple=False
            ),
            html.Div(id='file-info', className='text-muted'),
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='kpi-cards'),
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Span('Chart Type: '),
                    dcc.Dropdown(
                        id='chart-type',
                        options=[
                            {'label': 'Line', 'value': 'line'},
                            {'label': 'Bar', 'value': 'bar'},
                            {'label': 'Pie', 'value': 'pie'},
                            {'label': 'Heatmap', 'value': 'heatmap'}
                        ],
                        value='line',
                        clearable=False,
                        style={'width': '200px', 'display': 'inline-block'}
                    ),
                    html.Span(' | '),
                    html.Span('Date Column: '),
                    dcc.Dropdown(id='date-column', style={'width': '200px', 'display': 'inline-block'}),
                    html.Span(' | '),
                    html.Span('Value Column: '),
                    dcc.Dropdown(id='value-column', style={'width': '200px', 'display': 'inline-block'}),
                    html.Span(' | '),
                    dcc.DatePickerRange(id='date-picker', style={'display': 'inline-block'}),
                    html.Span(' | '),
                    dbc.Button('Download Data', id='download-data-btn', color='info', outline=True, size='sm', className='mx-1'),
                    dbc.Button('Download Chart', id='download-chart-btn', color='info', outline=True, size='sm', className='mx-1'),
                    dcc.Download(id='download-data'),
                    dcc.Download(id='download-chart')
                ]),
                dbc.CardBody([
                    dcc.Loading(
                        id='loading-graph',
                        type='circle',
                        children=dcc.Graph(id='main-graph', config={'displayModeBar': True, 'toImageButtonOptions': {'format': 'png'}})
                    )
                ])
            ])
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='data-table')
        ], width=12)
    ])
], fluid=True, id='main-container')

# Helper: Parse uploaded file
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return None, 'Unsupported file type.'
    except Exception as e:
        return None, f'Error: {str(e)}'
    return df, None

# Store uploaded data in dcc.Store (not shown for brevity)

# Callbacks for theme switching, file upload, KPI, chart, and download
@app.callback(
    Output('main-container', 'className'),
    [Input('light-btn', 'n_clicks'), Input('dark-btn', 'n_clicks')],
    prevent_initial_call=True
)
def switch_theme(light, dark):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ''
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if btn_id == 'dark-btn':
        app.external_stylesheets = [dbc.themes.DARKLY]
        return 'bg-dark text-light'
    else:
        app.external_stylesheets = [dbc.themes.BOOTSTRAP]
        return ''

@app.callback(
    [Output('file-info', 'children'),
     Output('date-column', 'options'),
     Output('value-column', 'options'),
     Output('date-column', 'value'),
     Output('value-column', 'value'),
     Output('kpi-cards', 'children'),
     Output('main-graph', 'figure'),
     Output('data-table', 'children')],
    [Input('upload-data', 'contents'),
     Input('chart-type', 'value'),
     Input('date-column', 'value'),
     Input('value-column', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')],
    [State('upload-data', 'filename')]
)
def update_dashboard(contents, chart_type, date_col, value_col, start_date, end_date, filename):
    if contents is None:
        return '', [], [], None, None, '', {}, ''
    df, err = parse_contents(contents, filename)
    if err:
        return err, [], [], None, None, '', {}, ''
    # Detect date and value columns
    date_options = [{'label': col, 'value': col} for col in df.select_dtypes(include=['datetime', 'object']).columns]
    value_options = [{'label': col, 'value': col} for col in df.select_dtypes(include=[np.number]).columns]
    # Try to auto-select
    date_val = date_options[0]['value'] if date_options else None
    value_val = value_options[0]['value'] if value_options else None
    # Filter by date
    if date_col and pd.api.types.is_datetime64_any_dtype(df[date_col]):
        if start_date and end_date:
            mask = (df[date_col] >= start_date) & (df[date_col] <= end_date)
            df = df.loc[mask]
    # KPIs
    kpi_cards = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5('Rows', className='card-title'),
                html.H2(f"{len(df):,}", className='card-text'),
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5('Columns', className='card-title'),
                html.H2(f"{len(df.columns):,}", className='card-text'),
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5('Missing Values', className='card-title'),
                html.H2(f"{df.isnull().sum().sum():,}", className='card-text'),
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5('Date Range', className='card-title'),
                html.H6(f"{df[date_col].min()} - {df[date_col].max()}" if date_col else 'N/A', className='card-text'),
            ])
        ]), width=3),
    ], className='my-2')
    # Chart
    fig = {}
    if chart_type == 'line' and date_col and value_col:
        fig = px.line(df, x=date_col, y=value_col, title='Line Chart')
    elif chart_type == 'bar' and date_col and value_col:
        fig = px.bar(df, x=date_col, y=value_col, title='Bar Chart')
    elif chart_type == 'pie' and value_col:
        fig = px.pie(df, names=date_col if date_col else df.columns[0], values=value_col, title='Pie Chart')
    elif chart_type == 'heatmap' and value_col:
        fig = px.density_heatmap(df, x=date_col if date_col else df.columns[0], y=value_col, title='Heatmap')
    # Tooltips
    fig.update_traces(hoverinfo='all', hovertemplate=None)
    # Data Table
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.head(100).to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
    )
    return f'Loaded: {filename}', date_options, value_options, date_val, value_val, kpi_cards, fig, table

# Download callbacks
@app.callback(
    Output('download-data', 'data'),
    Input('download-data-btn', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def download_data(n_clicks, contents, filename):
    if n_clicks and contents:
        df, _ = parse_contents(contents, filename)
        return dcc.send_data_frame(df.to_csv, filename or 'data.csv')
    return dash.no_update

@app.callback(
    Output('download-chart', 'data'),
    Input('download-chart-btn', 'n_clicks'),
    State('main-graph', 'figure'),
    prevent_initial_call=True
)
def download_chart(n_clicks, figure):
    if n_clicks and figure:
        fig = px.Figure(figure)
        img_bytes = fig.to_image(format='png')
        return dict(content=img_bytes, filename='chart.png')
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)