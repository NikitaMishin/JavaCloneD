import json
import os
import re

from viz_preprocessing.jsonProcessor import JsonProcessor, JsonProcessorGroupDuplicate
from viz_preprocessing.worddiff import replace_comment_stars, \
    markup_with_diff_mode


def escape(text):
    import html
    return html.escape(text)


def obj_dict(obj):
    return obj.__dict__


def source_nodes_ids(component):
    def is_empty(iterator):
        try:
            next(iterator)
            return False
        except StopIteration:
            return True

    return [index for index in component.nodes() if is_empty(component.predecessors(index))]


class StorageModifier:

    def __init__(self, workdir):
        self.workdir = workdir

    def save_page(self, name, data) -> str:
        path = os.path.join(self.workdir, name)
        with open(path, 'w') as f_stream:
            f_stream.write(data)
        print('Saved/Updated file: ' + path)
        return path

    def remove_page(self, name):
        os.remove(os.path.join(self.workdir, name))
        print('Removed' + os.path.join(self.workdir, name))

    def remove_storage(self):
        pass


class BackendHandler:

    def __init__(self, working_file, renderer, page_name):
        self.main_page_name = page_name
        self.working_file = working_file
        self.renderer = renderer
        # TODO
        self.graph, self.strongly_connected_components = JsonProcessorGroupDuplicate().apply(working_file)
        self.storage_modifier = StorageModifier(os.path.dirname(working_file))

    def save_page(self, page, data_name):
        self.storage_modifier.save_page(self.main_page_name, page)
        self.storage_modifier.save_page(data_name, self.form_data())

    def render_page(self) -> str:
        main = self.renderer.render(self.strongly_connected_components)
        return main

    # BELOW IS BACKEND API

    def form_data(self):
        data = {}
        for i in range(len(self.strongly_connected_components)):
            src_data, source_nodes_idx, graph = self.trigger_load_component(i)
            mark = {}
            for n in self.strongly_connected_components[i]:
                mark[n] = self.trigger_load_html_markup_display(i, n)
            data[i] = {
                'src_data': src_data,
                'source_nodes_idx': source_nodes_idx,
                'graph': graph,
                'markups': mark
            }

        return json.dumps(data, default=obj_dict)

    def trigger_load_component(self, idx):
        """
        This method triggers by frontend in order to switch currently displayed tree.
        After trigger this code call initialization of new tree by passing data to frontend
        :param idx:
        :return:
        """
        component = self.strongly_connected_components[idx]
        tree = [{
            'backendId': n, 'children': list(component.successors(n)),
            'title': extract_pretty_name(component.nodes[n]['name']),
            'folder': True if list(component.successors(n)) != [] else False,
            'text': component.nodes[n]['text']
        } for n in component.nodes()]

        def get_label_name(name):
            max_len = 50
            escaped_pretty = escape(extract_pretty_name(name))
            if len(escaped_pretty) < max_len:
                return escaped_pretty
            else:
                return escaped_pretty[:max_len] + '...'

        graph = {
            'nodes': [{'id': n, 'name': get_label_name(component.nodes[n]['name'])} for n in component.nodes()
                      ],
            'links': [{'source': i, 'target': j} for (i, j) in component.edges]
        }

        return tree, source_nodes_ids(component), graph

    def trigger_load_html_markup_display(self, tree_id, node_id):
        """

        :param tree_id:
        :param node_id:
        :return:
        """
        # pre_wrapper = lambda text: text.replace('&lt;pre&gt;', '<pre>&lt;pre&gt;').replace('&lt;/pre&gt;',
        #                                                                                    '&lt;/pre&gt;</pre>')
        pre_wrapper = lambda text: text

        def get_markups(nodes, fr, to):
            # TODO about <> in sravnenie
            text_from, text_to = nodes[fr]['text'], nodes[to]['text']
            sign_from, sign_to = nodes[fr]['name'], nodes[to]['name']
            cleared_from = replace_comment_stars(text_to)
            cleared_to = replace_comment_stars(text_from)
            return {
                'signature_from': escape(sign_from),
                'signature_to': escape(sign_to),
                'with_variation': pre_wrapper(markup_with_diff_mode(cleared_to, cleared_from)),
                'no_highlight': pre_wrapper(escape(cleared_from))
            }

        def get_markup_for_selected(nodes, idx):
            return {
                'signature': nodes[idx]['name'],
                'body': pre_wrapper(escape(replace_comment_stars(nodes[idx]['text'])))
            }

        comp = self.strongly_connected_components[tree_id]
        children_nodes, parent_nodes = comp.successors(node_id), comp.predecessors(node_id)

        childrens = [{'backendId': idx, 'markup': get_markups(comp.nodes, node_id, idx)} for idx in children_nodes]
        parents = [{'backendId': idx, 'markup': get_markups(comp.nodes, node_id, idx)} for idx in parent_nodes]
        current = {'backendId': node_id, 'markup': get_markup_for_selected(comp.nodes, node_id)}
        return {
            'parents': parents,
            'childrens': childrens,
            'current': current
        }


def extract_pretty_name(name: str, language='Java'):
    return name
    try:
        # print(name)
        catch_source = r'\(\S+\.java\)'
        class_name = re.search(catch_source, name).group(0)
        tokens = name.split()
        if language == 'Java':
            text_type = tokens[0]
            if text_type == 'Method':
                method_name = re.search(r'\w+\(', name).group(0)
                return ' '.join([text_type, method_name[0:-1], class_name])
            elif text_type == 'Interface':
                return name
            elif text_type == 'Class':
                return ' '.join([text_type, class_name[1: -5], class_name])
            elif text_type == 'Field':
                return name
            elif text_type == 'Package':
                return name
            else:
                return name
    except:
        # TODO is this possible?
        return name
