import html
from viz_preprocessing.server import extract_pretty_name
from flask import render_template


class AbstractRenderer:
    pass


class GraphRenderer:
    """
    Render page for specified components

    """

    def render(self, components) -> (str, [(str, str)]):
        ids = [index for index, component in enumerate(components, start=0)]
        main_frame_html = self.render_main_frame(components, ids)
        return main_frame_html

    def render_main_frame(self, components, ids):
        def get_li_name(component):
            import functools

            def parents(node_id):
                return sum(1 for _ in component.predecessors(node_id))

            def compare(item1, item2):
                res = item1[1] - item2[1]
                if res == 0:
                    return item1[2] - item2[2]
                return res

            # print(sorted([(a, b, parents(a)) for (a, b) in component.degree], key=functools.cmp_to_key(compare),
            #              reverse=True))
            a = sorted([(a, b, parents(a)) for (a, b) in component.degree], key=functools.cmp_to_key(compare),
                       reverse=True)
            return html.escape(extract_pretty_name(component.nodes[a[0][0]]['name']))

        return render_template('main_frame_html.html',
                               groups=[{'id': idx, 'name': get_li_name(component)} for (component, idx) in
                                       zip(components, ids)]
                               )

    def source_nodes_ids(self, component):
        def is_empty(iterator):
            try:
                next(iterator)
                return False
            except StopIteration:
                return True

        return [index for index in component.nodes() if not is_empty(component.predecessors(index))]
