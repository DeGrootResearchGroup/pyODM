import pandas as pd
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
        self._site = self.read_sheet(data_file, Sheets.site)
        self._reporter = self.read_sheet(data_file, Sheets.reporter)
        self._lab = self.read_sheet(data_file, Sheets.lab)
        self._instrument = self.read_sheet(data_file, Sheets.instrument)
        self._assay_method = self.read_sheet(data_file, Sheets.assay_method)
        self._sample = self.read_sheet(data_file, Sheets.sample)
        self._ww_measure = self.read_sheet(data_file, Sheets.ww_measure)
        self._site_measure = self.read_sheet(data_file, Sheets.site_measure)

    def read_sheet(self, file_name, sheet_name):
        """Function to read an excel sheet"""
        # Ignore warnings about Excel data validation
        warnings.simplefilter(action='ignore', category=UserWarning)
        return pd.read_excel(file_name, sheet_name=sheet_name)

    @property
    def site(self):
        """Function to get the site data frame"""
        return self._site

    @property
    def reporter(self):
        """Function to get the reporter data frame"""
        return self._reporter

    @property
    def lab(self):
        """Function to get the lab frame"""
        return self._lab

    @property
    def instrument(self):
        """Function to get the instrument data frame"""
        return self._instrument

    @property
    def assay_method(self):
        """Function to get the assay method data frame"""
        return self._assay_method

    @property
    def sample(self):
        """Function to get the sample data frame"""
        return self._sample

    @property
    def ww_measure(self):
        """Function to get the ww measure data frame"""
        return self._ww_measure

    @property
    def site_measure(self):
        """Function to get the site measure data frame"""
        return self._site_measure
