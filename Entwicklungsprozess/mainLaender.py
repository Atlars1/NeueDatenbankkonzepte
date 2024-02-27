import networkx as nx
import random
from neo4j import GraphDatabase
import matplotlib.pyplot as plt

class ProgressBar:
    def __init__(self, total):
        self.total = total
        self.current = 0

    def update(self, step=1):
        self.current += step
        percent = (self.current / self.total) * 100
        bar = '#' * int(percent) + '-' * (100 - int(percent))
        print(f"\r[{bar}] {percent:.2f}%", end="")

    def finish(self):
        print()

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
    def find_shortest_path(G, positions, start_node, end_node, progress_bar=None):
        if progress_bar:
            progress_bar.update()  # Start the progress

        path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')
        length = nx.shortest_path_length(G, source=start_node, target=end_node, weight='weight')

        if progress_bar:
            progress_bar.update()  # Update the progress after finding the path

        GraphUtils.plot_path(G, positions, path)
        return path, length

    @staticmethod
    def plot_path(G, positions, path):
        plt.figure(figsize=(10, 8))
        color_map = {1: 'skyblue', 2: 'green', 3: 'orange'}

        # Farben für alle Knoten basierend auf ihrem Typ
        all_node_colors = [color_map[G.nodes[node]['type']] for node in G.nodes()]

        # Zeichne alle Knoten mit ihren Typ-Farben
        nx.draw(G, pos=positions, with_labels=True, node_size=700, node_color=all_node_colors)

        # Zeichne Knoten und Kanten des Pfades in einer anderen Farbe (z.B. Rot)
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_nodes(G, pos=positions, nodelist=path, node_color='red', node_size=700)
        nx.draw_networkx_edges(G, pos=positions, edgelist=path_edges, edge_color='red', width=2)

        # Zeichne Kantenbeschriftungen
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels)

        plt.axis('off')
        plt.show()



class GraphInterface:
    def __init__(self):
        self.db_driver = None
        self.G = None
        self.positions = None
        self.original_weights = {}

    def create_and_store_graph(self, n, p=0.5):
        self.G = nx.erdos_renyi_graph(n, p)

        progress_bar = ProgressBar(total=n + len(self.G.edges()))

        for node in self.G.nodes():
            # Zusätzliche Zahl von 1 bis 3 für jeden Knoten
            self.G.nodes[node]['type'] = random.randint(1, 3)

        for (u, v) in self.G.edges():
            self.G.edges[u, v]['weight'] = random.randint(1, 20)
            progress_bar.update()

        uri = "neo4j://localhost:7687"
        user = "neo4j"
        password = "dklrtenzu011001010101"
        db_name = "neo4j"

        self.db_driver = GraphDatabaseDriver(uri, user, password, db_name)
        for node in self.G.nodes():
            self.db_driver.create_node(node)
            progress_bar.update()

        for source, target, data in self.G.edges(data=True):
            self.db_driver.create_edge(source, target, data['weight'])
            progress_bar.update()

        progress_bar.finish()

        self.positions = GraphUtils.assign_random_coordinates(self.G)
        self.plot_graph()

    def plot_graph(self):
            plt.figure(figsize=(10, 8))
            color_map = {1: 'skyblue', 2: 'green', 3: 'orange'}
            node_colors = [color_map[self.G.nodes[node]['type']] for node in self.G]
            nx.draw(self.G, pos=self.positions, with_labels=True, node_size=700, node_color=node_colors)
            edge_labels = nx.get_edge_attributes(self.G, 'weight')
            nx.draw_networkx_edge_labels(self.G, pos=self.positions, edge_labels=edge_labels)
            plt.axis('off')
            plt.show()


    def calculate_travel_time(self, path_length, transport_choice):
        speeds = {"1": 5, "2": 15, "3": 60, "4": 100}
        speed = speeds.get(transport_choice, 5)  # Default to walking speed if invalid choice
        time_hours = path_length / speed
        return time_hours

    def check_direct_connection(self, start_node, end_node):
        return self.G.has_edge(start_node, end_node)

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

    def temporarily_remove_node(self, node):
        for neighbor in list(self.G.neighbors(node)):
            self.original_weights[(node, neighbor)] = self.G.edges[node, neighbor]['weight']
            self.G.edges[node, neighbor]['weight'] = float('inf')

    def restore_node(self, node):
        for neighbor in list(self.G.neighbors(node)):
            self.G.edges[node, neighbor]['weight'] = self.original_weights[(node, neighbor)]
    
    def temporarily_avoid_node_type(self, node_type):
        self.original_weights = {}
        for node in self.G.nodes():
            if self.G.nodes[node]['type'] == node_type:
                for neighbor in self.G.neighbors(node):
                    self.original_weights[(node, neighbor)] = self.G.edges[node, neighbor].get('weight', 1)
                    self.G.edges[node, neighbor]['weight'] = float('inf')

    def restore_original_weights(self):
        for (node, neighbor), weight in self.original_weights.items():
            self.G.edges[node, neighbor]['weight'] = weight

    def interface_logic(self):
        print("Welcome to the Graph Pathfinding Interface!")
        transport_methods = ["1: Foot", "2: Bike", "3: Car", "4: Train"]
        print("How would you like to travel?")
        for method in transport_methods:
            print(method)
        transport_choice = input("Please choose your transport method by number (1-4): ")

        print("Do you want to avoid any node type? (1-3, enter -1 to skip): ")
        node_type_to_avoid = int(input())
        if node_type_to_avoid != -1:
            self.temporarily_avoid_node_type(node_type_to_avoid)

        print("Please enter your start and end nodes.")
        start_node = int(input("Start node: "))
        end_node = int(input("End node: "))

        avoid_node = int(input("Node to avoid (enter -1 to skip): "))

        if avoid_node != -1:
            self.temporarily_remove_node(avoid_node)

        if self.check_direct_connection(start_node, end_node):
            print(f"There is a direct connection between nodes {start_node} and {end_node}.")
        else:
            print(f"No direct connection between nodes {start_node} and {end_node}.")

        intermediate_node = int(input("Intermediate node (optional, enter -1 to skip): "))

        print("Choose your pathfinding strategy:")
        print("1: Shortest path by distance")
        print("2: Shortest path by number of nodes")
        strategy_choice = input("Please choose your strategy by number (1-2): ")

        progress_bar = ProgressBar(total=2)  # Total steps for path finding

        if strategy_choice == "1":
            if intermediate_node != -1:
                path_to_intermediate = nx.shortest_path(self.G, source=start_node, target=intermediate_node, weight='weight')
                path_from_intermediate = nx.shortest_path(self.G, source=intermediate_node, target=end_node, weight='weight')
                total_path = path_to_intermediate + path_from_intermediate[1:]
                total_length = self.calculate_path_length(total_path)
                GraphUtils.plot_path(self.G, self.positions, total_path)
                print(f"Path with intermediate node: {total_path} with total weight: {total_length}")
                travel_time = self.calculate_travel_time(total_length, transport_choice)
                print(f"Estimated travel time: {travel_time:.2f} hours")
            else:
                path, length = GraphUtils.find_shortest_path(self.G, self.positions, start_node, end_node, progress_bar)
                print(f"Shortest path by distance: {path} with total weight: {length}")
                travel_time = self.calculate_travel_time(length, transport_choice)
                print(f"Estimated travel time: {travel_time:.2f} hours")
        elif strategy_choice == "2":
            default_edge_weight = 1
            if intermediate_node != -1:
                path_to_intermediate = nx.shortest_path(self.G, source=start_node, target=intermediate_node)
                path_from_intermediate = nx.shortest_path(self.G, source=intermediate_node, target=end_node)
                total_path = path_to_intermediate + path_from_intermediate[1:]
                total_length = (len(total_path) - 1) * default_edge_weight
                GraphUtils.plot_path(self.G, self.positions, total_path)
                print(f"Path with intermediate node: {total_path}")
            else:
                path = nx.shortest_path(self.G, source=start_node, target=end_node)
                total_length = (len(path) - 1) * default_edge_weight
                GraphUtils.plot_path(self.G, self.positions, path)
                print(f"Shortest path by nodes: {path}")

            travel_time = self.calculate_travel_time(total_length, transport_choice)
            print(f"Estimated travel time: {travel_time:.2f} hours")


        progress_bar.finish()  # Finish the progress bar after finding the path

        if node_type_to_avoid != -1:
            self.restore_original_weights()

        if avoid_node != -1:
            self.restore_node(avoid_node)

    def main(self):
        self.create_and_store_graph(10)
        self.interface_logic()
        if self.db_driver:
            self.db_driver.close()

if __name__ == "__main__":
    graph_interface = GraphInterface()
    graph_interface.main()

