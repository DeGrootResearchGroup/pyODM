from pyodm import ODM
import os

EXCEL_SHEETS = './Wastewater_COVID19_2022_02_18/sheets/sheets.xlsx'
CSV_DIR = './Wastewater_COVID19_2022_02_18/data'

odm = ODM(EXCEL_SHEETS)
odm.filter_dates()
odm.export_csvs('output_directory')


odm = ODM(CSV_DIR)
odm.filter_dates()
odm.export_excel(os.path.join('output_directory', 'sheets.xlsx'))
