class Configuration(object):
    def __init__(self, full_datafile_path, include_georegions_with_at_least_this_many_cases, logplot,
                 differential_plot, initial_data_to_show, additional_locations_to_plot_substrings):
        self.full_datafile_path = full_datafile_path
        self.include_georegions_with_at_least_this_many_cases = include_georegions_with_at_least_this_many_cases
        self.logplot = logplot
        self.differential_plot = differential_plot
        self.initial_data_to_show = initial_data_to_show
        self.additional_locations_to_plot_substrings = additional_locations_to_plot_substrings