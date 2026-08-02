"""
CDepth first search algorythm with penalties for connection in results

The randomness is in how the list of names is initially prepared, otherwise this is deterministic (same inputs = same outputs)

"""
from collections import defaultdict
from typing import Tuple, List

from src._reader import BAD_CONNECT_COST, Reader


def build_adj_list(edges):
    adj = defaultdict(list)
    for u, v, cost in edges:
        adj[u].append((v, cost))
        adj[v].append((u, cost))
    return adj


def dfs_chain(adj, start):
    visited = set()
    chain = []

    def dfs(node):
        visited.add(node)
        chain.append(node)
        for neighbor in adj[node]:
            if neighbor not in visited:
                dfs(neighbor)

    dfs(start)
    return chain


def find_leaf(adj):
    for node, neighbors in adj.items():
        if len(neighbors) == 1:
            return node
    return next(iter(adj))  # fallback


def find_chain(adj):
    # Find a leaf (degree 1)
    start = None
    for node, neighbors in adj.items():
        if len(neighbors) == 1:
            start = node
            break

    # Walk the tree
    chain = []
    visited = set()
    current = start

    while current is not None:
        chain.append(current)
        visited.add(current)

        # pick the next unvisited neighbor
        next_node = None
        for neighbor in adj[current]:
            if neighbor not in visited:
                next_node = neighbor
                break

        current = next_node

    return chain


def chain_to_names(chain, people_list):
    return [people_list[i] for i in chain]


from heapq import heappush, heappop


def dfs_min_chain(reader, min_cost, cost_matrix, people_list):
    n = len(cost_matrix)

    # Priority queue: (total_cost, path_list)
    pq: List[Tuple[int, List[int]]] = []
    heappush(pq, (0, [0]))  # start at node 0

    best_cost = float('inf')
    best_value = BAD_CONNECT_COST * 10
    best_path = None

    while pq:
        cost, path = heappop(pq)
        last = path[-1]

        if cost >= best_cost:
            continue

        # If path includes all nodes → we found a full chain
        if len(path) == n:
            wrapped_path = path + [path[0]]
            chain_names = [people_list[i] for i in wrapped_path]
            total_value = reader.get_total_value(chain_names)

            if total_value < best_value:
                best_value = total_value
                best_path = wrapped_path
                if best_value < min_cost:
                    break
            continue

        # Expand BFS: try all unvisited neighbors
        for nxt in range(n):
            if nxt in path:
                continue

            edge_cost = cost_matrix[last][nxt]

            # Stop exploring this branch if cost is 10000
            if edge_cost >= BAD_CONNECT_COST:
                continue

            new_cost = cost + edge_cost
            new_path = path + [nxt]

            heappush(pq, (new_cost, new_path))

    if best_path is None:
        return None, None

    # Convert indices → names
    chain_names = [people_list[i] for i in best_path]
    return chain_names, best_cost


def main():
    reader = Reader()
    reader.load()
    people_list = reader.get_random_list_of_people()
    cost_matrix = reader.build_cost_matrix(people_list)
    # stop when you get something small !
    chain, cost = dfs_min_chain(reader, 50, cost_matrix, people_list)

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
