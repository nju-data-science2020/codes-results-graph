# -*- coding: UTF-8 -*-

import json
from math import log, floor, e
from statistics import stdev, pstdev

""" 四个基本方法 """

# 均值
def average(X):
    if len(X) <= 0:
        return -1
    sum = 0
    for x in X:
        sum += x
    return sum / float(len(X))

# 中位数
def middle(X, isSorted = False):
    n = len(X)
    if not isSorted:
        X = sorted(X)
    if n % 2 == 1:
        return X[n//2]
    return (X[n//2 - 1] + X[n//2])/2

# 标准差
def sigma(X):
    n = len(X)
    mx = average(X)
    sum = 0
    for x in X:
        sum += (x - mx)**2
    return (sum / (n - 1))**(1/2)

# Sxx, Sxy 用于计算回归斜率
def S(X, Y):
    if len(X) != len(Y):
        raise Exception("invalid Sxy parameter")
    n = len(X)
    mx = average(X)
    my = average(Y)
    total = 0
    for i in range(n):
        total += (X[i] - mx) * (Y[i] - my)
    return total

# 回归分析 y = a + bx, 求 a, b
def regression(X, Y):
    sxy = S(X, Y)
    sxx = S(X, X)
    b = sxy / sxx
    mx = average(X)
    my = average(Y)
    a = my - mx * b
    return a, b

##############################
""" 参数设置 """

sample_path = '../sample.json'
test_data_path = '../test_data.json'
formatted_data_paths = ['./user_record_{}.json'.format(i) for i in range(1, 28)]
case_types_path = './types.json'
user_r_path = './user_r.json'
type_case_seq_path = './type_case_seq.json'
user_type_case_rank_path = './user_type_case_rank.json'

chunk_size = 10 # 学生分档
M = 100 # 最高分

##############################
""" 文件读写 I/O 方法 """

# 写数据（保存中间数据、重新编排的数据）
def write_file(data, file_path, UTF8=False):
    try:
        f = False
        if UTF8:
            f = open(file_path, mode='w', encoding='utf-8')
        else:
            f = open(file_path, mode='w')
        json.dump(data, f)
    except Exception as err:
        print(err)
    finally:
        if f:
            f.close()
    pass

# 读数据（从文件抽取数据）
def get_data(file_path):
    try:
        f = False
        f = open(file_path)
        data = json.load(f)
        return data
    except Exception as err:
        print(err)
    finally:
        if f:
            f.close()

##############################
""" 1. 处理原数据（提取需要数据、分档） """

# 分散所有学生成绩
def divide_keys(obj):
    keys = list(obj.keys())
    keys_list = []
    for i in range(0, len(keys), chunk_size):
        keys_list.append(keys[i:i+chunk_size])
    for keys in keys_list:
        print(keys)
    return keys_list

# 提取指定学生指定题目的记录
def get_user_case_records(data, user_id, case_id):
    user = data[user_id]
    obj = {"time_seq": [-1.0], "score_seq": [0.0]}
    for case in user['cases']:
        if case['case_id'] == case_id:
            obj['final_score'] = case['final_score']
            obj['type'] = case['case_type']
            if len(case['upload_records']) <= 0:
                break
            base_time = case['upload_records'][0]['upload_time']
            for record in case['upload_records']:
                obj['time_seq'].append((record['upload_time'] - base_time) / 1000.0 / 60.0)
                obj['score_seq'].append(record['score'])
            break
    return obj

# 抽取必要数据并重新编排数据格式
def reformat_data():
    data = get_data(test_data_path)
    print('test_data keys: ' + str(len(data.keys())))

    obj = {}

    for user_id, user_info in data.items():
        obj[user_id] = {}
        for case in user_info['cases']:
            case_id = case['case_id']
            records = get_user_case_records(data, user_id, case_id)
            obj[user_id][case_id] = records
    # print(obj)
    keys_list = divide_keys(obj)
    i = 1
    for keys in keys_list:
        target = {}
        for key in keys:
            target[key] = obj[key]
        write_file(target, './user_record_{}.json'.format(i))
        i += 1


##############################
""" 2. 抽取题目类型并保存 """

# 收集所有类型
def pick_case_types_and_store():
    data = get_data(test_data_path)
    types = {}
    for user_id, user_info in data.items():
        for case in user_info['cases']:
            case_id = case['case_id']
            case_type = case['case_type']
            if not case_type in types:
                types[case_type] = set()
            types[case_type].add(case_id)
    
    for case_type in types:
        types[case_type] = list(types[case_type])
    
    write_file(types, case_types_path)

# 检查各类型题目数量
def check_types():
    types = get_data(case_types_path)
    for t, cases in types.items():
        print('type: {}, num: {}'.format(t, len(cases)))
    return types


##############################
""" 3. 计算所有学生熟练度 """

# 提取成绩和时间序列
def get_seq(case):
    obj = {}
    obj['score_seq'] = case['score_seq']
    obj['time_seq'] = case['time_seq']
    obj['len'] = len(case['time_seq'])
    return obj

# 计算熟练度
def count_r(seq):
    X = []
    Y = []
    l = seq['len']
    for i in range(l):
        x = seq['time_seq'][i]
        s = seq['score_seq'][i]
        X.append(x)
        Y.append(log((s+1)/(M-s+1)))
    # print(X)
    # print(Y)
    return regression(X, Y)
    
# 计算所有学生对于所有题目的熟练度
def count_all_r_and_restore_data():
    result = {}
    for path in formatted_data_paths:
        user_record = get_data(path)
        for user_id in user_record.keys():
            result[user_id] = {}
            for case_id in user_record[user_id].keys():
                case = user_record[user_id][case_id]
                seq = get_seq(case)
                l = seq['len']
                if l > 1:
                    a, b = count_r(seq)
                    result[user_id][case_id] = {"type": case['type'], "r": b, "offset": a}
    write_file(result, user_r_path)

##############################
""" 4. 按题目类型分类并收集总体表现 """

# 计算题目相对难度
def count_type_difficulty(type_cases):
    cases_r_seq = []
    cases_middles = []
    for case_id, case_info in type_cases.items():
        cases_r_seq += case_info['r_seq']
        cases_middles.append(case_info['middle'])
    
    sigma_middle = sigma(cases_middles) + 1
    total_middle = middle(cases_r_seq)
    for case_id, case_info in type_cases.items():
        m = case_info['middle']
        d = (m - total_middle) / sigma_middle
        type_cases[case_id]['difficulty'] = d

# 计算所有题目难度并分类后保存
def count_all_type_case_seq():
    user_r = get_data(user_r_path)
    case_r_seq = {}
    for user_id, cases in user_r.items():
        for case_id, case_info in cases.items():
            if not case_id in case_r_seq:
                case_r_seq[case_id] = {'r_seq': [], 'type': case_info['type']}
            case_r_seq[case_id]['r_seq'].append(case_info['r'])
    for case_id, case_info in case_r_seq.items():
        r_seq = case_info['r_seq'] = sorted(case_info['r_seq'])
        case_r_seq[case_id]['middle'] = middle(r_seq, True)
        case_r_seq[case_id]['sigma'] = sigma(r_seq)
        
    type_case_seq = {}
    types = check_types()
    for case_type in types:
        type_case_seq[case_type] = {}

    for case_id, case_info in case_r_seq.items():
        type_case_seq[case_info['type']][case_id] = case_info

    for case_type, cases in type_case_seq.items():
        count_type_difficulty(cases)        
    
    write_file(type_case_seq, type_case_seq_path)

##############################
""" 5. 计算学生熟练度评分 """

# 计算所有学生的熟练度和评分
def count_user_type_case_rank():
    user_r = get_data(user_r_path)
    type_case_seq = get_data(type_case_seq_path)

    result = {}
    for user_id, cases in user_r.items():
        result[user_id] = {}
        PJs = {}
        for case_id, case_info in cases.items():
            r = case_info['r']
            case_type = case_info['type']
            if r < 0:
                r = 0
            if case_id not in type_case_seq[case_type]:
                continue
            if case_type not in result[user_id]:
                result[user_id][case_type] = {'cases_rank': [], 'type_rank': -1}
                PJs[case_type] = []
            case_j = type_case_seq[case_type][case_id]
            middleJ = case_j['middle']
            sigmaJ = case_j['sigma']
            difficultyJ = case_j['difficulty']
            user_rank = (r - middleJ) / sigmaJ
            result[user_id][case_type]['cases_rank'].append({"case_id": case_id, "rank": user_rank})

            expYD = e**(user_rank - difficultyJ)
            PJ = expYD / (1 + expYD)
            PJs[case_type].append(PJ)
        for case_type in PJs:
            result[user_id][case_type]['type_rank'] = average(PJs[case_type])
    
    write_file(result, user_type_case_rank_path)
##############################

if __name__ == '__main__':
    reformat_data()
    pick_case_types_and_store()
    count_all_r_and_restore_data()
    count_all_type_case_seq()
    count_user_type_case_rank()