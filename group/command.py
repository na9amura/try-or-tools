import argparse
import pulp

from solver import create_lp_problem
from spreadsheet import create_spreadsheet_client


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('sheet_key', type=str, help='SpreadSheet ID to read')
    parser.add_argument('rosters_sheet_id', type=int, help='Rosters list sheet id')
    parser.add_argument('--previous', type=int, help='Previous group list sheet id')
    parser.add_argument('--name', type=str, required=True, help="Name of result sheet")
    parser.add_argument('--secret', type=str, default='./client-secret.json',
                        help="Path to Google service account's client secret file")
    args = parser.parse_args()

    sheet = create_spreadsheet_client(
        client_secret=args.secret,
        sheet_key=args.sheet_key,
        rosters_sheet_id=args.rosters_sheet_id)
    rosters = sheet.read_rosters()
    problem = create_lp_problem(rosters)
    status, result = problem.run()

    print(f'LP result: {pulp.LpStatus[status]}')

    rosters['Group'] = rosters['ID'].map(result)
    data = [[row.ID, row.Name, row.Group] for row in rosters.itertuples()]
    sheet.write(data, args.name)
