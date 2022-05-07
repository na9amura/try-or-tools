import pandas as pd
import pulp
import string


class Problem:
    M: list[int]
    G: list[int]
    MG: list[(int, int)]
    prev_group_mates = dict()
    swe_list: list[int]
    X: pulp.LpVariable.dicts

    def __init__(self, members: list[int], groups: list[int], swe_list: list[int], prev_group_mates: dict):
        self.M = members
        self.G = groups
        self.MG = [(m, g) for m in members for g in groups]
        self.swe_list = swe_list
        self.prev_group_mates = prev_group_mates

    def run(self) -> (pulp.LpStatus, dict):
        problem = self.__create_problem()
        status = problem.solve()

        return status, {m: g for m in self.M for g in self.G if self.X[m, g].value() == 1}

    def __create_problem(self) -> pulp.LpProblem:
        # Variables
        self.X = pulp.LpVariable.dicts('X', self.MG, cat=pulp.LpBinary)

        problem = pulp.LpProblem("Group", pulp.LpMaximize)

        # 1. Members must be assigned to one group
        for m in self.M:
            problem += pulp.lpSum(self.X[m, g] for g in self.G) == 1

        # 2. Number of members in a group must be 3 to 4
        for g in self.G:
            problem += pulp.lpSum(self.X[m, g] for m in self.M) >= 3
            problem += pulp.lpSum(self.X[m, g] for m in self.M) <= 4

        # 3. Max members of SwE must be 2
        for g in self.G:
            problem += pulp.lpSum(self.X[m, g] for m in self.swe_list) <= 2

        # 4. Avoid previous group members
        if len(self.prev_group_mates) > 0:
            for n, members in self.prev_group_mates.items():
                for g in self.G:
                    problem += pulp.lpSum(self.X[m, g] for m in members) <= 2

        return problem


def create_lp_problem(df, *, members_per_group=3, prev_group=pd.DataFrame([])) -> Problem:
    len_members = len(df)
    len_groups = int(len_members / members_per_group)
    members = df['ID'].tolist()
    groups = list(string.ascii_uppercase[:len_groups])

    swe_list = df[df['Role_Engineer'] == 1]['ID'].tolist()

    prev_group_mates = dict()
    if len(prev_group) > 0:
        for g, data in prev_group.groupby('Group'):
            _members = data['ID'].to_list()
            for name in members:
                prev_group_mates[name] = _members

    return Problem(members, groups, swe_list, prev_group_mates)
