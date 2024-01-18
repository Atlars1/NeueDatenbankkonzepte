import networkx as nx
import random
from neo4j import GraphDatabase
import matplotlib.pyplot as plt

class GraphDatabaseDriver:
    def __init__(self, uri, user, password, db_name):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.db_name = db_name

    def close(self):
        self.driver.close()

    def create_node(self, node_id):
        with self.driver.session(database=self.db_name) as session:
            session.execute_write(self._create_node_tx, node_id)

    def create_edge(self, source, target, weight):
        with self.driver.session(database=self.db_name) as session:
            session.execute_write(self._create_edge_tx, source, target, weight)

    @staticmethod
    def _create_node_tx(tx, node_id):
        tx.run(f"CREATE (n:Node {{id: {node_id}}})")

    @staticmethod
    def _create_edge_tx(tx, source, target, weight):
        tx.run(f"MATCH (a:Node {{id: {source}}}), (b:Node {{id: {target}}}) "
               f"CREATE (a)-[:CONNECTS {{weight: {weight}}}]->(b)")

def assign_random_coordinates(G, scale=100):
    positions = {}
    for node in G.nodes():
        positions[node] = (random.uniform(0, scale), random.uniform(0, scale))
    return positions

def create_and_store_graph():
    n = int(input("Geben Sie die Anzahl der Knoten ein: "))
    p = float(input("Geben Sie die Wahrscheinlichkeit für Kanten ein (0-1): "))

    G = nx.erdos_renyi_graph(n, p)
    for (u, v) in G.edges():
        G.edges[u, v]['weight'] = random.randint(1, 20)

    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "dklrtenzu011001010101"
    db_name = "neo4j"

    db_driver = GraphDatabaseDriver(uri, user, password, db_name)
    for node in G.nodes():
        db_driver.create_node(node)
    for source, target, data in G.edges(data=True):
        db_driver.create_edge(source, target, data['weight'])

    positions = assign_random_coordinates(G)

    # Plot the graph
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos=positions, with_labels=True, node_size=700, node_color='skyblue')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels)
    plt.axis('off')
    plt.show()

    return db_driver, G, positions

def find_shortest_path(db_driver, start_node, end_node):
    with db_driver.driver.session(database=db_driver.db_name) as session:
        result = session.run("MATCH (start:Node {id: $start_id}), (end:Node {id: $end_id}) "
                             "CALL apoc.algo.dijkstra(start, end, 'CONNECTS', 'weight') YIELD path, weight "
                             "RETURN path, weight",
                             start_id=start_node, end_id=end_node)
        return result.single()

def find_and_display_shortest_path(db_driver, G, positions):
    start_node = int(input("Geben Sie den Startknoten ein: "))
    end_node = int(input("Geben Sie den Zielknoten ein: "))

    path_result = find_shortest_path(db_driver, start_node, end_node)

    if path_result:
        print("Shortest Path: ", path_result["path"])
        print("Total Weight: ", path_result["weight"])

        path_nodes = [node["id"] for node in path_result["path"].nodes]
        path_edges = list(zip(path_nodes, path_nodes[1:]))

        plt.figure(figsize=(10, 8))
        nx.draw(G, pos=positions, with_labels=True, node_size=700, node_color='skyblue')
        nx.draw_networkx_nodes(G, pos=positions, nodelist=path_nodes, node_color='red', node_size=700)
        nx.draw_networkx_edges(G, pos=positions, edgelist=path_edges, edge_color='red', width=2)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels)
        plt.axis('off')
        plt.show()
    else:
        print("Kein Pfad gefunden.")

if __name__ == "__main__":
    db_driver, G, positions = create_and_store_graph()
    find_and_display_shortest_path(db_driver, G, positions)
    db_driver.close()
