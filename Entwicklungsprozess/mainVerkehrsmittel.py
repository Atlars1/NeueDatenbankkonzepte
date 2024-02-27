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
            session.write_transaction(self._create_node_tx, node_id)

    def create_edge(self, source, target, weight):
        with self.driver.session(database=self.db_name) as session:
            session.write_transaction(self._create_edge_tx, source, target, weight)

    @staticmethod
    def _create_node_tx(tx, node_id):
        tx.run(f"CREATE (n:Node {{id: {node_id}}})")

    @staticmethod
    def _create_edge_tx(tx, source, target, weight):
        tx.run(f"MATCH (a:Node {{id: {source}}}), (b:Node {{id: {target}}}) "
               f"CREATE (a)-[:CONNECTS {{weight: {weight}}}]->(b)")

class GraphUtils:
    @staticmethod
    def assign_random_coordinates(G, scale=100):
        positions = {}
        for node in G.nodes():
            positions[node] = (random.uniform(0, scale), random.uniform(0, scale))
        return positions

    @staticmethod
    def find_shortest_path(G, positions, start_node, end_node):
        path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')
        length = nx.shortest_path_length(G, source=start_node, target=end_node, weight='weight')
        GraphUtils.plot_path(G, positions, path)
        return path, length

    @staticmethod
    def plot_path(G, positions, path):
        plt.figure(figsize=(10, 8))
        nx.draw(G, pos=positions, with_labels=True, node_size=700, node_color='skyblue')
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_nodes(G, pos=positions, nodelist=path, node_color='red', node_size=700)
        nx.draw_networkx_edges(G, pos=positions, edgelist=path_edges, edge_color='red', width=2)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels)
        plt.axis('off')
        plt.show()

class GraphInterface:
    def __init__(self):
        self.db_driver = None
        self.G = None
        self.positions = None

    def create_and_store_graph(self, n, p=0.5):
        self.G = nx.erdos_renyi_graph(n, p)
        for (u, v) in self.G.edges():
            self.G.edges[u, v]['weight'] = random.randint(1, 20)

        uri = "neo4j://localhost:7687"
        user = "neo4j"
        password = "dklrtenzu011001010101"  # Replace with your actual password
        db_name = "neo4j"

        self.db_driver = GraphDatabaseDriver(uri, user, password, db_name)
        for node in self.G.nodes():
            self.db_driver.create_node(node)
        for source, target, data in self.G.edges(data=True):
            self.db_driver.create_edge(source, target, data['weight'])

        self.positions = GraphUtils.assign_random_coordinates(self.G)
        self.plot_graph()

    def plot_graph(self):
        plt.figure(figsize=(10, 8))
        nx.draw(self.G, pos=self.positions, with_labels=True, node_size=700, node_color='skyblue')
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos=self.positions, edge_labels=edge_labels)
        plt.axis('off')
        plt.show()

    def calculate_travel_time(self, path_length, transport_choice):
        speeds = {"1": 5, "2": 15, "3": 60, "4": 100}
        speed = speeds.get(transport_choice, 5)  # Default to walking speed if invalid choice
        time_hours = path_length / speed
        return time_hours

    def interface_logic(self):
        print("Welcome to the Graph Pathfinding Interface!")
        transport_methods = ["1: Foot", "2: Bike", "3: Car", "4: Train"]
        print("How would you like to travel?")
        for method in transport_methods:
            print(method)
        transport_choice = input("Please choose your transport method by number (1-4): ")

        print("Please enter your start and end nodes.")
        start_node = int(input("Start node: "))
        end_node = int(input("End node: "))
        intermediate_node = int(input("Intermediate node (optional, enter -1 to skip): "))

        print("Choose your pathfinding strategy:")
        print("1: Shortest path by distance")
        print("2: Shortest path by number of nodes")
        strategy_choice = input("Please choose your strategy by number (1-2): ")

        if strategy_choice == "1":
            if intermediate_node != -1:
                path_to_intermediate = nx.shortest_path(self.G, source=start_node, target=intermediate_node, weight='weight')
                path_from_intermediate = nx.shortest_path(self.G, source=intermediate_node, target=end_node, weight='weight')
                total_path = path_to_intermediate + path_from_intermediate[1:]
                total_length = self.calculate_path_length(total_path)
                GraphUtils.plot_path(self.G, self.positions, total_path)
                print(f"Path with intermediate node: {total_path} with total weight: {total_length}")
                # Calculating travel time
                travel_time = self.calculate_travel_time(total_length, transport_choice)
                print(f"Estimated travel time: {travel_time:.2f} hours")
            else:
                path, length = GraphUtils.find_shortest_path(self.G, self.positions, start_node, end_node)
                print(f"Shortest path by distance: {path} with total weight: {length}")
                # Calculating travel time
                travel_time = self.calculate_travel_time(length, transport_choice)
                print(f"Estimated travel time: {travel_time:.2f} hours")
            
            

        elif strategy_choice == "2":
            default_edge_weight = 1  # Default distance for each edge, you can adjust this value
            if intermediate_node != -1:
                path_to_intermediate = nx.shortest_path(self.G, source=start_node, target=intermediate_node)
                path_from_intermediate = nx.shortest_path(self.G, source=intermediate_node, target=end_node)
                total_path = path_to_intermediate + path_from_intermediate[1:]
                GraphUtils.plot_path(self.G, self.positions, total_path)
                print(f"Path with intermediate node: {total_path}")
                total_length = (len(total_path) - 1) * default_edge_weight
                # Calculate travel time
                travel_time = self.calculate_travel_time(total_length, transport_choice)
                print(f"Estimated travel time: {travel_time:.2f} hours")
            else:
                path = nx.shortest_path(self.G, source=start_node, target=end_node)
                GraphUtils.plot_path(self.G, self.positions, path)
                print(f"Shortest path by nodes: {path}")
                total_length = (len(path) - 1) * default_edge_weight
                # Calculate travel time
                travel_time = self.calculate_travel_time(total_length, transport_choice)
                print(f"Estimated travel time: {travel_time:.2f} hours")

        else:
            print("Invalid choice.")

    def calculate_path_length(self, path):
        length = 0
        for i in range(len(path) - 1):
            length += self.G.edges[path[i], path[i + 1]]['weight']
        return length

    def find_alternative_paths(self, original_path):
        alternative_paths = []
        for i in range(len(original_path) - 1):
            u, v = original_path[i], original_path[i + 1]

            original_weight = self.G.edges[u, v]['weight']
            self.G.edges[u, v]['weight'] = float('inf')

            try:
                new_path = nx.shortest_path(self.G, source=original_path[0], target=original_path[-1], weight='weight')
                if new_path != original_path:
                    alternative_paths.append(new_path)
            except nx.NetworkXNoPath:
                pass

            self.G.edges[u, v]['weight'] = original_weight

        return alternative_paths

    def main(self):
        self.create_and_store_graph(10)  # Create a graph with 10 nodes
        self.interface_logic()
        if self.db_driver:
            self.db_driver.close()

if __name__ == "__main__":
    graph_interface = GraphInterface()
    graph_interface.main()
