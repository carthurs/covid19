# Get the data from here, then point the paths in this file to it:
#
# git clone https://github.com/CSSEGISandData/COVID-19.git

import plotly
import pathlib
import plotly.express as px
import covid_config
import covid


def create_choropleth(config):
    data = covid.get_choropleth_data(config)

    choropleth = px.choropleth(data, locations='Country/Region', color='Growth Exponent',
                               color_continuous_scale=px.colors.sequential.Plasma)

    print(data)

    choropleth.update_layout(
        title='Growth Exponent Alpha [for N(t) = N(0)exp(Alpha * t); N(t)=num cases by day t] - Previous Five Days')

    output_filename = 'choropleth_five_day_exponent'
    plotly.offline.plot(choropleth, filename='/home/chris/{}.html'.format(output_filename))
    # choropleth.show()


if __name__ == '__main__':
    data_dir = pathlib.Path(r'/home/chris/WorkData/covid19/COVID-19/csse_covid_19_data/csse_covid_19_time_series')
    file_name = r'time_series_19-covid-Confirmed.csv'
    full_datafile_path = data_dir / file_name
    include_georegions_with_at_least_this_many_cases = 100
    initial_data_to_show = ['UK', 'United Kingdom', 'Italy', 'Germany', 'Taiwan', 'Iran', 'Hubei', 'Travis County, TX',
                            'Hidalgo County, TX', 'Westchester County, NY', 'New York County, NY', 'Harris County, TX',
                            'Ireland']
    additional_locations_to_plot_substrings = ['TX', 'NY', 'Ireland']

    for logplot in [True, False]:
        for differential_plot in [True, False]:
            covid.run_plotting(covid_config.Configuration(full_datafile_path, include_georegions_with_at_least_this_many_cases, logplot,
                                       differential_plot, initial_data_to_show, additional_locations_to_plot_substrings))

    create_choropleth(covid_config.Configuration(full_datafile_path, include_georegions_with_at_least_this_many_cases, False,
                                    False, initial_data_to_show, additional_locations_to_plot_substrings))
