from __future__ import division
from cvxpy import *
from noncvx_admm import *
import numpy as np

# Traveling salesman problem.
n = 5

# Get locations.
np.random.seed(2)
w = 10
x = np.random.uniform(-w, w, size=(n,1))
y = np.random.uniform(-w, w, size=(n,1))
# x = np.zeros((n,1))
# y = np.zeros((n,1))
# x[0] = -w + 4*w/n
# y[0] = -w
# x[1] = x[0]
# y[1] = -w + 4*w/n
# for i in range(1,n//2):
#     x[2*i] = x[2*i-1] + 4*w/n
#     y[2*i] = y[2*i-1]
#     x[2*i+1] = x[2*i]
#     y[2*i+1] = y[2*i] + 4*w/n
X = np.vstack([x.T,y.T])

MAX_ITER = 25
RESTARTS = 1

# Classical MIP approach.
# Edge matrix.
P = Assign(n, n)
constr = [trace(P) == 0]#,
          # (P + P.T)/2 - np.ones((n,n))/n << np.cos(2*np.pi/n)*np.eye(n)]
mat = (P + P.T)/2 - np.ones((n,n))/n - np.cos(2*np.pi/n)*np.eye(n)
barrier = pos(lambda_max(mat))
# Make distance matrix.
D = np.zeros((n,n))
for i in range(n):
    for j in range(n):
        D[i,j] = norm(X[:,i] - X[:,j]).value

prob = Problem(Minimize(vec(D).T*vec(P) + 50000*barrier), constr)
# result = prob.solve(method="relax_and_round")
# print "relax and round result", result
result = prob.solve(method="admm", max_iter=MAX_ITER,
                    restarts=RESTARTS, random=True,
                    rho=np.random.uniform(0,1,size=RESTARTS),
                    verbose=False, polish_best=False, solver=SCS)
print "all constraints hold:", np.all([c.value for c in prob.constraints])
print "final value", result
print barrier.value
print lambda_max(mat).value
print lambda_min(mat).value

import matplotlib.pyplot as plt
ordered = (X*P.T).value
for i in range(n):
    plt.plot([X[0,i], ordered[0,i]],
             [X[1,i], ordered[1,i]],
             color = 'brown', marker = 'o')
plt.show()


# True solution.
P = Bool(n, n)
constr = [trace(P) == 0,
          np.ones((1,n))*P == 1,
          P*np.ones((n,1)) == 1]
u = Int(n)
for i in range(1,n):
    for j in range(n):
        if i != j:
            constr += [u[i] - u[j] + n*P[i,j] <= n - 1]

prob = Problem(Minimize(vec(D).T*vec(P)), constr)
result = prob.solve(solver=GUROBI, TimeLimit=120)
print "true value", result

import matplotlib.pyplot as plt
ordered = (X*P.T).value
for i in range(n):
    plt.plot([X[0,i], ordered[0,i]],
             [X[1,i], ordered[1,i]],
             color = 'brown', marker = 'o')
plt.show()


#########################################################

# Make objective.
perm = Assign(n, n)
# ordered = hstack([-w,-w],
#                  X*perm,
#                  [w,w])
ordered = X*perm
cost = norm(ordered[:,-1] - ordered[:,0])
for i in range(n-1):
    cost += norm(ordered[:,i+1] - ordered[:,i])

# reg = 0
# for i in range(n+1):
#     reg += sum_entries(neg(ordered[:,i+1] - ordered[:,i]))

prob = Problem(Minimize(cost))
result = prob.solve(method="admm", max_iter=MAX_ITER,
                    restarts=RESTARTS, random=True, #rho=RESTARTS*[10],
                    solver=ECOS, verbose=False, sigma=1.0, polish_best=False)#, tau=1.1, tau_max=100)
print "all constraints hold:", np.all([c.value for c in prob.constraints])
print "final value", cost.value

import matplotlib.pyplot as plt
plt.plot(ordered.value[0,[0,-1]].T,
         ordered.value[1,[0,-1]].T,
         color = 'brown', marker = 'o')
for i in range(n-1):
    plt.plot(ordered[0,i:i+2].value.T,
             ordered[1,i:i+2].value.T,
             color = 'brown', marker = 'o')
plt.show()

# print "relax and round result", prob.solve(method="relax_and_round")

# # print prob.solve(method="polish")
# # print np.around(positions.value)

# perm = Bool(n, n)
# ordered_x = vstack(-w, perm*x, w)
# ordered_y = vstack(-w, perm*y, w)
# cost = 0
# for i in range(n+1):
#     x_diff = ordered_x[i+1] - ordered_x[i]
#     y_diff = ordered_y[i+1] - ordered_y[i]
#     cost += norm(vstack(x_diff, y_diff))
# prob = Problem(Minimize(cost),
#         [perm*np.ones((n, 1)) == 1,
#          np.ones((1, n))*perm == 1])
# prob.solve(solver=GUROBI, verbose=False, TimeLimit=100)
# print "gurobi solution", prob.value

# for i in range(n+1):
#     plt.plot([ordered_x[i].value, ordered_x[i+1].value],
#              [ordered_y[i].value, ordered_y[i+1].value],
#              color = 'brown', marker = 'o')
# plt.show()
# # print positions.value

# # Randomly guess permutations.
# total = 0
# best = np.inf
# for k in range(RESTARTS*MAX_ITER):
#     perm.value = np.zeros(perm.size)
#     selection = np.random.permutation(n)
#     perm.value[selection, range(n)] = 1
#     val = cost.value
#     if val < result:
#         total += 1
#     if val < best:
#         best = val
#     # print positions.value
# print "%% better = ", (total/(RESTARTS*MAX_ITER))
# print "best = ", best