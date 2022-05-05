import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


class Spreadsheet:
    sheets: gspread.Spreadsheet
    rosters: pd.DataFrame

    def __init__(self, *, sheets: gspread.Spreadsheet, rosters: pd.DataFrame):
        self.sheets = sheets
        self.rosters = rosters

    def check_sheet(self, name: str) -> bool:
        sheet = self.sheets.worksheet(name)
        return False if sheet else True

    def read_rosters(self) -> pd.DataFrame:
        rosters = self.rosters
        rosters = rosters[rosters['参加'] == 'TRUE'].rename(columns={'名前': 'Name'}).filter(items=['ID', 'Name', 'Role'])
        rosters = pd.get_dummies(rosters, columns=["Role"])

        return rosters

    def read_prev_group(self) -> pd.DataFrame:
        return None

    def write(self, data: list[list[object]], worksheet_name: str):
        new_sheet = self.sheets.add_worksheet(worksheet_name, 0, 0)
        new_sheet.update("A1:C1", [['ID', 'Name', 'Group']])
        new_sheet.update("A2:C", data)


def create_spreadsheet_client(*, client_secret: str, sheet_key: str, rosters_sheet_id: int) -> Spreadsheet:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(client_secret, scope)
    client = gspread.authorize(creds)
    sheets = client.open_by_key(sheet_key)
    rosters_sheet = sheets.get_worksheet_by_id(rosters_sheet_id)

    records = rosters_sheet.get_all_records()
    df = pd.DataFrame(records)
    return Spreadsheet(sheets=sheets, rosters=df)
