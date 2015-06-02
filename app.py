#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from utils import helloworld    # 这是个import我们写的模组的例子
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    helloworld.hello()  # 这是个调用我们写的函数的例子

    if request.method == 'POST':
        json_data = request.get_json()  # 读取POST请求中的JSON
        # 设计文件中定义传入格式: {"m_id": "104967351"}
        m_id = json_data["m_id"]    # 得到m_id

        # 待实现：处理m_id并返回所要求的结构

        return make_retweet_tree(m_id)

    else:
        return 'Hello World!'

def make_retweet_statistics(m_id):
    # 在db.retweet中找这条信息是否转发了其他信息
    # 若是：则它不是祖先节点，在表项中找它的祖先节点
        # 在db.retweet中找它的祖先微博original_mid
        # 递归～ return make_retweet_statistics(original_mid)

    # 若不是：则它是祖先节点
        u_ids = []
        # 在db.retweet中找祖先微博的m_id为这个m_id的微博
        # 得到一个集合
        # 对于集合中的每条微博：
            # 将u_id放入u_ids列表中

        # 对于u_ids中的每一个u_id:
            # 在user里面查找他的信息
            # 使用几个计数器，比如如果性别为男性则male += 1, 有通过验证则verified += 1等
        
        # 每个计数器的值除以len(u_ids)即得出比例

def make_retweet_tree(m_id):
    result = []

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

def preprocess(m_id):
    """返回该微博的m_id, 用户名，及里面//@的第一个人的用户名。"""

    # 查找db.weibo中它的text，得出parent_name
    # 从u_id查找user中它的name

    # 例：
    # name = "爽爷"
    # data = {"m_id": "4", "parent_name": "李雪"}
    return name, data   # 二元组

if __name__ == '__main__':
    app.run(debug=True)
