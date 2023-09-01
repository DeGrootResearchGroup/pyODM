from pyodm import ODM
from pathlib import Path

EXCEL_SHEETS = Path('./Wastewater_COVID19_2022_02_18/sheets/sheets.xlsx')
CSV_DIR = Path('./Wastewater_COVID19_2022_02_18/data')
OUT_DIR = Path('output_directory')

odm = ODM(EXCEL_SHEETS)
odm.filter_dates()
odm.export_csvs(OUT_DIR)

odm = ODM(CSV_DIR)
odm.filter_dates()
odm.export_excel(OUT_DIR / 'sheets.xlsx')
