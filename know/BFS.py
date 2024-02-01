from queue import Queue
import json
from graph_show import GraphShow
class GraphProcessor:
    def __init__(self, json_file):
        self.graph = self.build_graph_from_json(json_file)
    def build_graph_from_json(self, json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
        graph = {}
        for node in data['edges']:
            node_id = node.get('id')
            graph[node_id] = []
        for edge in data['nodes']:
            from_node = edge.get('from')
            to_node = edge.get('to')
            if from_node is not None and to_node is not None:
                if from_node not in graph:
                    graph[from_node] = []
                graph[from_node].append(to_node)
        return graph
    def bfs_related_nodes(self, keyword):
        visited = set()
        result = []
        re = read_json_file("query_graph.json")
                
        for start_node in self.graph:
            if str(keyword) in str(start_node) and start_node not in visited:
                queue = Queue()
                queue.put((start_node, 0))  # Tuple (node, distance)
                visited.add(start_node)
                re = read_json_file("query_graph.json")
                
                while not queue.empty():
                    current_node, distance = queue.get()
                    result.append(current_node)

                    for edge in re['edges']:
                        if current_node == edge['id']:
                            edge['distance'] = distance

                    for neighbor in self.graph.get(current_node, []):
                        if neighbor not in visited:
                            queue.put((neighbor, distance + 1))
                            visited.add(neighbor)

                            for edge in re['edges']:
                                if edge['id'] == neighbor:
                                    edge['distance'] = distance + 1

        with open('query_graph.json', 'w') as json_file:
            json.dump(re, json_file, indent=2)
        result_one = {}
        re=read_json_file("query_graph.json")

        for edge in re['edges']:
            if edge['distance'] >0:
                result_one[edge['label']] = edge['distance']

        if len(result_one)<1:
            return None
        final_distance = dict(sorted(result_one.items(), key=lambda item: item[1]))
        
        return final_distance
    
    def get_labels_by_ids(self, node_ids):
        labels = []
        for node_id in node_ids:
            for edge in self.graph:
                if 'id' in edge and edge['id'] == node_id:
                    labels.append(edge['label'])
                    break
        return labels
    
def read_json_file(file_path):
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                return json_data
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except json.JSONDecodeError:
            return f"Invalid JSON format in file: {file_path}"

def find_matching_id(json_data,keyw):
    nodes_id=json_data['edges']
    # print(nodes_id)
    for i in nodes_id:
        # print(i['label'])
        if i['label']==keyw:
            return i['id']
if __name__=="__main__":
    processor = GraphProcessor('graph_data.json')
    re=read_json_file("graph_data.json")
    ids=processor.bfs_related_nodes(find_matching_id(re,'XYZ Corporation')) 
    print(ids)
    # cal=find_matching_id(re,"AI")
    # distance={}
    # for i in ids:
    #     distance[i]=abs(i-cal)
    # # print(distance)
    # match_lab=[]
    # final_distance={}
    # for i in re['edges']:
    #     if i['id'] in ids:
    #         x=distance[int(i['id'])]
    #         final_distance[i['label']]=x
    #        # print("distance from this keyword",i['id'])
    #         lab=i['label']
    #         match_lab.append(lab)
    # final_distance=dict(sorted(final_distance.items(), key=lambda item: item[1]))
    # print(final_distance)
   