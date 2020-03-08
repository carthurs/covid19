# Get the data from here, then point the paths in this file to it:
#
# git clone https://github.com/CSSEGISandData/COVID-19.git

import pandas
import pathlib
import plotly.graph_objects as go

if __name__ == '__main__':
    data_dir = pathlib.Path(r'/home/chris/WorkData/covid19/COVID-19/csse_covid_19_data/csse_covid_19_time_series')
    file_name = r'time_series_19-covid-Confirmed.csv'
    include_georegions_with_at_least_this_many_cases = 100
    plot_all = True

    data = pandas.read_csv(data_dir / file_name)
    last_available_data_date = list(data)[-1]
    first_available_data_date = list(data)[4]
    slice_of_data_for_plotting = data.loc[:, first_available_data_date:last_available_data_date]

    print(list(data))
    print(list(data.loc[:, 'Province/State']))

    indices_of_included_georegions = [data_index for data_index, country_or_region in
                                      enumerate(list(data.loc[:, 'Country/Region'])) if
                                      data.loc[data_index, last_available_data_date] > include_georegions_with_at_least_this_many_cases]

    print("number of graphs to plot:", len(indices_of_included_georegions))

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
            fig.add_trace(go.Scatter(y=slice_of_data_for_plotting.loc[data_index, :],
                                     x=list(data)[4: -1],
                                     name=trace_name,
                                     hoverlabel=dict(namelength=-1, bgcolor='rgba(188, 20, 26, 0.5)')))

        fig.update_layout(title='Cumulative COVID-19 Cases by Country (Those with At Least {} Cases)'.format(include_georegions_with_at_least_this_many_cases),
                          xaxis_title='Date',
                          yaxis_title='Cumulative Cases')
        fig.show()