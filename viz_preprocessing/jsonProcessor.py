import json

import networkx

"""
 Example of data
 {
    "digraph": [
 {
   "vertexName": "Method public SortedDocValues select(final SortedSetDocValues values, final BitSet parentDocs, final DocIdSetIterator childDocs, int maxChildren) throws IOException  (MultiValueMode.java)",
   "children": [
     {
       "name": "Method public BinaryDocValues select(final SortedBinaryDocValues values, final BytesRef missingValue)  (MultiValueMode.java)"
     }
   ],
   "comment": "\n     * Return a {@link SortedDocValues} instance that can be used to sort root documents\n     * with this mode, the provided values and filters for root/inner documents.\n     *\n     * For every root document, the values of its inner documents will be aggregated.\n     *\n     * Allowed Modes: MIN, MAX\n     *\n     * NOTE: Calling the returned instance on docs that are not root docs is illegal\n     *       The returned instance can only be evaluate the current and upcoming docs\n     ",
   "vertexLabel": "SortedDocValues select()"
 },
 {
   "vertexName": "Method public String[] ignoreIndexSettings()  (RestoreSnapshotRequest.java)",
   "children": [
     {
       "name": "Method public RestoreSnapshotRequest ignoreIndexSettings(List<String> ignoreIndexSettings)  (RestoreSnapshotRequest.java)"
     }
   ],
   "comment": "\n     * Returns the list of index settings and index settings groups that shouldn't be restored from snapshot\n     ",
   "vertexLabel": "String[] ignoreIndexSettings()"
 },
 ...
 """


class AbstractJsonProcessor:
    def apply(self, filepath):
        pass


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
            return directed_graph, components
