#encoding=utf-8
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
# import pandas as pd
import json

def logistic_increase_function(t, S0, r):
    # t:time   t0:initial time = 0    S0:initial_score    M:full_score  r:increase_rate
    M = 100
    exp_value=np.exp(-(r * t))
    return (M * S0) / (S0 + (M - S0) * exp_value)



#定义x、y散点坐标
f = open('../source/sample.json', encoding='utf-8')
res = f.read()
data = json.loads(res)
user_id = '48117'
case_id = '2199'
cases = data[user_id]['cases']

score = []
for case in cases:
    if case["case_id"] == case_id:
        upload_records_lst = case["upload_records"]
        for record in upload_records_lst:
            if record["score"] != 0:
                score.append(record["score"])

score = score[24:]
time = np.arange(1, len(score) + 1)
print('time is :\n', time)
score = np.array(score)
print('score is :\n', score)

popt, pcov = curve_fit(logistic_increase_function, time, score)
#获取拟合系数
S0_val = popt[0]
r_val = popt[1]

score_val = logistic_increase_function(time, S0_val, r_val) #拟合score值
print(u'系数S0_val:', S0_val)
print(u'系数r_val:', r_val)

plot1 = plt.plot(time, score, 's',label='original values')
plot2 = plt.plot(time, score_val, 'r',label='polyfit values')
plt.xlabel('time')
plt.ylabel('score')
plt.legend(loc=4)
plt.title('student ' + user_id + ': ' + case_id)
plt.show()

