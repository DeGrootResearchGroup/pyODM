import pandas as pd
from datetime import datetime
import warnings

class Sheets():
    """Class with static variables for the sheet names"""
    site = "1 - Site"
    reporter = "2 - Reporter"
    lab = "3 - Lab"
    instrument = "4 - Instrument"
    assay_method = "5 - AssayMethod"
    sample = "6 - Sample"
    ww_measure = "7 - WWMeasure"
    site_measure = "8 - SiteMeasure"

class ODM():
    """Class used to represent Open Data Model file as pandas dataframes"""

    def __init__(self, data_file):
        """Class initialization"""
        # Read all of the sheets
        self._sheets = {
            Sheets.site : self.read_sheet(data_file, Sheets.site),
            Sheets.reporter : self.read_sheet(data_file, Sheets.reporter),
            Sheets.lab : self.read_sheet(data_file, Sheets.lab),
            Sheets.instrument : self.read_sheet(data_file, Sheets.instrument),
            Sheets.assay_method : self.read_sheet(data_file, Sheets.assay_method),
            Sheets.sample : self.read_sheet(data_file, Sheets.sample),
            Sheets.ww_measure : self.read_sheet(data_file, Sheets.ww_measure),
            Sheets.site_measure : self.read_sheet(data_file, Sheets.site_measure)
        }

    def read_sheet(self, file_name, sheet_name):
        """Function to read an excel sheet"""
        # Ignore warnings about Excel data validation
        warnings.simplefilter(action='ignore', category=UserWarning)
        return pd.read_excel(file_name, sheet_name=sheet_name)

    def filter_dates(self, start_date=None, end_date=None):
        """Function to filter the data by date
            Notes:
                - The dates are strings in the format "YYYY-MM-DD"
        """
        # Get a dataframe with the sample IDs and the time information
        samples = self._sheets[Sheets.sample][["sampleID", "dateTime", "dateTimeEnd"]].copy()

        # Add "sampleDate" which is either the date of the grab sample or the end date of a composite
        samples["sampleDate"] = pd.to_datetime(samples["dateTimeEnd"].fillna(samples["dateTime"])).dt.date

        # Filter the data that meet the date criteria
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            samples = samples[samples["sampleDate"] >= start_date]
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            samples = samples[samples["sampleDate"] <= end_date]

        # Filter the data that is date-based
        self._sheets[Sheets.sample] = self._sheets[Sheets.sample].loc[self._sheets[Sheets.sample]["sampleID"].isin(samples["sampleID"])]
        self._sheets[Sheets.ww_measure] = self._sheets[Sheets.ww_measure].loc[self._sheets[Sheets.ww_measure]["sampleID"].isin(samples["sampleID"])]
        self._sheets[Sheets.site_measure] = self._sheets[Sheets.site_measure].loc[self._sheets[Sheets.site_measure]["sampleID"].isin(samples["sampleID"])]

    @property
    def site(self):
        """Function to get the site data frame"""
        return self._sheets[Sheets.site]

    @property
    def reporter(self):
        """Function to get the reporter data frame"""
        return self._sheets[Sheets.reporter]

    @property
    def lab(self):
        """Function to get the lab frame"""
        return self._sheets[Sheets.lab]

    @property
    def instrument(self):
        """Function to get the instrument data frame"""
        return self._sheets[Sheets.instrument]

    @property
    def assay_method(self):
        """Function to get the assay method data frame"""
        return self._sheets[Sheets.assay_method]

    @property
    def sample(self):
        """Function to get the sample data frame"""
        return self._sheets[Sheets.sample]

    @property
    def ww_measure(self):
        """Function to get the ww measure data frame"""
        return self._sheets[Sheets.ww_measure]

    @property
    def site_measure(self):
        """Function to get the site measure data frame"""
        return self._sheets[Sheets.site_measure]
