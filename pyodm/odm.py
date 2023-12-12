"""Module for representing a PHES-ODM formatted database.

The Public Health Environmental Surveillance Open Data Model (PHES-ODM) is
an open data model that is commonly used for wastewater-based surveillance.
The data model is described here: https://github.com/Big-Life-Lab/PHES-ODM.
"""

import pandas as pd
from datetime import datetime
import warnings
from pathlib import Path
from odm_validation.validation import validate_data
import odm_validation.utils as utils
import tempfile


class OdmTables():
    """Class defining properties of the ODM tables."""

    @staticmethod
    def attributes():
        """Return list of class attributes.

        Returns
        -------
        list
            List of attribute names.
        """
        return ['site', 'reporter', 'lab', 'instrument', 'assay_method',
            'sample', 'ww_measure', 'site_measure']


class Sheets(OdmTables):
    """Class with static variables for the sheet names."""
    site = "1 - Site"
    reporter = "2 - Reporter"
    lab = "3 - Lab"
    instrument = "4 - Instrument"
    assay_method = "5 - AssayMethod"
    sample = "6 - Sample"
    ww_measure = "7 - WWMeasure"
    site_measure = "8 - SiteMeasure"


class CSVs(OdmTables):
    """Class with static variables for the CSV file names."""
    site = "Site.csv"
    reporter = "Reporter.csv"
    lab = "Lab.csv"
    instrument = "Instrument.csv"
    assay_method = "AssayMethod.csv"
    sample = "Sample.csv"
    ww_measure = "WWMeasure.csv"
    site_measure = "SiteMeasure.csv"


excel_extensions = ['.xls', '.xlsx', '.xlsm', '.xlsb', '.odf', '.ods', '.odt']
default_schema_file = Path(__file__).parent / Path('assets/schema-v1.1.0.yml')


def _validate_csvs(data_loc, validation_schema_file):

    schema = utils.import_schema(validation_schema_file)
    validation_summary = {}

    for attr in OdmTables.attributes():
        samples = utils.import_dataset(data_loc / getattr(CSVs, attr))
        data = {"samples": samples}
        report = validate_data(schema, data)
        if len(report.errors) > 0:
            raise ValueError(f'The data located at attribute {attr} has generated validation error(s) when compared'
                             f'against the schema file at {validation_schema_file}. Check to see if the schema version '
                             f'matches that of the data. Specific details of the error(s) are given below,'
                             f'and more details about the validator can be found at '
                             f'https://github.com/Big-Life-Lab/PHES-ODM-Validation'
                             f'\n\n {report.errors}')

        validation_summary[attr] = report

    return validation_summary


class ODM():
    """Class used to represent an Open Data Model file as a set of pandas
    DataFrames.

    Parameters
    ----------
    data_loc : str
        Name of directory containing CSV files or
        Name of the Excel file containing the ODM-formatted data

    Notes
    -----
    The individual datasets are retained in unmodified form, with the exception of
    ``Sheet 6 - Sample`` or ``Sample.csv`` which has a column ``sampleDate`` added.
    The ``sampleDate`` field unifies the ``dateTime`` and ``dateTimeEnd`` which
    are used for grab and composite samples, respectively.
    """

    def __init__(self, data_loc=None, validate_data=True, validation_schema_file=default_schema_file):
        """Class initialization"""
        self._data = {}
        self.validation_summary = {}

        csv_dir = data_loc

        if data_loc:
            data_loc = Path(data_loc)
            suffix = data_loc.suffix

            if suffix in excel_extensions:  # Excel file
                for attr in OdmTables.attributes():
                    self._data[attr] = self.read_sheet(data_loc, getattr(Sheets, attr))

                if validate_data:  # Export excel to temporary csv files
                    out_dir = Path(tempfile.mkdtemp(suffix='-' + data_loc.name))
                    csv_dir = out_dir / 'csv-files'
                    self.export_csvs(csv_dir)

            elif suffix == '':  # Directory
                for attr in OdmTables.attributes():
                    self._data[attr] = self.read_csv(data_loc / getattr(CSVs, attr))

            else:
                raise TypeError(f'A filepath with invalid extension {suffix}, was passed to the ODM constructor. \n'
                                f'Creating an ODM object requires either a directory containing .csv files or an'
                                f' Excel-like file with one of the following extensions: {excel_extensions}')

            if validate_data:
                self.validation_summary = _validate_csvs(csv_dir, validation_schema_file)

        else:
            for attr in OdmTables.attributes():
                self._data[attr] = pd.DataFrame()

    def read_csv(self, file_name):
        """Read a csv file.

        Parameters
        ----------
        file_name : str, Path
            Name of the CSV file.

        Returns
        -------
        pandas.DataFrame
            The data contained in the specified CSV file.
        """
        warnings.simplefilter(action='ignore', category=UserWarning)
        return pd.read_csv(file_name)

    def read_sheet(self, file_name, sheet_name):
        """Read a sheet from an Excel file.

        Parameters
        ----------
        file_name : str, Path
            Name of the Excel file.
        sheet_name : str
            Name of the sheet to be read.

        Returns
        -------
        pandas.DataFrame
            The data contained in the specified Excel sheet.
        """
        warnings.simplefilter(action='ignore', category=UserWarning)
        return pd.read_excel(file_name, sheet_name)

    def export_csvs(self,dir_path):
        """Export ODM formatted dataset into directory as CSV files.

        Parameters
        ----------
        dir_path : str, Path
            Name of the directory.
        """
        dir_path = Path(dir_path)

        if not dir_path.is_dir():
            dir_path.mkdir()

        for attr in CSVs.attributes():
            df = self._data[attr]
            df.to_csv(dir_path / getattr(CSVs, attr), index=False)

    def export_excel(self, file_name):
        """Export ODM formatted dataset into Excel sheets.

        Parameters
        ----------
        file_name : str, Path
            Name of the Excel file.
        """
        with pd.ExcelWriter(file_name) as excel_writer:
            for attr in Sheets.attributes():
                df = self._data[attr]
                df.set_index(df.columns[0], inplace=True)
                df.to_excel(excel_writer, sheet_name=getattr(Sheets, attr))

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
        samples = self.sample[['sampleID', 'dateTimeEnd', 'dateTime']].copy()

        # Add a temporary column that takes the date from either dateTime or
        # dateTimeEnd, whichever is present
        samples['sampleDate'] = pd.to_datetime(samples['dateTimeEnd'].fillna(samples['dateTime'])).dt.date

        # Add a temporary column that tracks whether to keep the sample
        samples['keep'] = True

        # Find samples that meet date criteria
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            samples['keep'] = (samples['keep'] & (samples['sampleDate'] >= start_date))
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            samples['keep'] = (samples['keep'] & (samples['sampleDate'] <= end_date))
        samples = samples[samples['keep']]

        # Filter the data that is date-based
        self._data['sample'] = self.sample.loc[self.sample['sampleID'].isin(samples['sampleID'])]
        self._data['ww_measure'] = self.ww_measure.loc[self.ww_measure['sampleID'].isin(samples['sampleID'])]
        self._data['site_measure'] = self.site_measure.loc[self.site_measure['sampleID'].isin(samples['sampleID'])]

        # Return the object to allow for assignment
        return self

    @property
    def site(self):
        """Get the site data frame.

        Returns
        -------
        pandas.DataFrame
            The "Site" data, which contains information about the sites being
            samples.
        """
        return self._data['site']

    @property
    def reporter(self):
        """Get the reporter data frame.

        Returns
        -------
        pandas.DataFrame
            The "Reporter" data, which contains information about the people
            reporting the data.
        """
        return self._data['reporter']

    @property
    def lab(self):
        """Get the lab frame.

        Returns
        -------
        pandas.DataFrame
            The "Lab" data, which contains information about the reporting
            lab(s).
        """
        return self._data['lab']

    @property
    def instrument(self):
        """Get the instrument data frame.

        Returns
        -------
        pandas.DataFrame
            The "Instrument" data, which contains information about the
            instrument being used to collect the data.
        """
        return self._data['instrument']

    @property
    def assay_method(self):
        """Get the assay method data frame.

        Returns
        -------
        pandas.DataFrame
            The "AssayMethod" data, which contains information about the
            assay method(s) being used to collect the data.
        """
        return self._data['assay_method']

    @property
    def sample(self):
        """Get the sample data frame.

        Returns
        -------
        pandas.DataFrame
            The "Sample" data, which contains information about the samples
            collected.
        """
        return self._data['sample']

    @property
    def ww_measure(self):
        """Get the ww measure data frame.

        Returns
        -------
        pandas.DataFrame
            The "WWMeasure" data, which contains the wastewater measurements
            made on the samples collected.
        """
        return self._data['ww_measure']

    @property
    def site_measure(self):
        """Get the site measure data frame.

        Returns
        -------
        pandas.DataFrame
            The "SiteMeasure" data, which contains additional measurements
            made relating to the collection site.
        """
        return self._data['site_measure']

    @staticmethod
    def combine(first, second):
        """Combine the tables from another two ODM objects.

        Parameters
        ----------
        first : ODM
            First ODM object.
        second : ODM
            Second ODM object.

        Returns
        -------
        ODM
            ODM object containing tables combined from the two input arguments.
        """
        new = ODM()
        for attr in OdmTables.attributes():
            new._data[attr] = pd.concat([getattr(first, attr), getattr(second, attr)])
            new._data[attr].drop_duplicates(subset=new._data[attr].columns[0], keep='first', inplace=True)
        return new

    def __add__(self, other):
        """Add two ODM objects together"""
        return ODM.combine(self, other)
