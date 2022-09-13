"""Module for performing modelling on data represented by SiteData objects.
"""

import datetime
import numpy as np
import pandas as pd

class AggregateModel():
    """Class representing an aggregate model for multipe sampling sites.

    Parameters
    ----------
    data : dict
        The site data to be modelled. The keys of the dict are the names of the
        sampling sites used in the ODM database and the values are SiteData
        objects representing that site.
    weights : dict
        The weighting factors for each sampling site (often the population).
        The keys of the dict are the names of the sampling sites used in the ODM
        database and the values are the weights.
    """

    def __init__(self, data, weights):
        """Class initialization"""
        self._data = data
        self._weights = weights

    def str_to_datetime(self, date):
        """Convert a string of the form YYYY-MM-DD to a datetime object.

        Parameters
        ----------
        date : str
            Date in the format YYYY-MM-DD.


        Returns
        -------
        datetime.date
            Date as a datetime.date object.
        """
        return datetime.datetime.strptime(date, "%Y-%m-%d").date()

    def get_date_list(self, start_date, end_date):
        """Get a list of dates (spaced daily) based on start and end dates.

        The list will include the start and end dates.

        Parameters
        ----------
        start_date : str
            Start date of date list.
        end_date : str
            End date of date list.


        Returns
        -------
        list of datetime.date
            A list of dates, evenly spaced at 1-day intervals.
        """
        start_date = self.str_to_datetime(start_date)
        end_date = self.str_to_datetime(end_date)

        dates = [start_date]
        while dates[-1] <= end_date:
            dates.append(dates[-1] + datetime.timedelta(days=1))

        return dates

    def get_site_spline(self, site, gene_1, gene_2, start_date, end_date, units="gcL"):
        """Get a spline curve for a given site.

        For dates that are beyond the range of the dataset, a value of NaN
        is inserted.

        Parameters
        ----------
        site : str
            Site name.
        gene_1 : str
            Gene target for quantification (naming as per ODM format).
        gene_2 : str
            Gene used for normalization of gene_1 (naming as per ODM format).
        start_date : str
            Start date of model.
        end_date : str
            End date of model.
        units : str, optional
            Units for quantification of gene_1 and gene_2.

        Returns
        -------
        pandas.DataFrame
            Time series of the modelled site data. The dates are in the column
            labelled "sampleDate" and the values are in the column labelled
            "value".
        """
        # Get the model for all dates requested even if out of range
        model = self._data[site].get_spline_model(gene_1, gene_2, units)
        dates = self.get_date_list(start_date, end_date)
        values = [float(model(date)) for date in dates]

        # Get the date limits for the actual data
        min_date = self._data[site].sample_data["sampleDate"].min()
        max_date = self._data[site].sample_data["sampleDate"].max()

        # Fill out of range dates with None
        for i, date in enumerate(dates):
            if date < min_date:
                values[i] = None
            if date > max_date:
                values[i] = None

        # Return the data
        return pd.DataFrame({"sampleDate" : dates, "value": values})

    def get_multisite_splines(self, sites, gene_1, gene_2, start_date, end_date, units="gcL"):
        """Get spline curves for multiple sites.

        For dates that are beyond the range of the dataset, a value of NaN
        is inserted.

        Parameters
        ----------
        sites : list of str
            Site names.
        gene_1 : str
            Gene target for quantification (naming as per ODM format).
        gene_2 : str
            Gene used for normalization of gene_1 (naming as per ODM format).
        start_date : str
            Start date of model.
        end_date : str
            End date of model.
        units : str, optional
            Units for quantification of gene_1 and gene_2.

        Returns
        -------
        pandas.DataFrame
            Time series of the modelled site data. The dates are in the column
            labelled "sampleDate" and the values are in the columns labelled
            "value_X", where X represents the site name.
        """
        splines = self.get_site_spline(sites[0], gene_1, gene_2, start_date, end_date, units)
        splines = splines.rename(columns={"value" : "value_{}".format(sites[0])})
        for site in sites[1:]:
            spline = self.get_site_spline(site, gene_1, gene_2, start_date, end_date, units)
            splines = splines.merge(spline, how="left", on="sampleDate")
            splines = splines.rename(columns={"value" : "value_{}".format(site)})
        return splines

    def get_aggregate_model(self, sites, gene_1, gene_2, start_date, end_date, units="gcL"):
        """Get a weighted aggregate model for multiple sites.

        Parameters
        ----------
        sites : list of str
            Site names.
        gene_1 : str
            Gene target for quantification (naming as per ODM format).
        gene_2 : str
            Gene used for normalization of gene_1 (naming as per ODM format).
        start_date : str
            Start date of model.
        end_date : str
            End date of model.
        units : str, optional
            Units for quantification of gene_1 and gene_2.

        Returns
        -------
        pandas.DataFrame
            Time series of the modelled site data. The dates are in the column
            labelled "sampleDate" and the values, representing a weighted
            average of the site models, are in the column labelled "value".
        """
        splines = self.get_multisite_splines(sites, gene_1, gene_2, start_date, end_date, units)
        spline_columns = []
        weight_columns = []
        for site in sites:
            spline_columns.append("value_{}".format(site))
            weight_columns.append("weight_{}".format(site))
            splines[spline_columns[-1]] = splines[spline_columns[-1]]*self._weights[site]
            # Set the weights, where the weight is zero if the value is NaN
            splines[weight_columns[-1]] = self._weights[site]
            splines.loc[splines[spline_columns[-1]].isna(), weight_columns[-1]] = 0.0
        splines["value"] = splines[spline_columns].sum(axis=1)/splines[weight_columns].sum(axis=1)
        return splines[["sampleDate", "value"]]
