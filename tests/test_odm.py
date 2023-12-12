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
def example_odm1(excel_file_path):
    return ODM(excel_file_path)

@pytest.fixture
def example_odm2(excel_file_path):
    return ODM(excel_file_path)

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
