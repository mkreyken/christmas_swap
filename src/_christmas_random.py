import random
from typing import List

from src._reader import Reader, BAD_CONNECT_COST


def get_shuffled_people_list(reader: Reader):
    first_person = random.choice(list(reader.connections.keys()))
    people_list: List = [first_person]
    for key in reader.connections.keys():
        if key not in people_list:
            people_list.append(key)

    for key in range(0, len(people_list) - 2):
        rnd = random.randint(key + 1, len(people_list) - 1)
        x = people_list[key]
        people_list[key] = people_list[rnd]
        people_list[rnd] = x
    # connect first to last
    people_list.append(people_list[0])
    return people_list


def add_list_if_valid(reader, path):
    global routes
    v = reader.get_total_value(path)
    if v < BAD_CONNECT_COST:
        routes.append([v, path])


def pick_random_least(results):
    # results should come in sorted, so this collects all routes of same cost
    least = results[0][0]

    pick_routes = [results[0][1]]
    print("Shortest route: {} {} ".format(least, results[0][1]))
    for i_cnt in range(1, len(results)):
        if results[i_cnt][0] <= least:
            print("Shortest route: {} {} ".format(results[i_cnt][0], results[i_cnt][1]))
            pick_routes.append(results[i_cnt][1])
    # give some random results from above
    rnd_pick = random.randint(0, len(pick_routes) - 1)
    print(" Picked: {} ".format(results[rnd_pick]))
    rnd_pick = random.randint(0, len(pick_routes) - 1)
    print(" Picked: {} ".format(results[rnd_pick]))
    rnd_pick = random.randint(0, len(pick_routes) - 1)
    print(" Picked: {} ".format(results[rnd_pick]))
    return results[rnd_pick][1]

global routes
def main(attempts:int):
    global routes
    reader = Reader()
    reader.load()

    routes = []

    # 100 random trials without broken penalties
    for rnd_shuffle_cnt in range(0, attempts):
        people = get_shuffled_people_list(reader)
        add_list_if_valid(reader,people)

    routes.sort()
    if len(routes) == 0:
        print("FAIL!")
        exit(0)

    people = pick_random_least(routes)

    print("total cost = {}".format(reader.get_total_value(people, True)))
    print("family pairing giving= {}".format(reader.check_pairing(people)))

    for i in range(1, len(people)):
        print("\"{}\" : \"{}\",".format(people[i - 1], people[i]))


if __name__ == "__main__":
    main(20000)
