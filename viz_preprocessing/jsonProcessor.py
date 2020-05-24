import json

import networkx


class AbstractJsonProcessor:
    def apply(self, filepath):
        pass


# OUTDATED
class JsonProcessor(AbstractJsonProcessor):
    """
    Parses to networkx graph json  with structure described above
    """

    name = 'vertexName'
    text = 'comment'
    child = 'children'
    child_name = 'name'

    def apply(self, filepath) -> (networkx.DiGraph, [networkx.DiGraph]):
        with open(filepath, 'r') as f:
            data = json.load(f)['digraph']
            directed_graph = networkx.DiGraph()

            for index, vtx in enumerate(data, start=0):
                directed_graph.add_node(index, name=vtx[self.name], text=vtx[self.text])
            for i, source in enumerate(data, start=0):
                if self.child in source:
                    for destination in source[self.child]:
                        dest_name = destination[self.child_name]
                        indexes_dest = [j for j, data in directed_graph.nodes(True) if
                                        data[self.child_name] == dest_name]
                        for to in indexes_dest:
                            directed_graph.add_edge(i, to)

            components = [directed_graph.subgraph(c) for c in
                          sorted(networkx.connected_components(networkx.Graph(directed_graph)),
                                 key=len, reverse=True)]
            # uncomment to see debug if all component is asyclic
            # for comp in components:
            #     if not networkx.is_directed_acyclic_graph(comp):
            #         print('Component is circled')
            return directed_graph, components


class JsonProcessorGroupDuplicate(AbstractJsonProcessor):
    """
       Parses to networkx graph json  with structure described above
    """

    def apply(self, filepath) -> (networkx.DiGraph, [networkx.DiGraph]):
        with open(filepath, 'r') as f:
            groups = json.load(f)
            directed_graph = networkx.DiGraph()

            trees = []

            for group in groups:
                vertices = group['vertices']
                edges = group['edges']
                tree = networkx.DiGraph()
                for vertex in vertices:
                    directed_graph.add_node(vertex['id'], name=vertex['signature'], text=vertex['body'])
                    tree.add_node(vertex['id'], name=vertex['signature'], text=vertex['body'])
                for edge in edges:
                    tree.add_edge(edge['from'], edge['to'],
                                  clone=(edge['cloneInTo']['startInclusive'], edge['cloneInTo']['endExclusive']))
                    directed_graph.add_edge(edge['from'], edge['to'], clone=(
                        edge['cloneInTo']['startInclusive'], edge['cloneInTo']['endExclusive']))
                trees.append(tree)
            trees.sort(key=len, reverse=True)
            # print(trees[0].edges)
            return directed_graph, trees


class JsonProcessorPatternMatching(AbstractJsonProcessor):
    """
       Parses to pattern,text and list of positions
    """

    def apply(self, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
            text = data['text']
            pattern = data['pattern']
            clones = data['clones']
            positions = list(map(lambda x: (int(x['startInclusive']), int(x["endExclusive"])), clones))
            return pattern, text, positions


# JsonProcessorGroupDuplicate().apply('/home/nikita/PycharmProjects/untitled1/output.json')
