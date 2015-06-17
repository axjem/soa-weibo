#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import sys
import pymongo
import re

mongo_host = '127.0.0.1'
mongo_port = 20018
tree_result = []
true_result = []

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    # 设计文件中定义传入格式: {"m_id": "104967351"}

    if request.method == 'POST':
        json_data = request.get_json()  # 读取POST请求中的JSON
        # 设计文件中定义传入格式: {"m_id": "104967351"}
        m_id = json_data["m_id"]    # 得到m_id

    else:
        m_id = request.values.get('m_id', '3511308492007954')

    print "m_id =", m_id

    global tree_result
    global true_result
    
    tree_result = []
    true_result = []

    res = {
        "tree_node": make_retweet_tree(m_id),
        "statistics": make_retweet_statistics(m_id)
    }
    return jsonify(res)

def make_retweet_statistics(m_id):
    con = pymongo.MongoClient(mongo_host, mongo_port)
    db = con.weibodata

    # 在db.retweet中找这条信息是否转发了其他信息
    if db.retweet.find_one({'original_mid': m_id}) is None:
    # 若是：则它不是祖先节点，在表项中找它的祖先节点

        # 在db.retweet中找它的祖先微博original_mid
        original_mid = db.retweet.find_one({'retweet_mid': m_id})['original_mid']
        # 递归
        return make_retweet_statistics(original_mid)

    else:
    # 若不是：则它是祖先节点
        u_ids = []
        # 在db.retweet中找祖先微博的m_id为这个m_id的微博
        retweet_weibo = db.retweet.find({'original_mid': m_id})
        # 得到一个集合

        for item in retweet_weibo:
            # 将u_id放入u_ids列表中
            u_ids.append(item['retweet_uid'])

        male_num = 0
        verified_num = 0
        total_tweets = 0
        total_followers = 0
        total_followees = 0
        location_dist = {}

        for u_id in u_ids:
            # 在user里面查找他的信息
            user = db.user.find_one({'u_id': u_id})

            # 使用几个计数器，比如如果性别为男性则male += 1, 有通过验证则verified += 1等
            if user['gender'] == 'm':
                male_num += 1
            if user['verified_type'] != '-1':   # 验证了的是不同号码挺有趣？
                verified_num += 1
            total_tweets += int(user['num_tweets'])
            total_followers += int(user['num_followers'])
            total_followees += int(user['num_followees'])
            
            location = user['location']
            location = get_city_from_location(location)

            if location in location_dist:
                location_dist[location] += 1
            else:
                location_dist[location] = 1

        # 每个计数器的值除以len(u_ids)即得出比例
        user_nums = len(u_ids)
        gender_ratio = male_num * 1.0 / user_nums
        verified_ratio = verified_num *  1.0 / user_nums
        avg_tweets = total_tweets * 1.0 / user_nums
        avg_followers = total_followers * 1.0 / user_nums
        avg_followees = total_followees * 1.0 / user_nums

        for loc in location_dist:
            location_dist[loc] /= (user_nums * 1.0)
            location_dist[loc] = str(location_dist[loc])

        result = {
            'gender_ratio': str(gender_ratio),
            'verified_ratio': str(verified_ratio),
            'avg_tweets': str(avg_tweets),
            'avg_followers': str(avg_followers),
            'avg_followees': str(avg_followees),
            'location_dist': location_dist
        }
        return result

def handle(pid,depth):
    sub_child = []

    global tree_result
    global true_result

    for item in tree_result:
        if item['parent'] == pid:
            sub_child.append(item)

    max_leaf = 0
    max_depth = -1
    if len(sub_child) == 0:
        return depth,1
    
    for item in sub_child:
        true_result.append(item)
        a,b = handle(item['m_id'],item['depth'])
        if a > max_depth:
            max_depth = a
        max_leaf += b
        for i in true_result:
            if i['m_id'] == item['m_id']:
                i['max_leaf_subtree'] = b
                i['max_depth_subtree'] = a-i['depth']
                break
            
    return max_depth,max_leaf
    

def make_retweet_tree(m_id):
    con = pymongo.MongoClient(mongo_host, mongo_port)
    db = con.weibodata

    global tree_result
    global true_result
    child_weibo_data = {}

    # 在db.retweet中找这条信息是否转发了其他信息
    if db.retweet.find_one({'original_mid': m_id}) == None:
    # 若是：则它不是祖先节点，在表项中找它的祖先节点
        # 在db.retweet中找它的祖先微博original_mid
        original_mid = db.retweet.find_one({'retweet_mid': m_id})['original_mid']
        # 递归
        return make_retweet_tree(original_mid)

    # 若不是：则它是祖先节点
    else:
        # 在db.retweet中找祖先微博的m_id为这个m_id的微博
        retweet_weibo = db.retweet.find({'original_mid': m_id})
        # 得到一个集合

        for item in retweet_weibo:
            name, data = preprocess(item['retweet_mid'])
            # 得到它的用户名，及它的相关数据
            child_weibo_data[name] = data

            # 例
            #~ child_weibo_data = {
            #~     "显安": {"m_id": "1"},
            #~     "马琳": {"m_id": "2", "parent_name": "显安"},
            #~     "李雪": {"m_id": "3"},
            #~     "爽爷": {"m_id": "4", "parent_name": "李雪"}
            #~ }
            # 表示显安和李雪转发了某条微博，马琳转发了显安，爽爷转发了李雪
        tree_result.append({
             'm_id': m_id, 
             'parent': "null",
             'depth': 0,
             'parent_index':-1,         # 节点的父亲序号
             'max_depth_subtree':-1,    # 子树的高度
             'max_leaf_subtree':-1      # 子树叶节点数
             })
        flag = False
        for item in child_weibo_data:
            if 'parent_name' not in child_weibo_data[item]:
                # 是第一代转发微博，放入result中
                tree_result.append({
                    'm_id': child_weibo_data[item]['m_id'], 
                    'parent': m_id,
                    'depth':1,
                    'parent_index':-1,
                    'max_depth_subtree':-1,
                    'max_leaf_subtree':-1
                })
            else:
                parent_name = child_weibo_data[item]['parent_name']
                # 用它的parent_name去查child_weibo_data中的m_id，即父微博id
                if parent_name in child_weibo_data:
                    parent_id = child_weibo_data[parent_name]['m_id']
                    tree_result.append({
                        'm_id': child_weibo_data[item]['m_id'], 
                        'parent': parent_id,
                        'depth': -1,
                        'parent_index':-1,
                        'max_depth_subtree':-1,
                        'max_leaf_subtree':-1
                    })
                    flag = True
                    # print parent_id
                else:
                    tree_result.append({
                        'm_id': child_weibo_data[item]['m_id'], 
                        'parent': m_id,
                        'depth':1,
                        'parent_index':-1,
                        'max_depth_subtree':-1,
                        'max_leaf_subtree':-1
                    })
        while flag:
            flag = False
            for item in tree_result:
                if item['depth'] == -1:
                    parent = item['parent']
                    for p in tree_result:
                        if p['m_id'] == parent and p['depth'] != -1:
                            item['depth'] = p['depth'] + 1
                            break
            for item in tree_result:
                if item['depth'] == -1:
                    flag = True
        handle("null",0)
        for i in range(1,len(true_result)):
            parent = true_result[i]['parent']
            for j in range(0,i):
                if true_result[j]['m_id'] == parent:
                    true_result[i]['parent_index'] = j
                    break
                
        return true_result
        # 例（续上方）：
        #~ result = [
        #~     {
        #~         "m_id": "1",
        #~         "parent": "0"
        #~     },
        #~     {
        #~         "m_id": "2",
        #~         "parent": "1"
        #~     },
        #~     {
        #~         "m_id": "3",
        #~         "parent": "0"
        #~     },
        #~     {
        #~         "m_id": "4",
        #~         "parent": "3"
        #~     }
        #~ ]

def preprocess(m_id):
    """返回该微博的m_id, 用户名，及里面//@的第一个人的用户名。"""

    con = pymongo.MongoClient(mongo_host, mongo_port)
    db = con.weibodata
    weibo = db.weibo.find_one({'mid': m_id})
    u_id = weibo['uid']    
    name = db.user.find_one({'u_id': u_id})['name']
    
    text = weibo['text']
    tmp = text.decode('utf8') 
    regExp = u'//@[\u4e00-\u9fa5_a-zA-Z0-9_]+:'
    pattern = re.compile(regExp)
    results = pattern.findall(tmp)

    if len(results) > 0:
        parent_name = results[0][3:-1]
        data = {'m_id': m_id, 'parent_name': parent_name}
    else:
        data = {'m_id': m_id}

    return name, data   # 二元组
    # 例：
    # name = "爽爷"
    # data = {"m_id": "4", "parent_name": "李雪"}

def get_city_from_location(loc):
    if ' ' not in loc:
        return loc
    if '区' in loc:
        return loc.split()[0]
    return loc.split()[1]

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    app.run(host='0.0.0.0', port = 18084, debug=False)

