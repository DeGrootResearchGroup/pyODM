import pandas as pd
import numpy as np

class SiteData():
    """Class used to store and access data for a named sampling site"""

    def __init__(self, data, site_id):
        """Class initialization"""

        # Store reference to the ODM data
        self._data = data

        # Store the site_id
        self._site_id = site_id

        # Read relevant information about the site
        #site_data = self.read_sheet(data_file, Sheets.site)
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
        """Return timestamped data for a specific gene"""
        # Extract the necessary columns
        measure_data = self.measure_data[["sampleID", "type", "unit", "value", "qualityFlag", "sampleDate"]].copy()

        # Get the rows with the specified gene
        measure_data = measure_data.loc[self.measure_data["type"] == gene]

        # Drop any blanks
        measure_data = measure_data.dropna(subset=["value"])

        # Convert units as requires (note: only "gcL" and "gcMl" are supported)
        if units == "gcL":
            measure_data.loc[measure_data["unit"] == "gcMl", "value"] = measure_data["value"]*1000.0
        elif units == "gcMl":
            measure_data.loc[measure_data["unit"] == "gcL", "value"] = measure_data["value"]/1000.0
        else:
            raise ValueError("Invalid units \"{}\" given for wastewater measure.".format(units))

        # Compute the mean if needed
        if mean:
            measure_data = measure_data.groupby(["sampleID"]).agg({"value" : "mean", "sampleDate" : "first"})

        # Return the data
        return measure_data[["sampleDate", "value"]]

    def get_normalized_data(self, gene_1, gene_2, units="gcL"):
        """Return the timestamped data for a specific gene, normalized by another"""
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
        """Return the timestamped data for a normalized conecentration, standardized by its std. dev."""
        # Get the normalized data
        measure_data = self.get_normalized_data(gene_1, gene_2, units)

        # Normalize by standard deviation
        measure_data["value"] = measure_data["value"]/np.std(measure_data["value"])

        # Return the data
        return measure_data[["sampleDate", "value"]]
