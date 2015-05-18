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

        return 'Not yet implemented'

    else:
        return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
