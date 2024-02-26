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

    def create_nodes_and_edges(self, nodes, edges):
        with self.driver.session(database=self.db_name) as session:
            session.write_transaction(self._create_nodes_and_edges_tx, nodes, edges)

    @staticmethod
    def _create_nodes_and_edges_tx(tx, nodes, edges):
        # Erstellen aller Knoten in einem Batch
        query_create_nodes = "UNWIND $nodes AS node CREATE (:Node {id: node})"
        tx.run(query_create_nodes, nodes=nodes)

        # Erstellen aller Kanten in einem Batch
        query_create_edges = """
        UNWIND $edges AS edge
        MATCH (source:Node {id: edge.source}), (target:Node {id: edge.target})
        CREATE (source)-[:CONNECTS {weight: edge.weight}]->(target)
        """
        tx.run(query_create_edges, edges=edges)


def assign_random_coordinates(G, scale=100):
    positions = {}
    for node in G.nodes():
        positions[node] = (random.uniform(0, scale), random.uniform(0, scale))
    return positions




def create_and_store_graph(Knoten):
    n = Knoten
    p = 0.3

    G = nx.erdos_renyi_graph(n, p)
    for (u, v) in G.edges():
        G.edges[u, v]['weight'] = random.randint(1, 20)

    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "password"  # Use a placeholder or secure method to handle the password
    db_name = "neo4j"

    db_driver = GraphDatabaseDriver(uri, user, password, db_name)

    # Prepare nodes and edges for batch creation
    nodes = list(G.nodes())
    edges = [(source, target, G.edges[source, target]['weight']) for source, target in G.edges()]

    # Create nodes and edges in batch
    db_driver.create_nodes_and_edges(nodes, edges)

    positions = assign_random_coordinates(G)

    # Plot the graph
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos=positions, with_labels=True, node_size=700, node_color='skyblue')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels)
    plt.axis('off')
    plt.show()

    return db_driver, G, positions

