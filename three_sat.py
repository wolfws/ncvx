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
VARIABLES = 100
CLAUSES_PER_VARIABLE = 3

# The 3-SAT solution.
solution = [random.random() < 0.5 for i in range(VARIABLES)]

# The 3-SAT clauses.
clauses = []
for i in range(VARIABLES*CLAUSES_PER_VARIABLE):
    clause_vars = random.sample(range(VARIABLES), 3)
    # Which variables are negated in the clause?
    negated = [random.random() < 0.5 for j in range(3)]
    # while True:
    #     negated = [random.random() < 0.5 for j in range(3)]
    #     # Must be consistent with the solution.
    #     result = False
    #     for index, negation in zip(clause_vars,negated):
    #         result |= negation ^ solution[index]
    #     if result:
    #         break
    clauses.append( (clause_vars, negated) )
print "Generated %d clauses." % len(clauses)

# The 3-SAT variables.
vars = [Boolean() for i in range(VARIABLES)]

# The 3-SAT constraints.
cost = 0
constraints = []
for clause_vars, negated in clauses:
    terms = []
    for index, negation in zip(clause_vars,negated):
        if negation:
            terms.append( (1-vars[index]) )
        else:
            terms.append(vars[index])
    constraints.append(sum(terms) >= 1)
    # cost += neg(sum(terms) - 1)
# cost = sum([random.random()*v for v in vars])

best_values = VARIABLES*[0]
best_match = 0
best_rho = 0
for i in range(10):
    p = Problem(Minimize(0), constraints)
    rho = random.random()
    print rho
    # result = p.solve(method="admm_basic", rho=rho,
    #                  iterations=2, solver=ECOS)
    result = p.solve(method="admm", rho=[rho], restarts=1,
                     max_iter=50, solver=ECOS, random=True)
    print result
    # print p.solve(method="repeated_rr", max_iter=25, delta=1.05, tau_init=1)
    # print p.solve(method="relax_and_round")

    # Store the result.
    values = [vars[i].value for i in range(VARIABLES)]

    # What percentage of the clauses were satisfied?
    satisfied = []
    for clause_vars,negated in clauses:
        result = False
        for index, negation in zip(clause_vars,negated):
            if negation:
                result |= vars[index].value <= EPSILON
            else:
                result |= vars[index].value > EPSILON
        satisfied.append(result)

    if sum(satisfied) > best_match:
        best_values = values
        best_match = sum(satisfied)
        best_rho = rho
    if best_match == len(clauses): break

    print best_match, len(clauses)

percent_satisfied = 100*best_match/len(clauses)
print "%s%% of the clauses were satisfied." % percent_satisfied
