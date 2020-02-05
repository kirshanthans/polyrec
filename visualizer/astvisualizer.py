import graphviz as gv
import subprocess
import numbers
import re
from uuid import uuid4 as uuid
import optparse
import sys

def main(args):
    parsers = {
        "pyast": generate_pyast,
        "lib2to3": generate_lib2to3_ast,
        "jinja2": generate_jinja2_ast,
    }

    optparser = optparse.OptionParser(usage="astvisualizer.py [options] [string]")
    optparser.add_option("-f", "--file",
                      help="Read a code snippet from the specified file")
    optparser.add_option("-l", "--label",
                      help="The label for the visualization")
    optparser.add_option("-p", "--parser", type="choice", choices=list(parsers.keys()),
                      help="The parser to use in order to parse the input tree")
    optparser.set_default("parser", "pyast")

    options, args = optparser.parse_args(args)
    if options.file:
        with open(options.file) as instream:
            code = instream.read()
        label = options.file
    elif len(args) == 2:
        code = args[1] + "\n"
        label = "<code read from command line parameter>"
    else:
        print("Expecting Python code on stdin...")
        code = sys.stdin.read()
        label = "<code read from stdin>"
    if options.label:
        label = options.label

    generate_ast = parsers[options.parser]
    code_ast = generate_ast(code)

    renderer = GraphRenderer()
    renderer.render(code_ast, label=label)


def generate_lib2to3_ast(code):
    from lib2to3.pgen2.driver import Driver
    from lib2to3.pgen2 import token as pgen2_token
    from lib2to3.pygram import python_symbols, python_grammar
    from lib2to3 import pytree
    from io import StringIO

    token_types = list(python_symbols.__dict__.items())
    token_types += list(pgen2_token.__dict__.items())

    def transform_ast(ast):
        transformed = {"node_type": next(n for n, t in token_types if t == ast.type)}
        if ast.children:
            transformed["children"] = [transform_ast(child) for child in ast.children]
        if isinstance(ast, pytree.Leaf):
            if ast.value != "":
                transformed["value"] = ast.value
            if ast._prefix != "":
                transformed["prefix"] = ast._prefix
        return transformed

    driver = Driver(python_grammar, convert=pytree.convert)
    return transform_ast(driver.parse_stream(StringIO(code)))


def generate_pyast(code):
    import ast
    def transform_ast(code_ast):
        if isinstance(code_ast, ast.AST):
            node = {to_camelcase(k): transform_ast(getattr(code_ast, k)) for k in code_ast._fields}
            node['node_type'] = to_camelcase(code_ast.__class__.__name__)
            return node
        elif isinstance(code_ast, list):
            return [transform_ast(el) for el in code_ast]
        else:
            return code_ast

    return transform_ast(ast.parse(code))


def generate_jinja2_ast(code):
    import jinja2

    def transform_ast(ast):
        if isinstance(ast, jinja2.nodes.Node):
            transformed = {k: transform_ast(getattr(ast, k)) for k in ast.fields + ast.attributes if k != "environment"}
            transformed["node_type"] = ast.__class__.__name__
            return transformed
        elif isinstance(ast, list):
            return [transform_ast(el) for el in ast]
        else:
            return ast

    env = jinja2.Environment()
    return transform_ast(env.parse(code))


def to_camelcase(string):
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()


class GraphRenderer:
    """
    this class is capable of rendering data structures consisting of
    dicts and lists as a graph using graphviz
    """

    graphattrs = {
        'labelloc': 't',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'margin': '0',
    }

    nodeattrs = {
        'color': 'white',
        'fontcolor': 'white',
        'style': 'filled',
        'fillcolor': '#006699',
    }

    edgeattrs = {
        'color': 'white',
        'fontcolor': 'white',
    }

    _graph = None
    _rendered_nodes = None
    _max_label_len = 100


    @staticmethod
    def _escape_dot_label(str):
        return str.replace("\\", "\\\\").replace("|", "\\|").replace("<", "\\<").replace(">", "\\>")


    def _shorten_string(self, string):
        if len(string) > self._max_label_len - 3:
            halflen = int((self._max_label_len - 3) / 2)
            return string[:halflen] + "..." + string[-halflen:]
        return string


    def _render_node(self, node):
        if isinstance(node, (str, numbers.Number)) or node is None:
            node_id = uuid()
        else:
            node_id = id(node)
        node_id = str(node_id)

        if node_id not in self._rendered_nodes:
            self._rendered_nodes.add(node_id)
            if isinstance(node, dict):
                self._render_dict(node, node_id)
            elif isinstance(node, list):
                self._render_list(node, node_id)
            else:
                self._graph.node(node_id, label=self._escape_dot_label(self._shorten_string(repr(node))))

        return node_id


    def _render_dict(self, node, node_id):
        self._graph.node(node_id, label=node.get("node_type", "[dict]"))
        for key, value in node.items():
            if key == "node_type":
                continue
            child_node_id = self._render_node(value)
            self._graph.edge(node_id, child_node_id, label=self._escape_dot_label(key))


    def _render_list(self, node, node_id):
        self._graph.node(node_id, label="[list]")
        for idx, value in enumerate(node):
            child_node_id = self._render_node(value)
            self._graph.edge(node_id, child_node_id, label=self._escape_dot_label(str(idx)))


    def render(self, data, *, label=None):
        # create the graph
        graphattrs = self.graphattrs.copy()
        if label is not None:
            graphattrs['label'] = self._escape_dot_label(label)
        graph = gv.Digraph(graph_attr = graphattrs, node_attr = self.nodeattrs, edge_attr = self.edgeattrs)

        # recursively draw all the nodes and edges
        self._graph = graph
        self._rendered_nodes = set()
        self._render_node(data)
        self._graph = None
        self._rendered_nodes = None

        # display the graph
        graph.view()

if __name__ == '__main__':
    main(sys.argv)
