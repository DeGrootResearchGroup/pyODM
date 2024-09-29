from pyodm import ODM
import pytest
from pathlib import Path
from datetime import datetime

@pytest.fixture
def excel_file_path():
    return Path('example/Wastewater_COVID19_2022_02_18/sheets/sheets.xlsx')

@pytest.fixture
def csv_dir_path():
    return Path('example/Wastewater_COVID19_2022_02_18/data/')

@pytest.fixture
def csv_duplicate_path1():
    return Path('example/Wastewater_COVID19_2022_02_18/duplicate1/')

@pytest.fixture
def csv_duplicate_path2():
    return Path('example/Wastewater_COVID19_2022_02_18/duplicate2/')

@pytest.fixture
def example_odm1(excel_file_path):
    return ODM(excel_file_path)

@pytest.fixture
def example_odm2(excel_file_path):
    return ODM(excel_file_path)

@pytest.fixture
def duplicate_odm1(csv_duplicate_path1):
    return ODM(csv_duplicate_path1)

@pytest.fixture
def duplicate_odm2(csv_duplicate_path2):
    return ODM(csv_duplicate_path2)

def test_init_odm_with_excel(excel_file_path):
    odm = ODM(excel_file_path)
    assert True

def test_init_odm_with_csv(csv_dir_path):
    odm = ODM(csv_dir_path)
    assert True

def test_add_odms(example_odm1, example_odm2):
    odm = example_odm1 + example_odm2
    assert True

def test_filter_start_date(excel_file_path):
    odm = ODM(excel_file_path)
    odm.filter_dates(start_date='2021-1-31')
    min_date = datetime.strptime(odm._data['sample']['dateTimeEnd'].max(), '%Y-%m-%d %H:%M:%S').date()
    assert (min_date >= datetime.strptime('2021-1-31', '%Y-%m-%d').date())

def test_filter_end_date(excel_file_path):
    odm = ODM(excel_file_path)
    odm.filter_dates(end_date='2021-12-31')
    max_date = datetime.strptime(odm._data['sample']['dateTimeEnd'].max(), '%Y-%m-%d %H:%M:%S').date()
    assert (max_date <= datetime.strptime('2021-12-31', '%Y-%m-%d').date())

def test_filter_start_and_end_date(excel_file_path):
    odm = ODM(excel_file_path)
    odm.filter_dates(start_date='2021-1-31', end_date='2021-12-31')
    min_date = datetime.strptime(odm._data['sample']['dateTimeEnd'].max(), '%Y-%m-%d %H:%M:%S').date()
    max_date = datetime.strptime(odm._data['sample']['dateTimeEnd'].max(), '%Y-%m-%d %H:%M:%S').date()
    assert (min_date >= datetime.strptime('2021-1-31', '%Y-%m-%d').date())
    assert (max_date <= datetime.strptime('2021-12-31', '%Y-%m-%d').date())

def test_combine_duplicate_odms(duplicate_odm1:ODM,duplicate_odm2:ODM):

    odm = duplicate_odm1.__add__(duplicate_odm2)
    sites1 = duplicate_odm1._data['site']
    sites2 = duplicate_odm2._data['site']

    samples1 = duplicate_odm1._data['sample']
    samples2 = duplicate_odm2._data['sample']

    sites = odm._data['site']
    samples = odm._data['sample']
    
    assert(len(sites) == len(sites1)+1)
    assert(len(samples) == len(samples1) + len(samples2))

    # check to make sure that the pseudo-duplicate siteID was inserted with a suffix
    assert(sites.iloc[-1,0] == sites2.iloc[-1,0] == sites1.iloc[-1,0] + "_1")

    # check to make sure that the pseudo-duplicate sampleID was inserted with a suffix
    assert(samples.iloc[-1,0] == samples2.iloc[-1,0] == samples1.iloc[-1,0] + "_1")
    assert(samples.iloc[-2,0] == samples2.iloc[-2,0] == samples1.iloc[-2,0] + "_1")
