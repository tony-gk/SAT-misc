from pysat.formula import CNF
from pysat.solvers import Solver
import itertools as it


def varnum(i, j, k):
    return (i + 1) * 100 + (j + 1) * 10 + k


def read_sudoku(file_name):
    with open(file_name, 'r') as f:
        lines = f.read().splitlines()

        if len(lines) != 9:
            raise Exception(f'Number of line is {len(lines)}, expected 9')

        satisfied_vars = []
        for i in range(0, 9):
            if len(lines[i]) != 9:
                raise Exception(f'Length of line {i} is {len(lines[i])}, expected 9')

            for j in range(0, 9):
                if lines[i][j] != "*" and not lines[i][j].isdigit():
                    raise Exception(f'Unexpected symbol at line {i} and number {j}: {lines[i][j]}')
                if lines[i][j].isdigit():
                    satisfied_vars.append(varnum(i, j, int(lines[i][j])))
    return satisfied_vars


def exactly_one_of(cnf: CNF, vars):
    cnf.append(vars)
    for comb in it.combinations(vars, 2):
        cnf.append([-el for el in comb])


if __name__ == '__main__':
    cnf = CNF()

    satisfied = read_sudoku('sudoku.txt')
    for sat_var in satisfied:
        cnf.append([sat_var])

    for i in range(0, 9):
        for j in range(0, 9):
            exactly_one_of(cnf, [varnum(i, j, k) for k in range(1, 10)])

    for i in range(0, 9):
        for k in range(1, 10):
            exactly_one_of(cnf, [varnum(i, j, k) for j in range(0, 9)])
            exactly_one_of(cnf, [varnum(j, i, k) for j in range(0, 9)])

    for (i, j) in it.product([0, 3, 6], repeat=2):
        for k in range(1, 10):
            exactly_one_of(cnf, [varnum(i + di, j + dj, k) for (di, dj) in it.product([0, 1, 2], repeat=2)])

    with Solver(bootstrap_with=cnf) as solver:
        print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')
        model = [x for x in solver.get_model() if x > 0]
        print('and the model is:', model)
        print(solver.accum_stats())

        grid = [["*" for _ in range(0, 9)] for _ in range(0, 9)]
        for val in model:
            i = val // 100 - 1
            j = (val % 100) // 10 - 1
            k = (val % 100) % 10
            grid[i][j] = str(k)

        print("\n".join(["".join(row) for row in grid]))
