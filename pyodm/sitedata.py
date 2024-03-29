import pandas as pd
import numpy as np

from scipy.interpolate import LSQUnivariateSpline

def delta_days(date_2, date_1):
    """Function to return the number of days between two dates"""
    delta = date_2 - date_1
    return delta.days

def spline_model(date, start_date, func):
    """Function implementing a spline model func(x) with the date represented as a float"""
    day = delta_days(date, start_date)
    return func(day)

class SiteData():
    """Class used to store and access data for a named sampling site"""

    def __init__(self, data, site_id):
        """Class initialization"""

        # Store reference to the ODM data
        self._data = data

        # Store the site_id
        self._site_id = site_id

        # Read relevant information about the site
        site_data = self._data.site
        row = site_data.loc[site_data["siteID"] == site_id]
        self.name = row["name"].values[0]
        self.description = row["description"].values[0]
        self.type = row["type"].values[0]
        self.health_region = row["healthRegion"].values[0]
        self.health_department = row["publicHealthDepartment"].values[0]
        self.latitude = row["geoLat"].values[0]
        self.longitude = row["geoLong"].values[0]

        # Extract the sample data associated with this site
        sample_data = self._data.sample
        self.sample_data = sample_data.loc[sample_data["siteID"] == self._site_id].copy()

        # Create a field for "sampleTime" which is either the grab sample time or the end time of a composite
        self.sample_data["sampleTime"] = self.sample_data["dateTimeEnd"].fillna(self.sample_data["dateTime"])

        # Create a field for "sampleDate" which is "sampleTime" without the time
        self.sample_data["sampleDate"] = pd.to_datetime(self.sample_data["sampleTime"]).dt.date

        # Extract the measurement data associated with this site
        measure_data = self._data.ww_measure
        self.measure_data = measure_data.loc[measure_data["sampleID"].isin(self.sample_data["sampleID"])].copy()

        # Add a column in the measurement data for the sampleDate
        self.measure_data = self.measure_data.merge(self.sample_data[["sampleID", "sampleDate"]], how="left", on="sampleID")

        # Extract all of the gene names in this file
        self.genes = self.measure_data["type"].unique()

    def get_genes_reported(self):
        """Return the list of all genes reported"""
        return self.genes

    def get_data_by_gene(self, gene, units="gcL", mean=True):
        """Return datestamped data for a specific gene"""
        # Extract the necessary columns
        measure_data = self.measure_data[["sampleID", "type", "unit", "value", "qualityFlag", "sampleDate"]].copy()

        # Get the rows with the specified gene
        measure_data = measure_data.loc[self.measure_data["type"] == gene]

        # Drop any blanks
        measure_data = measure_data.dropna(subset=["value"])

        # Convert units as requires (note: only "gcL" and "gcMl" are supported)
        if units == "gcL":
            measure_data.loc[measure_data["unit"] == "gcMl", "value"] = measure_data["value"]*1000.0
            # Replace zeros with 0.5*LOD (LOD is currently a dummy value)
            measure_data.loc[measure_data["value"] < 300.0, "value"] = 150.0
        elif units == "gcMl":
            measure_data.loc[measure_data["unit"] == "gcL", "value"] = measure_data["value"]/1000.0
            # Replace zeros with 0.5*LOD (LOD is currently a dummy value)
            measure_data.loc[measure_data["value"] < 0.3, "value"] = 0.15
        else:
            raise ValueError("Invalid units \"{}\" given for wastewater measure.".format(units))

        # Compute the mean if needed
        if mean:
            measure_data = measure_data.groupby(["sampleID"]).agg({"value" : "mean", "sampleDate" : "first"})

        # Return the data
        return measure_data[["sampleDate", "value"]]

    def get_normalized_data(self, gene_1, gene_2, units="gcL"):
        """Return the datestamped data for a specific gene, normalized by another"""
        # Get the two dataframes
        data_1 = self.get_data_by_gene(gene_1, units)
        data_2 = self.get_data_by_gene(gene_2, units)

        # Merge the frames and compute normalized signal
        measure_data = data_1.merge(data_2, how="inner", on="sampleID")
        measure_data["value"] = measure_data["value_x"]/measure_data["value_y"]
        measure_data = measure_data.rename(columns={"sampleDate_x" : "sampleDate"}).drop(columns=["sampleDate_y"])

        # Return the data
        return measure_data[["sampleDate", "value"]]

    def get_standardized_data(self, gene_1, gene_2, units="gcL"):
        """Return the datestamped data for a normalized conecentration, standardized by its std. dev."""
        # Get the normalized data
        measure_data = self.get_normalized_data(gene_1, gene_2, units)

        # Normalize by standard deviation
        measure_data["value"] = measure_data["value"]/np.std(measure_data["value"])

        # Return the data
        return measure_data[["sampleDate", "value"]]

    def get_log_standardized_data(self, gene_1, gene_2, units="gcL"):
        """Return the datestamped data for standardized concentration, log transformed"""
        # Get the standardized data
        measure_data = self.get_standardized_data(gene_1, gene_2, units)

        # Log transform
        measure_data["value"] = np.log(measure_data["value"])

        # Return the data
        return measure_data[["sampleDate", "value"]]

    def get_spline_model(self, gene_1, gene_2, units="gcL"):
        """Return a spline model of the log standardized date, acceptng a datetime date as an argument"""
        # Get the log transformed standardized data
        measure_data = self.get_log_standardized_data(gene_1, gene_2, units)

        # Get the start/end dates of the model
        start_date = measure_data["sampleDate"].min()
        end_date = measure_data["sampleDate"].max()
        duration = delta_days(end_date, start_date)

        # Define the knots in the spline
        knots = np.arange(10, duration, 10)

        # Convert the date to a float value
        measure_data["sampleDate"] = measure_data["sampleDate"].apply(delta_days, args=(start_date,))

        # Sort by date
        measure_data = measure_data.sort_values(by=["sampleDate"])

        # Fit the spline model
        spline = LSQUnivariateSpline(measure_data["sampleDate"].to_numpy(), measure_data["value"].to_numpy(), knots)

        # Return the spline model
        return lambda x : spline_model(x, start_date, spline)
