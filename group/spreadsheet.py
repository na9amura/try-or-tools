import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


class Spreadsheet:
    sheets: gspread.Spreadsheet
    rosters_sheet_id: int
    prev_sheet_id: int

    def __init__(self, sheets: gspread.Spreadsheet, rosters_sheet_id: int, prev_sheet_id: int):
        self.sheets = sheets
        self.rosters_sheet_id = rosters_sheet_id
        self.prev_sheet_id = prev_sheet_id

    def sheet_exists(self, name: str) -> bool:
        try:
            self.sheets.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            return False
        return True

    def read_rosters(self) -> pd.DataFrame:
        rosters = self.__read(self.rosters_sheet_id)
        rosters = rosters[rosters['参加'] == 'TRUE'].rename(columns={'名前': 'Name'}).filter(items=['ID', 'Name', 'Role'])
        rosters = pd.get_dummies(rosters, columns=["Role"])
        return rosters

    def read_prev_group(self) -> pd.DataFrame:
        if self.prev_sheet_id:
            prev = self.__read(self.prev_sheet_id)
            return prev
        else:
            return pd.DataFrame([])

    def write(self, data: list[list[object]], worksheet_name: str):
        new_sheet = self.sheets.add_worksheet(worksheet_name, 0, 0)
        new_sheet.update("A1:C1", [['ID', 'Name', 'Group']])
        new_sheet.update("A2:C", data)

    def __read(self, sheer_id: int) -> pd.DataFrame:
        sheet = self.sheets.get_worksheet_by_id(sheer_id)
        records = sheet.get_all_records()
        return pd.DataFrame(records)


def create_spreadsheet_client(*, client_secret: str, sheet_key: str, rosters_sheet_id: int, prev_sheet_id: int) -> Spreadsheet:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(client_secret, scope)
    client = gspread.authorize(creds)
    sheets = client.open_by_key(sheet_key)
    return Spreadsheet(sheets, rosters_sheet_id, prev_sheet_id)
