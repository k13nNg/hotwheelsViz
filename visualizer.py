import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd

data = pd.read_csv("./Phase 2/processedPhase2.csv")

summary_data = (
    data.groupby(["Country Code", "Country (Normalized)", "Year"])
        .size()
        .reset_index(name="Number of Hotwheels versions produced")
)
summary_data = summary_data.sort_values("Year")

top_model_data = (
    data.groupby(["Year", "Model Name"])
        .size()
        .reset_index(name="Count")
)

years = sorted(summary_data["Year"].unique())

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Hot Wheels Production Dashboard"),

    html.Div([
        html.Button("\u25B6", id="play-button", n_clicks=0),
        html.Button("\u23F8", id="pause-button", n_clicks=0),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': y, 'value': y} for y in years],
            value=years[0],
            clearable=False,
            style={'width': '200px'}
        )
    ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px', 'marginBottom': '20px'}),

    dcc.Graph(id='choropleth', style={'height': '500px', 'width': '100%'}),

    dcc.Interval(id='interval', interval=1000, disabled=True, n_intervals=0),

    html.Div(id='top-info-container', children=[
        html.Div(id='top-models', style={
            'width': '45%', 'marginBottom': '30px', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'
        }),
        html.Div(id='top-countries', style={
            'width': '45%', 'marginBottom': '30px', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'
        }),
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'marginTop': '20px',
        'maxWidth': '900px',
        'marginLeft': 'auto',
        'marginRight': 'auto'
    }),
])

# Play/Pause buttons toggle Interval disabled property
@app.callback(
    Output('interval', 'disabled'),
    Input('play-button', 'n_clicks'),
    Input('pause-button', 'n_clicks'),
    State('interval', 'disabled'),
)
def play_pause(play_clicks, pause_clicks, is_disabled):
    ctx = dash.callback_context
    if not ctx.triggered:
        return True
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'play-button':
        return False  # Enable interval to start animation
    elif button_id == 'pause-button':
        return True   # Disable interval to pause animation
    return True

# Interval updates the dropdown's selected year
@app.callback(
    Output('year-dropdown', 'value'),
    Input('interval', 'n_intervals'),
    State('year-dropdown', 'value'),
)
def update_year(n_intervals, current_year):
    current_index = years.index(current_year)
    next_index = (current_index + 1) % len(years)
    return years[next_index]

# Update the graph and top info when dropdown value changes
@app.callback(
    Output('choropleth', 'figure'),
    Output('top-models', 'children'),
    Output('top-countries', 'children'),
    Input('year-dropdown', 'value')
)
def update_visuals(selected_year):
    filtered_map = summary_data[summary_data["Year"] == selected_year]

    fig = px.choropleth(
        filtered_map,
        locations='Country Code',
        color='Number of Hotwheels versions produced',
        hover_name='Country (Normalized)',
        projection='miller',
        color_continuous_scale='Plasma',
        title=f'Hot Wheels Cars Produced by Country ({selected_year})'
    )

    top_models = (
        top_model_data[top_model_data["Year"] == selected_year]
        .sort_values("Count", ascending=False)
        .head(5)
    )
    top_models_list = html.Ol([
        html.Li(f"{row['Model Name']}: {row['Count']} versions")
        for _, row in top_models.iterrows()
    ])
    top_models_div = html.Div([
        html.H4(f"Top 5 Models in {selected_year}"),
        top_models_list
    ])

    top_countries = (
        filtered_map.sort_values("Number of Hotwheels versions produced", ascending=False)
        .head(5)
    )
    top_countries_list = html.Ol([
        html.Li(f"{row['Country (Normalized)']}: {row['Number of Hotwheels versions produced']} versions")
        for _, row in top_countries.iterrows()
    ])
    top_countries_div = html.Div([
        html.H4(f"Top 5 Countries in {selected_year}"),
        top_countries_list
    ])

    return fig, top_models_div, top_countries_div


if __name__ == '__main__':
    app.run_server(debug=True)
