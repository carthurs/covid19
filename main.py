# Get the data from here, then point the paths in this file to it:
#
# git clone https://github.com/CSSEGISandData/COVID-19.git

import plotly
import pandas
import pathlib
import plotly.graph_objects as go

class Configuration(object):
    def __init__(self, full_datafile_path, include_georegions_with_at_least_this_many_cases, logplot,
                 differential_plot, initial_data_to_show):
        self.full_datafile_path = full_datafile_path
        self.include_georegions_with_at_least_this_many_cases = include_georegions_with_at_least_this_many_cases
        self.logplot = logplot
        self.differential_plot = differential_plot
        self.initial_data_to_show = initial_data_to_show

def run_plotting(config):
    plot_all = True
    if config.logplot:
        y_axis_type = 'log'
    else:
        y_axis_type = 'linear'

    data = pandas.read_csv(config.full_datafile_path)
    last_available_data_date = list(data)[-1]
    first_available_data_date = list(data)[4]

    slice_of_data_for_plotting = data.loc[:, first_available_data_date:last_available_data_date]
    # differential_data = slice_of_data_for_plotting.copy(deep=True)
    #
    # print(differential_data)
    # for row in range(differential_data.shape[0]):
    #     for column in range(differential_data.shape[1]):p


    print(list(data))
    print(list(data.loc[:, 'Province/State']))

    indices_of_included_georegions = [data_index for data_index, country_or_region in
                                      enumerate(list(data.loc[:, 'Country/Region'])) if
                                      data.loc[data_index, last_available_data_date] > config.include_georegions_with_at_least_this_many_cases]

    print("number of graphs to plot:", len(indices_of_included_georegions))

    plot_title = 'COVID-19 Cases by Country (Those with At Least {} Cases)'.format(config.include_georegions_with_at_least_this_many_cases)

    if config.logplot:
        plot_title = 'Logarithmic ' + plot_title
    else:
        plot_title = 'Linear ' + plot_title

    if config.differential_plot:
        plot_title = 'Differential ' + plot_title
    else:
        plot_title = 'Cumulative ' + plot_title


    if plot_all:
        fig = go.Figure()
        for loop_index, data_index in enumerate(indices_of_included_georegions):
            country = data.loc[:, 'Country/Region'][data_index]
            province_or_state = data.loc[:, 'Province/State'][data_index]

            if not pandas.isnull(province_or_state):
                trace_name = '{}: {}'.format(country, province_or_state)
            else:
                trace_name = country

            print('Plotting {} - Region index {} - {}'.format(loop_index, data_index, trace_name))
            if config.differential_plot:
                y_data = slice_of_data_for_plotting.loc[data_index, :].diff()
            else:
                y_data = slice_of_data_for_plotting.loc[data_index, :]

            if country in config.initial_data_to_show or province_or_state in config.initial_data_to_show:
                visibility_setting = None
            else:
                visibility_setting = 'legendonly'

            fig.add_trace(go.Scatter(y=y_data,
                                     x=list(data)[4: -1],
                                     name=trace_name,
                                     visible=visibility_setting,
                                     hoverlabel=dict(namelength=-1, bgcolor='rgba(188, 20, 26, 0.5)')))

        fig.update_layout(title=plot_title,
                          xaxis_title='Date',
                          yaxis_title='Cumulative Cases',
                          yaxis_type=y_axis_type)
        # fig.show()

        output_filename = 'covid'
        if config.logplot:
            output_filename += '_logplot'
        if config.differential_plot:
            output_filename += '_diff'
        plotly.offline.plot(fig, filename='/home/chris/{}.html'.format(output_filename))

if __name__ == '__main__':
    data_dir = pathlib.Path(r'/home/chris/WorkData/covid19/COVID-19/csse_covid_19_data/csse_covid_19_time_series')
    file_name = r'time_series_19-covid-Confirmed.csv'
    full_datafile_path = data_dir / file_name
    include_georegions_with_at_least_this_many_cases = 100
    initial_data_to_show = ['UK', 'Italy', 'Germany', 'Taiwan', 'Iran', 'USA', 'Hubei']

    for logplot in [True, False]:
        for differential_plot in [True, False]:
            run_plotting(Configuration(full_datafile_path, include_georegions_with_at_least_this_many_cases, logplot, differential_plot, initial_data_to_show))
