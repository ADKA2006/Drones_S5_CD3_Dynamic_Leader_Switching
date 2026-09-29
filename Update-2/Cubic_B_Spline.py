import random as r
import numpy as np

def myKnot(nCPS, deg):  # Clamped
    # Number of knots = nCPS + deg + 1
    knots = [0] * (deg + 1)

    # Internal knots
    for _ in range(nCPS - deg - 1):
        knots.append(r.random())

    knots += [1] * (deg + 1)

    knots.sort()

    print(knots)
    return knots


def bSpline(p, CPts, U, u):

    # Special case: right endpoint
    if u >= U[-1]:
        return CPts[-1][:]

    # Find knot span k
    k = 0
    for i in range(len(U) - 1):
        if U[i] <= u < U[i + 1]:
            k = i
            break

    # p + 1 active control points
    d = [
        CPts[k - p + i][:]
        for i in range(p + 1)
    ]

    # de Boor algorithm
    for rr in range(1, p + 1):

        for i in range(p, rr - 1, -1):

            denominator = U[k + 1 + i - rr] - U[k - p + i]

            if denominator != 0:
                alpha = (u - U[k - p + i]) / denominator
            else:
                alpha = 0

            for j in range(len(d[i])):
                d[i][j] = (
                    (1 - alpha) * d[i - 1][j]
                    + alpha * d[i][j]
                )

    return d[p]

def BSpline(CPts, p):
    tempx = []
    tempy = []
    tempz = []
    U = myKnot(len(CPts),p)
    u = np.linspace(U[p],U[len(U)-p],100)

    for i in range(len(u)):
        temp = (bSpline(p,CPts,U,u[i]))
        tempx.append(temp[0])
        tempy.append(temp[1])
        tempz.append(temp[2])
    return tempx, tempy, tempz
