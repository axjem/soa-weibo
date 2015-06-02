#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import sys
import pymongo
import re

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    # 设计文件中定义传入格式: {"m_id": "104967351"}
    m_id = request.values.get('m_id', '3511308492007954')
    response = []
    response.append(make_retweet_tree(m_id))
    response.append(make_retweet_statistics(m_id))
    return response.__str__()

    '''
    if request.method == 'POST':
        json_data = request.get_json()  # 读取POST请求中的JSON
        # 设计文件中定义传入格式: {"m_id": "104967351"}
        m_id = json_data["m_id"]    # 得到m_id

        # 待实现：处理m_id并返回所要求的结构

        return make_retweet_tree(m_id)

    else:
        return 'Hello World!'
    '''

def make_retweet_statistics(m_id):
    # 在db.retweet中找这条信息是否转发了其他信息
    # 若是：则它不是祖先节点，在表项中找它的祖先节点
        # 在db.retweet中找它的祖先微博original_mid
        # 递归～ return make_retweet_statistics(original_mid)

    # 若不是：则它是祖先节点
        # u_ids = []
        # 在db.retweet中找祖先微博的m_id为这个m_id的微博
        # 得到一个集合
        # 对于集合中的每条微博：
            # 将u_id放入u_ids列表中

        # 对于u_ids中的每一个u_id:
            # 在user里面查找他的信息
            # 使用几个计数器，比如如果性别为男性则male += 1, 有通过验证则verified += 1等
        
        # 每个计数器的值除以len(u_ids)即得出比例
    con = pymongo.MongoClient('127.0.0.1', 27017)
    db = con.weibodata

    if db.retweet.find_one({'original_mid': m_id}) == None:
        original_mid = db.retweet.find_one({'retweet_mid': m_id})['original_mid']
        return make_retweet_statistics(original_mid)
    else:
        u_ids = []
        retweet_weibo = db.retweet.find({'original_mid': m_id})
        for item in retweet_weibo:
            u_ids.append(item['retweet_uid'])
        male_num = 0
        verified_num = 0
        for u_id in u_ids:
            user = db.user.find_one({'u_id': u_id})
            if user['gender'] == 'm':
                male_num += 1
            if user['verified_type'] != '-1':   # 验证了的是不同号码挺有趣？
                verified_num += 1
        gender_ratio = male_num * 1.0 / len(u_ids)
        verified_ratio = verified_num *  1.0 / len(u_ids)
        result = []
        result.append({'gender_ratio': gender_ratio})
        result.append({'verified_ratio': verified_ratio})
        return result

def make_retweet_tree(m_id):
    # 在db.retweet中找这条信息是否转发了其他信息
    # 若是：则它不是祖先节点，在表项中找它的祖先节点
        # 在db.retweet中找它的祖先微博original_mid
        # 递归～ return make_retweet_tree(original_mid)

    # 若不是：则它是祖先节点
        # 在db.retweet中找祖先微博的m_id为这个m_id的微博
        # 得到一个集合
        # 对于集合中的每条微博：
            # 调用preprocess(它的m_id)
            # 如：name, data = preprocess(它的m_id)
            # 得到它的用户名，及它的相关数据
            # 存到child_weibo_data中
            # 如：child_weibo_data[name] = data

            # 例
            #~ child_weibo_data = {
            #~     "显安": {"m_id": "1"},
            #~     "马琳": {"m_id": "2", "parent_name": "显安"},
            #~     "李雪": {"m_id": "3"},
            #~     "爽爷": {"m_id": "4", "parent_name": "李雪"}
            #~ }
            # 表示显安和李雪转发了某条微博，马琳转发了显安，爽爷转发了李雪

        # 对于child_weibo_data中的每一项：
            # if not has_key("parent_name"):    （之类的，具体语法我想不起来）
                # 是第一代转发微博，放入result中，
                # m_id 为自己的m_id, parent 为祖先节点的m_id

            # 否则：
                # 用它的parent_name去查child_weibo_data中的m_id，即父微博id
                # 放到result中

        # 返回result

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
    con = pymongo.MongoClient('127.0.0.1', 27017)
    db = con.weibodata

    result = []
    child_weibo_data = {}
    if db.retweet.find_one({'original_mid': m_id}) == None:
        original_mid = db.retweet.find_one({'retweet_mid': m_id})['original_mid']
        return make_retweet_tree(original_mid)
    else:
        retweet_weibo = db.retweet.find({'original_mid': m_id})
        for item in retweet_weibo:
            name, data = preprocess(item['retweet_mid'])
            child_weibo_data[name] = data
            # print name, data
        for item in child_weibo_data:
            if 'parent_name' not in child_weibo_data[item]:
                result.append({
                    'm_id': child_weibo_data[item]['m_id'], 
                    'parent': m_id
                })
            else:
                parent_name = child_weibo_data[item]['parent_name']
                if parent_name in child_weibo_data:
                    parent_id = child_weibo_data[parent_name]['m_id']
                    result.append({
                        'm_id': child_weibo_data[item]['m_id'], 
                        'parent': parent_id
                    })
                    # print parent_id
                else:
                    result.append({
                        'm_id': child_weibo_data[item]['m_id'], 
                        'parent': m_id
                    })
        return result

def preprocess(m_id):
    """返回该微博的m_id, 用户名，及里面//@的第一个人的用户名。"""

    # 查找db.weibo中它的text，得出parent_name
    # 从u_id查找user中它的name

    # 例：
    # name = "爽爷"
    # data = {"m_id": "4", "parent_name": "李雪"}
    con = pymongo.MongoClient('127.0.0.1', 27017)
    db = con.weibodata
    weibo = db.weibo.find_one({'mid': m_id})
    u_id = weibo['uid']    
    name = db.user.find_one({'u_id': u_id})['name']
    
    text = weibo['text']
    tmp = text.decode('utf8') 
    regExp = u'//@[\u4e00-\u9fa5_a-zA-Z0-9_]+:'
    pattern = re.compile(regExp)
    results = pattern.findall(tmp)

    # print text
    if len(results) > 0:
        parent_name = results[0][3:-1]
        data = {'m_id': m_id, 'parent_name': parent_name}
    else:
        data = {'m_id': m_id}
    return name, data   # 二元组

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    app.run(debug=True)

