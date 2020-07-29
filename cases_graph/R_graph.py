#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 10:04:56 2020

"""

import numpy as np
import matplotlib.pyplot as plt
import json
from math import log

f1 = open('../user_record_1.json', encoding='utf-8')
f2 = open('../user_r.json', encoding='utf-8')
res1 = f1.read()
res2 = f2.read()
data1 = json.loads(res1)
data2 = json.loads(res2)

def get_graph_data(uid, pid):
    case = data1[uid][pid]
    r = data2[uid][pid]['r']
    offset = data2[uid][pid]['offset']
    time, score, M = case['time_seq'], case['score_seq'], 100
    pro_score = []
    pro_time = time
    line_y = []
    for y in score:
        pro_score.append(log((y + 1) / (M - y + 1)))
    for x in pro_time:
        line_y.append(r * x + offset)
        
    print("user_id:", uid, "rM:", r)
    
    return np.array(pro_time), np.array(pro_score), line_y

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
ax1.set_xlabel("time")
ax1.set_ylabel("ln-score")

#------------------------------------48117---------------------------------------

user_id1 = '48117'


problem_id1 = '2140'
graph_data = get_graph_data(user_id1, problem_id1)
ax1.scatter(graph_data[0], graph_data[1])
ax1.plot(graph_data[0], graph_data[2], label=user_id1 + ": " + problem_id1)

problem_id2 = '2209'
graph_data = get_graph_data(user_id1, problem_id2)
ax1.scatter(graph_data[0], graph_data[1])
ax1.plot(graph_data[0], graph_data[2], label=user_id1 + ": " + problem_id2)

#------------------------------------49405---------------------------------------

#
user_id2 = '49405'


problem_id3 = '2140'
graph_data = get_graph_data(user_id2, problem_id3)
ax1.scatter(graph_data[0], graph_data[1])
ax1.plot(graph_data[0], graph_data[2], 'g--', label=user_id2 + ": " + problem_id3)
#ax1.set_title('student ' + user_id2 + ': ' + problem_id3)

#--------------------------------------------------------------------

plt.legend()
plt.show()

