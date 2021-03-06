#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import sys
import pymongo
import re

mongo_host = '127.0.0.1'
mongo_port = 20018
serial_num = 0      # 编号

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

    serial_num = 0

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

def traverse(trees, tree_id):
    for child in trees[tree_id]['children']:
        # 如果该孩子是内部节点，遍历子树
        if trees.has_key(child):
            if not trees[child]['flag']:
                traverse(trees, child)
            trees[tree_id]['leaf_num'] += trees[child]['leaf_num']
            if trees[tree_id]['max_depth_subtree'] < trees[child]['max_depth_subtree'] + 1:
                trees[tree_id]['max_depth_subtree'] = trees[child]['max_depth_subtree'] + 1
        else:
            trees[tree_id]['leaf_num'] += 1
            if trees[tree_id]['max_depth_subtree'] < 1:
                trees[tree_id]['max_depth_subtree'] = 1
    trees[tree_id]['flag'] = True


def get_retweet_result(result, trees, parent_id, parent_index):
    global serial_num
    for current_id in trees[parent_id]['children']:
        serial_num += 1
        if trees.has_key(current_id):
            result.append({
                'm_id': current_id,
                'leaf_num': trees[current_id]['leaf_num'],
                'max_depth_subtree': trees[current_id]['max_depth_subtree'],
                'parent_index': parent_index
            })
            get_retweet_result(result, trees, current_id, serial_num)
        else:
            result.append({
                'm_id': current_id,
                'leaf_num': 0,
                'max_depth_subtree': 0,
                'parent_index': parent_index
            })

def make_retweet_tree(m_id):
    con = pymongo.MongoClient(mongo_host, mongo_port)
    db = con.weibodata

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
        retweet_weibo = db.retweet.find({'original_mid': m_id})

        for item in retweet_weibo:
            name, data = preprocess(item['retweet_mid'])
            child_weibo_data[name] = data

        trees = {}      # 一个单层的树
        trees[m_id] = {
            'leaf_num': 0,      # 叶子节点个数
            'max_depth_subtree': 0,     # 最大的子树高度
            'children': [],     # 应该只用存id即可
            'flag': False       # 是否遍历过，之后有用
        }
        

        for item in child_weibo_data:
            # 第一代转发微博
            if 'parent_name' not in child_weibo_data[item]:
                trees[m_id]['children'].append(
                    child_weibo_data[item]['m_id']
                )
            else:
                parent_name = child_weibo_data[item]['parent_name']
                # 用它的parent_name去查child_weibo_data中的m_id，即父微博id
                # 如果父微博在当前转发集合中，则不是第一代
                if parent_name in child_weibo_data:
                    parent_id = child_weibo_data[parent_name]['m_id']
                    if not trees.has_key(parent_id):
                        trees[parent_id] = {
                            'leaf_num': 0,      # 叶子节点个数
                            'max_depth_subtree': 0,     # 最大的子树高度
                            'children': [],     # 应该只用存id即可
                            'flag': False       # 是否遍历过，之后有用
                        }
                    trees[parent_id]['children'].append(
                        child_weibo_data[item]['m_id']
                    )
                # 否则看做第一代转发微博
                else:
                    trees[m_id]['children'].append(
                        child_weibo_data[item]['m_id']
                    )
        
        for tree_id in trees:
            if not trees[tree_id]['flag']:
                traverse(trees, tree_id)
        
        # 结果
        result = [{
            'm_id': m_id,
            'leaf_num': trees[m_id]['leaf_num'],
            'max_depth_subtree': trees[m_id]['max_depth_subtree'],
            'parent_index': -1
        }]
        
        get_retweet_result(result, trees, m_id, 0)
        return result


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

