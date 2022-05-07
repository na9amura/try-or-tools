import argparse
import sys

import pulp

from solver import create_lp_problem
from spreadsheet import create_spreadsheet_client


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('sheet_key', type=str, help='SpreadSheet ID to read')
    parser.add_argument('rosters_sheet_id', type=int, help='Rosters list sheet id')
    parser.add_argument('--prev', type=int, help='Previous group list sheet id')
    parser.add_argument('--name', type=str, required=True, help="Name of result sheet")
    parser.add_argument('--secret', type=str, default='./client-secret.json',
                        help="Path to Google service account's client secret file")
    args = parser.parse_args()

    prev_sheet_id = args.prev
    sheet = create_spreadsheet_client(
        client_secret=args.secret,
        sheet_key=args.sheet_key,
        rosters_sheet_id=args.rosters_sheet_id,
        prev_sheet_id=prev_sheet_id)

    name = args.name
    res = sheet.sheet_exists(name)
    if res:
        sys.exit(f"Sheet '{name}' already exists")

    rosters = sheet.read_rosters()
    prev = sheet.read_prev_group()
    problem = create_lp_problem(rosters, prev_group=prev)
    status, result = problem.run()

    if pulp.LpStatus[status] != pulp.LpStatus.LpStatusOptimal:
        sys.exit(f"Failed to solve: {pulp.LpStatus[status]}")

    rosters['Group'] = rosters['ID'].map(result)
    data = [[row.ID, row.Name, row.Group] for row in rosters.itertuples()]
    result = sheet.write(data, name)
    print("Update finished")

