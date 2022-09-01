import datetime
import numpy as np
import pandas as pd

class AggregateModel():
    """Class representing an aggregate model for multipe sampling sites"""

    def __init__(self, data, weights):
        """Class initialization"""
        # Store the inputs
        self._data = data
        self._weights = weights

        # Normalize the weights
        total_weight = sum(self._weights.values())
        for key in self._weights.keys():
            self._weights[key] = self._weights[key]/total_weight

    def str_to_datetime(self, date):
        """Function to convert a string of the form YYYY-MM-DD to a datetime object"""
        return datetime.datetime.strptime(date, "%Y-%m-%d").date()

    def get_date_list(self, start_date, end_date):
        """Function to return a list of dates based on start and end dates"""
        start_date = self.str_to_datetime(start_date)
        end_date = self.str_to_datetime(end_date)

        dates = [start_date]
        while dates[-1] <= end_date:
            dates.append(dates[-1] + datetime.timedelta(days=1))

        return dates

    def get_site_spline(self, site, gene_1, gene_2, start_date, end_date, units="gcL"):
        """Function to generate a spline curve for a given site"""
        model = self._data[site].get_spline_model(gene_1, gene_2, units)
        dates = self.get_date_list(start_date, end_date)
        values = [float(model(date)) for date in dates]
        return pd.DataFrame({"sampleDate" : dates, "value": values})

    def get_multisite_splines(self, sites, gene_1, gene_2, start_date, end_date, units="gcL"):
        """Function to generate a weighted spline curve for multiple sites"""
        splines = self.get_site_spline(sites[0], gene_1, gene_2, start_date, end_date, units)
        splines = splines.rename(columns={"value" : "value_{}".format(sites[0])})
        for site in sites[1:]:
            spline = self.get_site_spline(site, gene_1, gene_2, start_date, end_date, units)
            splines = splines.merge(spline, how="left", on="sampleDate")
            splines = splines.rename(columns={"value" : "value_{}".format(site)})

        return splines
