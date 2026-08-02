"""
Multiple Random solutions, pick the lowest cost one found

Each run produces a new result

"""

import random

from src._reader import Reader, BAD_CONNECT_COST


def pick_random_least(results):
    # results should come in sorted, so this collects all routes of same cost
    least = results[0][0]

    pick_routes = [results[0][1]]
    print("Shortest route: {} {} ".format(least, results[0][1]))
    for i_cnt in range(1, len(results)):
        if results[i_cnt][0] <= least:
            print("Shortest route: {} {} ".format(results[i_cnt][0], results[i_cnt][1]))
            pick_routes.append(results[i_cnt][1])
    if len(pick_routes) == 1:
         return pick_routes[0]

    # If multiple path's with same result:
    rnd_pick = random.randint(0, len(pick_routes) - 1)
    print(" Picked: {} ".format(pick_routes[rnd_pick]))
    return results[rnd_pick][1]

def main(attempts: int):
    reader = Reader()
    reader.load()

    routes = []

    for rnd_shuffle_cnt in range(0, attempts):
        path = reader.get_random_list_of_people()
        path.append(path[0])
        v = reader.get_total_value(path)
        if v < BAD_CONNECT_COST:
            routes.append([v, path])

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
