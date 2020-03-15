import pandas
import math
import plotly.graph_objects as go
import plotly

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

    # Custom additional province, state, country or regions to add (i.e. even if they fall below the threshold
    # case count config.include_georegions_with_at_least_this_many_cases
    adddtional_provinces_or_state_names = []
    for name_substring in config.additional_locations_to_plot_substrings:
        for province_or_state in list(data.loc[:, 'Province/State']):
            if name_substring in str(province_or_state):
                adddtional_provinces_or_state_names.append(province_or_state)
        for country_or_region in list(data.loc[:, 'Country/Region']):
            if name_substring in str(country_or_region):
                adddtional_provinces_or_state_names.append(country_or_region)

    print(adddtional_provinces_or_state_names)

    indices_of_included_georegions = [data_index for data_index, country_or_region in
                                      enumerate(list(data.loc[:, 'Country/Region'])) if
                                      data.loc[
                                          data_index, last_available_data_date] > config.include_georegions_with_at_least_this_many_cases]

    custom_additional_georegion_indices = [data_index for data_index, province_or_state in
                                           enumerate(list(data.loc[:, 'Province/State'])) if
                                           province_or_state in adddtional_provinces_or_state_names]

    custom_additional_georegion_indices.extend([data_index for data_index, province_or_state in
                                                enumerate(list(data.loc[:, 'Country/Region'])) if
                                                province_or_state in adddtional_provinces_or_state_names])

    indices_of_included_georegions.extend(custom_additional_georegion_indices)
    indices_of_included_georegions = list(set(indices_of_included_georegions))  # remove duplicates
    indices_of_included_georegions = sorted(indices_of_included_georegions, key=lambda i: data.loc[i, 'Country/Region'])

    print("number of graphs to plot:", len(indices_of_included_georegions))

    plot_title = 'COVID-19 Cases by Region (Those with {}+ Cases, & Custom Additional)'.format(
        config.include_georegions_with_at_least_this_many_cases)

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
                y_axis_title = 'New Cases'
            else:
                y_data = slice_of_data_for_plotting.loc[data_index, :]
                y_axis_title = 'Cumulative Cases'

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
                          yaxis_title=y_axis_title,
                          yaxis_type=y_axis_type)
        # fig.show()

        output_filename = 'covid'
        if config.logplot:
            output_filename += '_logplot'
        if config.differential_plot:
            output_filename += '_diff'
        plotly.offline.plot(fig, filename='/home/chris/{}.html'.format(output_filename))


def get_choropleth_data(config):
    country_codes_dataframe = pandas.read_json(r'country_names_codes_and_iso3.json')

    datasource_specific_name_replacements = pandas.read_json(r'datasource_specific_name_replacements.json')

    data = pandas.read_csv(config.full_datafile_path)
    for row_index in range(datasource_specific_name_replacements.shape[0]):
        data.replace(to_replace=datasource_specific_name_replacements.loc[row_index, 'from'],
                     value=datasource_specific_name_replacements.loc[row_index, 'to'],
                     inplace=True)

    # Drop nongeographical regions:
    regions_to_drop = ['Others', 'Cruise Ship']
    for region_to_drop in regions_to_drop:
        index_to_drop = data.loc[data['Country/Region'] == region_to_drop].index
        data.drop(index_to_drop, inplace=True)
        data = data.reset_index()

    # Add together all regions of one country
    data = data.groupby('Country/Region').sum()
    data = data.reset_index()

    for row_index in range(data.shape[0]):
        print("data:", data.loc[row_index, 'Country/Region'])
        # print(data.loc[data['Country/Region'] == 'France'])
        frame_mask_matching_country = country_codes_dataframe['name'] == data.loc[row_index, 'Country/Region']
        replacement = country_codes_dataframe.loc[frame_mask_matching_country]['alpha-3']
        data.loc[row_index, 'Country/Region'] = replacement.values[0]

    number_of_columns_added = 0
    for growth_exponent_lag in range(-10, 0):
        last_available_data_date = list(data)[growth_exponent_lag - number_of_columns_added]
        earlier_available_data_date = list(data)[-5 + growth_exponent_lag - number_of_columns_added]

        current_exponent_field = 'Growth Exponent {}'.format(last_available_data_date)

        data[current_exponent_field] = [0.0] * data.shape[0]
        number_of_columns_added += 1
        for row_index in range(data.shape[0]):
            current_cases_at_lag = data.loc[row_index, last_available_data_date]
            earlier_cases = data.loc[row_index, earlier_available_data_date]

            if current_cases_at_lag > 0 and earlier_cases > 0:
                data.loc[row_index, current_exponent_field] = (math.log(current_cases_at_lag) - math.log(earlier_cases)) / 5.0
            else:
                data.loc[row_index, current_exponent_field] = 0.0

    # Duplicate final field for the plotly choropleth
    data['Growth Exponent'] = data[current_exponent_field]

    print(data['Country/Region'])
    for i in range(data.shape[0]):
        if data.loc[i, 'Country/Region'] == 'GBR':
            print(data.loc[i, :])

    return data
