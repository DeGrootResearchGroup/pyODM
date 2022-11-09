from pyodm import ODM
import pytest

@pytest.fixture
def excel_file_path():
    return ('example/Wastewater_COVID19_2022_02_18/data/sheets.xlsx')

@pytest.fixture
def csv_dir_path():
    return ('example/Wastewater_COVID19_2022_02_18/data/')

def test_init_odm_with_sheets():
    odm = ODM(excel_file_path)
    print(odm)
    assert True

# def test_init_odm_with_csv():
#     odm = ODM(csv_dir_path)
#     return True

