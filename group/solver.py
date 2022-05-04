import pandas as pd
import pulp
import string


class Problem:
    df: pd.DataFrame
    len_groups: int
    prev_group_mates = dict()
    M: list[int]
    G: list[int]
    MG: list[(int, int)]
    X: pulp.LpVariable.dicts

    def __init__(self, file: string, *, members_per_group=3, prev_group=pd.DataFrame([])):
        self.df = pd.read_csv(file)
        len_members = len(self.df)
        self.len_groups = int(len_members / members_per_group)

        for g, data in prev_group.groupby('group'):
            members = data['ID'].to_list()
            for name in members:
                self.prev_group_mates[name] = members

    def run(self, ) -> pd.DataFrame:
        problem = self.__create_problem()
        problem.solve()

        result_df = self.df.copy()
        result_df['group'] = result_df['ID'].map({m: g for m in self.M for g in self.G if self.X[m, g].value() == 1})

        return result_df

    def __create_problem(self) -> pulp.LpProblem:
        # Variables
        self.M = self.df['ID'].tolist()
        self.G = list(string.ascii_uppercase[:self.len_groups])
        self.MG = [(m, g) for m in self.M for g in self.G]
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
        swe = self.df[self.df['SwE'] == 1]['ID'].tolist()
        for g in self.G:
            problem += pulp.lpSum(self.X[m, g] for m in swe) <= 2

        # 4. Avoid previous group members
        for n, members in self.prev_group_mates.items():
            for g in self.G:
                problem += pulp.lpSum(self.X[m, g] for m in members) <= 2

        return problem
