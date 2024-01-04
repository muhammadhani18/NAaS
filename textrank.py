import sys
from collections import defaultdict
#TextRank is an unsupervised algorithm used for keyword extraction in natural language processing. It is based on the concept of PageRank, which is widely used in web search engines. TextRank treats words or phrases as nodes in a graph and establishes edges based on co-occurrence within a context window. The algorithm iteratively updates node weights until convergence, and the final weights indicate the importance of words or phrases. Keywords are then extracted based on the highest weights.
#Nodes: TextRank, unsupervised, algorithm, keyword, extraction, natural language processing, PageRank, concept, web search engines, words, phrases, graph, edges, co-occurrence, context window, iteratively, updates, node weights, convergence, final weights, importance.
#Edges: (TextRank, unsupervised), (TextRank, algorithm), (algorithm, keyword), ...
#TextRank: 0.15, unsupervised: 0.12, algorithm: 0.20, keyword: 0.18, extraction: 0.16, ...
#algorithm, TextRank, keyword, extraction, node weights.
#new_weight(node) = (1 - d) + d * (sum(weight(neighbor) / out_degree(neighbor)) for neighbor in neighbors)
#The update is based on the weights of neighboring nodes and the number of outgoing edges from each node.


class TextrankGraph:
    '''textrank graph'''
    def __init__(self):
        self.graph = defaultdict(list)
        self.d = 0.85 # damping coefficient, usually is .85
        self.min_diff = 1e-5 # convergence threshold
        self.steps = 1000 # iteration steps

    def addEdge(self, start, end, weight):
        """Add edge between node"""
        self.graph[start].append((start, end, weight))
        self.graph[end].append((end, start, weight))

    def rank(self):
        """Rank all nodes"""
        weight_deafault = 1.0 / (len(self.graph) or 1.0) # initialize weight
        # print("default weight",weight_deafault)
        nodeweight_dict = defaultdict(float) # store weight of node
        outsum_node_dict = defaultdict(float) # store wegiht of out nodes
        for node, out_edge in self.graph.items(): # initilize nodes weight by edges
            # node: was
            # out_edge: [('was', 'prison', 1), ('was', 'wrong', 1), ('was', 'bad', 1)]
            # print(out_edge)
            nodeweight_dict[node] = weight_deafault
            outsum_node_dict[node] = sum((edge[2] for edge in out_edge), 0.0) # if no out edge, set weight 0
        # print(nodeweight_dict)
        # print(outsum_node_dict)
        sorted_keys = sorted(self.graph.keys()) # save node name as a list for iteration
        step_dict = [0]
        for step in range(1, self.steps):
            for node in sorted_keys:
                s = 0
                # Node's weight calculation: 
                # (edge_weight/ node's number of out link)*node_weight[edge_node]
                for e in self.graph[node]:
                    s += e[2] / outsum_node_dict[e[1]] * nodeweight_dict[e[1]]
                # Update calculation: (1-d) + d*s
                nodeweight_dict[node] = (1 - self.d) + self.d * s
            step_dict.append(sum(nodeweight_dict.values()))

            if abs(step_dict[step] - step_dict[step - 1]) <= self.min_diff:
                break
        # print(step_dict)
        # min-max scale to make result in range to [0 - 1]
        min_rank, max_rank = 0, 0 # initilize max and min wegiht value
        for w in nodeweight_dict.values():
            if w < min_rank:
                min_rank = w
            if w > max_rank:
                max_rank = w

        for n, w in nodeweight_dict.items():
            nodeweight_dict[n] = (w - min_rank/10.0) / (max_rank - min_rank/10.0)
        # print(nodeweight_dict)
        return nodeweight_dict
   


class TextRank:
    """Extract keywords based on textrank graph algorithm"""
    def __init__(self):
        self.candi_pos = ['NOUN', 'PROPN', 'VERB'] 
        self.stop_pos = ['NUM', 'ADV'] 
        self.span = 5

    def extract_keywords(self, word_list, num_keywords):
        g = TextrankGraph()
        cm = defaultdict(int)
        for i, word in enumerate(word_list): # word_list = [['previous', 'ADJ'], ['rumor', 'NOUN']]
            if word[1] in self.candi_pos and len(word[0]) > 1: # word = ['previous', 'ADJ']
                for j in range(i + 1, i + self.span):
                    if j >= len(word_list):
                        break
                    if word_list[j][1] not in self.candi_pos or word_list[j][1] in self.stop_pos or len(word_list[j][0]) < 2:
                        continue
                    pair = tuple((word[0], word_list[j][0]))
                    cm[(pair)] +=  1
                    # print(pair)

        # cm = {('was', 'prison'): 1, ('become', 'prison'): 1}
        
        # print("++++",self.candi_pos)
        # print(word_list)
        # print(cm)
        for terms, w in cm.items():
            # print(terms)
            g.addEdge(terms[0], terms[1], w)
        nodes_rank = g.rank()
        nodes_rank = sorted(nodes_rank.items(), key=lambda asd:asd[1], reverse=True)
        # print(nodes_rank)
        return nodes_rank[:num_keywords]

