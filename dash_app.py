import math
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
import os
import covid
import covid_config
import pathlib

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

data_dir = pathlib.Path(r'/home/chris/WorkData/covid19/COVID-19/csse_covid_19_data/csse_covid_19_time_series')
file_name = r'time_series_19-covid-Confirmed.csv'
full_datafile_path = data_dir / file_name
include_georegions_with_at_least_this_many_cases = 100
initial_data_to_show = ['UK', 'United Kingdom', 'Italy', 'Germany', 'Taiwan', 'Iran', 'Hubei', 'Travis County, TX',
                        'Hidalgo County, TX', 'Westchester County, NY', 'New York County, NY', 'Harris County, TX',
                        'Ireland']
additional_locations_to_plot_substrings = ['TX', 'NY', 'Ireland']

configuration = covid_config.Configuration(full_datafile_path, include_georegions_with_at_least_this_many_cases, False,
                                    False, initial_data_to_show, additional_locations_to_plot_substrings)

data_frame = covid.get_choropleth_data(configuration)

app = dash.Dash('app', server=server)

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

app.layout = html.Div([
    html.H1('COVID-19 Growth Exponents over Time [Alpha, where N(t) = N(0)exp(Alpha * t); N(t)=num cases by day t] - Five day trailing'),
    dcc.Slider(
        marks={v+1: list(data_frame)[v-1] for v in range(-10, 0)},
        id='my-slider',
        min=-9,
        max=0,
        step=1,
        value=0
    ),
    html.Div([
        dcc.Graph(id='my-graph', style={'width': '100%', 'height': '800px'})
        ])
], className="container")


def myfunc(x):
    if x > 0:
        return math.log(x)
    else:
        return 0


@app.callback(Output('my-graph', 'figure'),
              [Input('my-slider', 'value')])
def update_graph(slider_value):
    growth_rate_index = data_frame.shape[1] - 2 + slider_value
    print(data_frame, "val:", growth_rate_index, slider_value, len(list(data_frame)))

    colour_data = data_frame.loc[:, list(data_frame)[growth_rate_index]]

    country_or_region_data = data_frame.loc[:, 'Country/Region']

    return {
        'data': [{
            'locations': country_or_region_data,
            'z': colour_data,
            'zmin': 0,
            'zmax': 0.4,
            'line': {
                'width': 3,
                'shape': 'spline'
            },
            'type': 'choropleth'
        }],
        'layout': {
            'margin': {
                'l': 30,
                'r': 20,
                'b': 30,
                't': 20
            }
        },
    }


if __name__ == '__main__':
    app.run_server()
