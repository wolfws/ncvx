from cvxpy import *
from noncvx_admm import *
import random
import numpy as np

random.seed(1)
np.random.seed(1)
# 3-SAT problem solved with non-convex ADMM
# TODO initialize z's at 0.5
EPSILON = 1e-8

# Randomly generate a feasible 3-SAT problem.
VARIABLES = 10
CLAUSES_PER_VARIABLE = 4
CLAUSES = int(VARIABLES*CLAUSES_PER_VARIABLE)

while True:
    # The 3-SAT clauses.
    A = np.zeros((CLAUSES,VARIABLES))
    b = np.zeros((CLAUSES, 1))
    clauses = []
    for i in range(CLAUSES):
        clause_vars = random.sample(range(VARIABLES), 3)
        # Which variables are negated in the clause?
        negated = np.array([random.random() < 0.5 for j in range(3)])
        A[i, clause_vars] = 2*negated - 1
        b[i] = sum(negated) - 1
    print "Generated %d clauses." % CLAUSES

    x = Bool(VARIABLES)
    # cost = sum([abs(v-0.5) for v in vars])
    prob = Problem(Minimize(0), [A*x <= b])
    print "true solution", prob.solve(solver=GUROBI)
    if prob.status != INFEASIBLE:
        break

# WEIRD. only works if rho varies.
x = Boolean(VARIABLES)
# prob = Problem(Minimize(sum_entries(pos(A*x - b))))
prob = Problem(Minimize(0), [A*x <= b])
RESTARTS = 1
ITERS = 50
result = prob.solve(method="admm", restarts=RESTARTS,
                    rho=RESTARTS*[10],
                    # rho=np.random.uniform(0,2,size=RESTARTS),
                    polish_depth=5,
                    parallel=False, prox_polished=False,
                    max_iter=ITERS, solver=ECOS, random=True,
                    polish_best=False, sigma=1, show_progress=True, alpha=1.5)

satisfied = (A*x.value <= b).sum()
percent_satisfied = 100*satisfied/CLAUSES
print "%s%% of the clauses were satisfied." % percent_satisfied


print prob.solve(method="relax_project_polish")
satisfied = (A*x.value <= b).sum()
percent_satisfied = 100*satisfied/CLAUSES
print "%s%% of the clauses were satisfied." % percent_satisfied


# Try random binary vectors.
total = 0
for i in range(RESTARTS*ITERS):
    x.value = np.random.uniform(size=VARIABLES) < 0.5
    if (A*x.value <= b).sum() == CLAUSES:
        total += 1
print "%s%% of random guesses satisfied" % (100*total/(RESTARTS*ITERS))



