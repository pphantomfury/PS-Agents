import networkx as nx
from collections import deque
import heapq

# (from, to, distance_km); each road is added in both directions
roads = [
    ("Nairobi", "Thika", 42), ("Nairobi", "Limuru", 35),
    ("Nairobi", "Naivasha", 90), ("Thika", "Murang'a", 38),
    ("Murang'a", "Karatina", 55), ("Karatina", "Nyeri", 25),
    ("Karatina", "Embu", 60), ("Nyeri", "Nanyuki", 60),
    ("Naivasha", "Gilgil", 35), ("Gilgil", "Nakuru", 35),
    ("Nakuru", "Kericho", 115), ("Nakuru", "Eldoret", 155),
    ("Eldoret", "Kitale", 70), ("Eldoret", "Kakamega", 110),
    ("Kitale", "Bungoma", 70), ("Kericho", "Kisumu", 90),
    ("Kakamega", "Kisumu", 50), ("Kakamega", "Bungoma", 40),
    ("Bungoma", "Busia", 50), ("Kisumu", "Kisii", 110),
    ("Kisumu", "Busia", 100),
]

region = {
    "Nairobi": "Nairobi", "Limuru": "Nairobi",
    "Thika": "Central Highlands", "Murang'a": "Central Highlands",
    "Karatina": "Central Highlands", "Nyeri": "Central Highlands",
    "Nanyuki": "Central Highlands", "Embu": "Central Highlands",
    "Naivasha": "Rift Valley", "Gilgil": "Rift Valley",
    "Nakuru": "Rift Valley", "Kericho": "Rift Valley",
    "Eldoret": "Rift Valley", "Kitale": "Rift Valley",
    "Kisumu": "Lake Victoria Basin", "Kakamega": "Lake Victoria Basin",
    "Bungoma": "Lake Victoria Basin", "Busia": "Lake Victoria Basin",
    "Kisii": "Lake Victoria Basin",
}

# Level 0: concrete directed graph
G = nx.DiGraph()
for a, b, d in roads:
    G.add_edge(a, b, weight=d)
    G.add_edge(b, a, weight=d)
nx.set_node_attributes(G, region, "region")

print("Nodes:", G.number_of_nodes(), "Edges:", G.number_of_edges())

# Level 1: abstract graph of regions
A = nx.DiGraph()
for u, v in G.edges:
    if region[u] != region[v]:
        A.add_edge(region[u], region[v])

print("Abstract edges:", list(A.edges))

def abstract_path(start_region, goal_region):
    """BFS over regions, returns the list of regions to use."""
    frontier = deque([[start_region]])
    while frontier:
        path = frontier.popleft()
        if path[-1] == goal_region:
            return path
        for nxt in A.successors(path[-1]):
            if nxt not in path:
                frontier.append(path + [nxt])
    return None

def concrete_search(start, goal, allowed_regions):
    """Uniform-cost search restricted to the abstract plan."""
    tree_edges = []
    frontier = [(0, start, [start])]
    explored = set()
    while frontier:
        cost, city, path = heapq.heappop(frontier)
        if city == goal:
            return path, cost, tree_edges
        if city in explored:
            continue
        explored.add(city)
        for nxt in G.successors(city):
            if region[nxt] in allowed_regions and nxt not in path:
                step = G[city][nxt]["weight"]
                tree_edges.append((city, nxt, step))
                heapq.heappush(frontier, (cost + step, nxt, path + [nxt]))
    return None, None, tree_edges

def tree_to_mermaid(edges):
    lines = ["flowchart TD"]
    for a, b, w in edges:
        a_id = a.replace("'", "")
        b_id = b.replace("'", "")
        lines.append(f"  {a_id} -->|{w}| {b_id}")
    return "\n".join(lines)

start, goal = "Nairobi", "Kisumu"

plan = abstract_path(region[start], region[goal])
print("Abstract plan:", " -> ".join(plan))

path, cost, tree = concrete_search(start, goal, set(plan))
print("Concrete path:", " -> ".join(path))
print("Total cost:", cost, "km")

print("\nMermaid search tree:")
print(tree_to_mermaid(tree))