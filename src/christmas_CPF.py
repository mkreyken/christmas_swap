"""
Cheapest path first algorythm with penalties for connection in results

The randomness is in how the list of names is initially prepared, otherwise this is deterministic (same inputs = same outputs)

"""

from heapq import heappush, heappop
from typing import List, Tuple

from src._reader import Reader, BAD_CONNECT_COST


def cheapest_chain_with_penalty(
        reader: Reader,
        people_list: List[str],
        edges: List[List[int]]
) -> Tuple[List[str] | None, int]:
    n = len(people_list)
    max_cost: int = BAD_CONNECT_COST

    # Priority queue: (total_cost, chain_indices)
    pq: List[Tuple[int, List[int]]] = []
    heappush(pq, (0, [0]))  # start at person index 0

    best_chain = None
    best_cost = BAD_CONNECT_COST

    while pq:
        cost, chain = heappop(pq)  # ⭐ always the cheapest-so-far chain
        last = chain[-1]

        if cost >= max_cost:
            continue

        # full chain found
        if len(chain) == n:
            wrapped_path = chain + [chain[0]]
            chain_names = [people_list[i] for i in wrapped_path]
            total_value = reader.get_total_value(chain_names)
            if total_value < best_cost:
                best_cost = total_value
                best_chain = chain
                max_cost = best_cost
            if total_value == 0:
                break
            continue

        # expand this cheapest-so-far chain
        for nxt in range(n):
            if nxt in chain:
                continue

            new_cost = cost + edges[last][nxt]
            if new_cost >= max_cost:
                continue

            new_chain = chain + [nxt]
            new_cost += reader.get_penalties_when_last_added_idx(new_chain)
            if new_cost >= max_cost:
                continue

            heappush(pq, (new_cost, new_chain))

    if best_chain is not None:
        best_chain_names = [people_list[i] for i in best_chain]
        return best_chain_names, best_cost

    return None, int('inf')


def main():
    reader = Reader()
    reader.load()
    people_list = reader.get_random_list_of_people()
    cost_matrix = reader.build_cost_matrix(people_list)
    # stop when you get something small !
    chain, cost = cheapest_chain_with_penalty(reader, people_list, cost_matrix)

    if not chain:
        print("FAIL!")
        return

    print("Minimum-cost chain:")
    print(" -> ".join(chain))
    print("Chain cost:", cost)
    people = chain

    print("Cheapest chain:", " -> ".join(people))
    print("Total cost:", cost)

    print("total cost = {}".format(reader.get_total_value(people, True)))
    print("family pairing giving= {}".format(reader.check_pairing(people)))

    for i in range(1, len(people)):
        print("\"{}\" : \"{}\",".format(people[i - 1], people[i]))


if __name__ == "__main__":
    main()
