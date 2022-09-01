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

    def get_site_spline(self, site, gene_1, gene_2, start_date, end_date, units="gcL"):
        """Class to generate a spline curve for a given site"""
        # Get the spline model for the site
        model = self._data[site].get_spline_model(gene_1, gene_2, units)

        # Convert the date strings
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        # Generate the lists of dates
        dates = [start_date]
        while dates[-1] <= end_date:
            dates.append(dates[-1] + datetime.timedelta(days=1))

        # Generate the model values
        values = [model(date) for date in dates]

        # Return a dataframe
        return pd.DataFrame({"sampleDate" : dates, "value": values})
