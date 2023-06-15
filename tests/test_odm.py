from pyodm import ODM
import pytest

@pytest.fixture
def excel_file_path():
    return ('example/Wastewater_COVID19_2022_02_18/sheets/sheets.xlsx')

@pytest.fixture
def csv_dir_path():
    return ('example/Wastewater_COVID19_2022_02_18/data/')

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
