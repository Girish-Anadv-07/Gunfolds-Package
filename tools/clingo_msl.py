""" This module contains clingo interaction functions """
from __future__ import print_function

import time

from gunfolds.tools.clingo import clingo
from gunfolds.tools.conversions import g2clingo, g2wclingo, msl_jclingo2g
import time


uprogram = """
{ edge1(X,Y) } :- node(X),node(Y).
edge(X,Y,1) :- edge1(X,Y).
edge(X,Y,L) :- edge(X,Z,L-1),edge1(Z,Y), L <= U, u(U).
derived_edgeu(X,Y) :- edge(X,Y,L), u(L).
derived_confu(X,Y) :- edge(Z,X,L), edge(Z,Y,L),node(X),node(Y),node(Z),X < Y, L < U, u(U).
:- edgeu(X,Y), not derived_edgeu(X,Y),node(X),node(Y).
:- not edgeu(X,Y), derived_edgeu(X,Y),node(X),node(Y).
:- derived_confu(X,Y), not confu(X,Y),node(X),node(Y), X < Y.
:- not derived_confu(X,Y), confu(X,Y),node(X),node(Y), X < Y.
    """
wuprogram = """
    { edge1(X,Y) } :- node(X), node(Y).
    path(X,Y,1) :- edge1(X,Y).
    path(X,Y,L) :- path(X,Z,L-1), edge1(Z,Y), L <= U, u(U).
    edgeu(X,Y) :- path(X,Y,L), u(L).
    confu(X,Y) :- path(Z,X,L), path(Z,Y,L), node(X;Y;Z), X < Y, L < U, u(U).
    :~ edgeh(X,Y,W), not edgeu(X,Y). [W,X,Y,1]
    :~ no_edgeh(X,Y,W), edgeu(X,Y). [W,X,Y,1]
    :~ confh(X,Y,W), not confu(X,Y). [W,X,Y,2]
    :~ no_confh(X,Y,W), confu(X,Y). [W,X,Y,2]
    """

def rate(u):
    s = "u("+str(u)+")."
    return s

def g2clingo_msl(g):
    return g2clingo(g, directed='edgeu', bidirected='confu', both_bidirected=True)

def msl_command(g, urate=2, exact=True):
    if exact:
        command = rate(urate) +' ' + g2clingo_msl(g) + ' ' + uprogram
    else:
        command = rate(urate) + ' ' + g2wclingo(g) + ' ' + wuprogram
    command = command.encode().replace(b"\n", b" ")
    return command

def msl(g, capsize, exact=True, urate=2, timeout=0, pnum=None):
    return clingo(msl_command(g, urate=urate, exact=exact), capsize=capsize, convert=msl_jclingo2g, timeout=timeout, pnum=pnum)

def rasl_msl(g, capsize, exact=True, urate=2, timeout=0, pnum=None):
    r = set()
    remain_time = timeout
    for i in range(2, urate + 1):
        startTime = int(round(time.time()))
        k = msl(g, capsize, urate=i, pnum=pnum, timeout=remain_time)
        endTime = int(round(time.time()))
        remain_time = max(0, remain_time - (endTime - startTime))
        r = r | {(x[0], i) for x in k}
        capsize = max(0, capsize - len(r))
        if not (capsize and remain_time):
            break
    return r

