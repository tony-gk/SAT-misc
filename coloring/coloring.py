import distinctipy
from pysat.formula import CNF
from pysat.formula import IDPool
from pysat.solvers import Solver
from pyvis.network import Network
import itertools as it


def exactly_one_of(cnf: CNF, vars):
    cnf.append(vars)
    for comb in it.combinations(vars, 2):
        cnf.append([-el for el in comb])


def format_var(i, j):
    return f'{i}-{j}'


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*[int(x * 255) for x in rgb])


if __name__ == '__main__':

    with open('coloring.txt', 'r') as f:
        num_colors = int(f.readline())
        edges = []
        for line in f.read().splitlines():
            edge_nodes = line.split()
            if len(edge_nodes) != 2:
                raise Exception(f"Unexpected number of nodes in line '{line}'")
            edges.append([int(node) for node in edge_nodes])

    nodes = set([node for edge in edges for node in edge])

    cnf = CNF()
    vpool = IDPool()

    # each node must be colored with one of the colors
    for node in nodes:
        exactly_one_of(cnf, [vpool.id(format_var(node, color)) for color in range(num_colors)])
    # adjacent nodes must be of different colors
    for (source, to) in edges:
        for color in range(num_colors):
            src_color = vpool.id(format_var(source, color))
            to_color = vpool.id(format_var(to, color))
            cnf.append([-src_color, -to_color])

    model = None
    with Solver(bootstrap_with=cnf, name='cadical') as solver:
        print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')
        if solver.get_model() is not None:
            model = [vpool.obj(x) for x in solver.get_model() if x > 0]
            print('and the model is:', model)
        print(solver.accum_stats())

    g = Network()
    g.add_nodes(list(nodes), label=[str(val) for val in nodes])

    for (source, to) in edges:
        g.add_edge(source, to)

    if model is not None:
        colors = distinctipy.get_colors(num_colors)
        for var in model:
            node, color_i = [int(val) for val in var.split('-')]
            g.get_node(node)['color'] = rgb_to_hex(colors[color_i])

    g.toggle_physics(True)
    g.show('coloring.html')
