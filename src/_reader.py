import json
import os
import random

import re
from datetime import datetime

from typing import Dict, List, Any

BAD_CONNECT_COST = 10_000  # large number for missing connections
PENALTY_VALUE_FAMILY = 25
SIBLING_COST = 5  # more than the 4.x
PENALTY_VALUE_FAMILY_G_R = PENALTY_VALUE_FAMILY * 3
YEAR_JSON_PATTERN = re.compile(r"^(\d{4})\.json$")


def read_json_file(filepath: str) -> Dict[str, Any]:
    """Read and return JSON data from a single file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def read_all_year_json_files(directory: str) -> Dict[str, Dict[str, str]]:
    """Read all JSON files in a directory whose names end with .json."""
    data_by_year = {}

    for filename in os.listdir(directory):
        match = YEAR_JSON_PATTERN.match(filename)
        if match:
            year_match = match.group(1)
            full_path = os.path.join(directory, filename)
            data_by_year[year_match] = read_json_file(full_path)

    return data_by_year


COST_TABLE = [BAD_CONNECT_COST, BAD_CONNECT_COST / 10, BAD_CONNECT_COST / 25, 15, 10, 4, 4, 4, 4, 4, 4, 4]


def cost_func(year_index: int) -> int:
    current_year = datetime.now().year
    index = current_year - year_index
    if index < 0:
        # Future year → treat as index 0
        return COST_TABLE[0]

    if index >= len(COST_TABLE):
        # Too far in the past → clamp to last value
        return COST_TABLE[-1]
    return COST_TABLE[index]


class Reader:
    def __init__(self):
        self.names_list: List[str] = []
        self.connections: Dict[str, Dict[str, int]] = {}
        self.ignore_people: List = []
        self.families: Dict[str, List[str]] = {}
        self.other_costs = {}
        self.kids = []

    @classmethod
    def ignore_comment_key(cls, key: str) -> bool:
        return key.startswith("#") or key == "comment"

    def ignore_person(self, key) -> bool:
        return key in self.ignore_people

    # String,String,Int
    def add_connections(self, name1, name2, value):
        # skip 0, since everything is connected at 0 by default
        if value != 0:
            if name1 not in self.connections:
                self.connections[name1] = {name2: value}
                return
            if name2 in self.connections[name1]:
                self.connections[name1][name2] = self.connections[name1][name2] + value
                return
            self.connections[name1][name2] = value
        return

    # return an int that represents to value of this gift from name1 to name2
    def get_value(self, name1: str, name2: str):
        if name1 in self.connections:
            if name2 in self.connections[name1]:
                return self.connections[name1][name2]
        return 0

    # given a list of names where each entry is the giver and the next entry is the receiver.
    # The last entry needs to connect to the first
    # return the total value
    def get_total_value(self, name_list: List[str], with_print=False) -> int:
        total = 0
        for cnt in range(0, len(name_list) - 1):
            value = self.get_value(name_list[cnt], name_list[cnt + 1])
            total += value
            if with_print:
                print("{} - {}, this = {} Cumulative ={}".format(name_list[cnt], name_list[cnt + 1], value, total))
        penalties = self.get_penalties(name_list)
        if with_print:
            print("penalties = {}".format(penalties))
        return total + penalties

    @classmethod
    def three_names_in_family(cls, family, name_r, name_rg, name_g):
        return name_r in family and name_rg in family and name_g in family

    @classmethod
    def both_names_in_family(cls, family, name_g, name_r):
        return name_g in family and name_r in family

    # reciprocal giving, (tail = start)
    def check_pairing(self, name_list):
        member_family = {}
        for family_name in self.families.keys():
            family = self.families[family_name]
            for member in family:
                member_family[member] = family_name
        joint_count = {}
        for cnt in range(0, len(name_list) - 1):
            first_family = member_family[name_list[cnt]]
            second_family = member_family[name_list[cnt + 1]]
            if first_family + "-" + second_family in joint_count:
                joint_count[first_family + "-" + second_family] += 1
            else:
                joint_count[first_family + "-" + second_family] = 1

        total = 0
        for pairs in joint_count.keys():
            total += (joint_count[pairs] ^ 2) - 1
        print("pairing = {}".format(joint_count))
        return total

    # currently solved by picking 3 random results
    # since distribution is bad, this is difficult for a general giving
    def get_penalties(self, name_list):
        penalty = 0
        for family_name in self.families.keys():
            family = self.families[family_name]
            for cnt in range(0, len(name_list) - 1):
                if self.both_names_in_family(family, name_list[cnt], name_list[cnt + 1]):
                    penalty += PENALTY_VALUE_FAMILY
                if cnt > 0 and self.three_names_in_family(family, name_list[cnt - 1], name_list[cnt],
                                                          name_list[cnt + 1]):
                    penalty += PENALTY_VALUE_FAMILY_G_R

                # reciprocal rule Tony->Michael->Karin
                if cnt > 0 and self.both_names_in_family(family, name_list[cnt - 1], name_list[cnt + 1]):
                    penalty += PENALTY_VALUE_FAMILY_G_R

            # same rules but for ends of list
            if self.both_names_in_family(family, name_list[len(name_list) - 1], name_list[0]):
                penalty += PENALTY_VALUE_FAMILY

            if self.three_names_in_family(family, name_list[len(name_list) - 1], name_list[0], name_list[1]):
                penalty += PENALTY_VALUE_FAMILY_G_R

            if self.three_names_in_family(family, name_list[len(name_list) - 2], name_list[len(name_list) - 1],
                                          name_list[0]):
                penalty += PENALTY_VALUE_FAMILY_G_R

            if name_list[1] in family and name_list[len(name_list) - 1] in family and name_list[0] in family:
                penalty += PENALTY_VALUE_FAMILY_G_R

        if penalty <= PENALTY_VALUE_FAMILY:
            return 0
        return penalty - PENALTY_VALUE_FAMILY

    def add_bi_connections(self, name1, name2, value):
        self.add_connections(name1, name2, value)
        self.add_connections(name2, name1, value)

    def add_family_value(self, members, value, value2):
        if len(members) > 2:
            self.add_bi_connections(members[0], members[1], value)
        for cnt_o in range(2, len(members)):
            self.add_bi_connections(members[0], members[cnt_o], value)
            self.add_bi_connections(members[1], members[cnt_o], value)
            for cnt_i in range(2, cnt_o):
                self.add_bi_connections(members[cnt_o], members[cnt_i], value2)

    def add_family_values(self, families, value, value2):
        for family in families.keys():
            if not self.ignore_comment_key(family):
                self.add_family_value(families[family], value, value2)

    def add_former_gifts(self, these_cost: int, givers: Dict[str, str], bidirectional=False):
        for giver in givers.keys():
            if (not self.ignore_comment_key(giver)
                    and not self.ignore_person(giver)
                    and not self.ignore_comment_key(givers[giver])
                    and not self.ignore_person(givers[giver])):
                if bidirectional:
                    self.add_bi_connections(giver, givers[giver], float(these_cost))
                else:
                    self.add_connections(giver, givers[giver], float(these_cost))

    def add_costs(self, costs, bidirectional=False):
        for cost_key in costs.keys():
            if not self.ignore_comment_key(cost_key):
                pairs = costs[cost_key]
                for key in pairs.keys():
                    if not self.ignore_comment_key(key):
                        if bidirectional:
                            self.add_bi_connections(pairs[key][0], pairs[key][1], cost_key)
                        else:
                            self.add_connections(pairs[key][0], pairs[key][1], cost_key)

    def print_connection_dict(self):
        for key in self.connections.keys():
            print(key, self.connections[key])


    def build_cost_matrix(self,
                          people_list: List[str]) -> List[List[int]]:
        """
        Convert the connected_values dictionary into a square cost matrix
        where matrix[i][j] is the cost between people_list[i] and people_list[j].
        Missing edges get a large default cost.
        """
        n = len(people_list)
        matrix = [[0] * n for _ in range(n)]

        for i, person_i in enumerate(people_list):
            for j, person_j in enumerate(people_list):
                if i == j:
                    matrix[i][j] = BAD_CONNECT_COST  # can't connect to self
                else:
                    # Look up cost if it exists
                    cost = self.connections.get(person_i, {}).get(person_j)
                    if cost is None:
                        # Missing connection → treat as never been used
                        matrix[i][j] = 0
                    else:
                        matrix[i][j] = int(cost)

        return matrix

    def get_random_list_of_people(self) -> List[str]:
        first_person = random.choice(list(self.connections.keys()))
        people_list: List = [first_person]
        for key in self.connections.keys():
            if key not in people_list:
                people_list.append(key)
        return people_list


    def load(self) -> Dict[str, Dict[str, int]]:
        # a hash of people with a hash of people with value
        # key = person
        connection_dict = {}
        #
        data = read_json_file("../data/base.json")
        self.ignore_people = data['ignore']
        self.families=data['families']

        self.add_family_values(self.families, BAD_CONNECT_COST, SIBLING_COST)
        self.add_costs(data['otherCostsBi'], True)

        file_input = read_all_year_json_files("../data")
        for year, year_dict in file_input.items():
            cost = cost_func(int(year))
            self.add_former_gifts(cost, year_dict)
        self.print_connection_dict()
        return connection_dict


if __name__ == "__main__":
    reader = Reader()
    reader.load()
