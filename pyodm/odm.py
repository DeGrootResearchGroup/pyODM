"""Module for representing a PHES-ODM formatted database.

The Public Health Environmental Surveillance Open Data Model (PHES-ODM) is
an open data model that is commonly used for wastewater-based surveillance.
The data model is described here: https://github.com/Big-Life-Lab/PHES-ODM.
"""

import pandas as pd
from datetime import datetime
import warnings

class Sheets():
    """Class with static variables for the sheet names."""
    site = "1 - Site"
    reporter = "2 - Reporter"
    lab = "3 - Lab"
    instrument = "4 - Instrument"
    assay_method = "5 - AssayMethod"
    sample = "6 - Sample"
    ww_measure = "7 - WWMeasure"
    site_measure = "8 - SiteMeasure"

class ODM():
    """Class used to represent an Open Data Model file as a set of pandas
    DataFrames.

    Parameters
    ----------
    data_file : str
        Name of the Excel file containing the ODM-formatted data.

    Notes
    -----
    The data sheets in the ODM file are retained in unmodified form, with
    the exception of the "Sample" data sheet which has a column ``sampleDate``
    added. The ``sampleDate`` field unifies the ``dateTime`` and ``dateTimeEnd``
    which are used for grab and composite samples, respectively.
    """

    def __init__(self, data_file):
        """Class initialization"""
        # Read all of the sheets from the Excel file
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
        # Add a "sampleDate" column, which is either the date of the grab sample
        # or the end date of a composite
        self._sheets[Sheets.sample]["sampleDate"] = pd.to_datetime(self._sheets[Sheets.sample]["dateTimeEnd"].fillna(self._sheets[Sheets.sample]["dateTime"])).dt.date

    def read_sheet(self, file_name, sheet_name):
        """Read a sheet from an Excel file.

        Parameters
        ----------
        file_name : str
            Name of the Excel file.
        sheet_name : str
            Name of the sheet to be read.

        Returns
        -------
        pandas.DataFrame
            The data contained in the specified Excel sheet.
        """
        # Ignore warnings about Excel data validation
        warnings.simplefilter(action='ignore', category=UserWarning)
        return pd.read_excel(file_name, sheet_name=sheet_name)

    def filter_dates(self, start_date=None, end_date=None):
        """Filter the data by sample date.

        Data before start_date and after end_date will be deleted from all
        DataFrames. Data falling exactly on these dates will be retained.

        Parameters
        ----------
        start_date : str, optional
            Start date in the format "YYYY-MM-DD"
        end_date : str, optional
            End date in the format "YYYY-MM-DD"
        """
        # Get a dataframe with the sample IDs and the time information
        samples = self.sample[["sampleID", "sampleDate"]].copy()

        # Find samples that meet date criteria
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            samples = samples[samples["sampleDate"] >= start_date]
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            samples = samples[samples["sampleDate"] <= end_date]

        # Filter the data that is date-based
        self._sheets[Sheets.sample] = self.sample.loc[self.sample["sampleID"].isin(samples["sampleID"])]
        self._sheets[Sheets.ww_measure] = self.ww_measure.loc[self.ww_measure["sampleID"].isin(samples["sampleID"])]
        self._sheets[Sheets.site_measure] = self.site_measure.loc[self.site_measure["sampleID"].isin(samples["sampleID"])]

    @property
    def site(self):
        """Get the site data frame.

        Returns
        -------
        pandas.DataFrame
            The "Site" data, which contains information about the sites being
            samples.
        """
        return self._sheets[Sheets.site]

    @property
    def reporter(self):
        """Get the reporter data frame.

        Returns
        -------
        pandas.DataFrame
            The "Reporter" data, which contains information about the people
            reporting the data.
        """
        return self._sheets[Sheets.reporter]

    @property
    def lab(self):
        """Get the lab frame.

        Returns
        -------
        pandas.DataFrame
            The "Lab" data, which contains information about the reporting
            lab(s).
        """
        return self._sheets[Sheets.lab]

    @property
    def instrument(self):
        """Get the instrument data frame.

        Returns
        -------
        pandas.DataFrame
            The "Instrument" data, which contains information about the
            instrument being used to collect the data.
        """
        return self._sheets[Sheets.instrument]

    @property
    def assay_method(self):
        """Get the assay method data frame.

        Returns
        -------
        pandas.DataFrame
            The "AssayMethod" data, which contains information about the
            assay method(s) being used to collect the data.
        """
        return self._sheets[Sheets.assay_method]

    @property
    def sample(self):
        """Get the sample data frame.

        Returns
        -------
        pandas.DataFrame
            The "Sample" data, which contains information about the samples
            collected.
        """
        return self._sheets[Sheets.sample]

    @property
    def ww_measure(self):
        """Get the ww measure data frame.

        Returns
        -------
        pandas.DataFrame
            The "WWMeasure" data, which contains the wastewater measurements
            made on the samples collected.
        """
        return self._sheets[Sheets.ww_measure]

    @property
    def site_measure(self):
        """Get the site measure data frame.

        Returns
        -------
        pandas.DataFrame
            The "SiteMeasure" data, which contains additional measurements
            made relating to the collection site.
        """
        return self._sheets[Sheets.site_measure]
