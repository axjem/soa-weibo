SOA 微博转发信息模块
==========

如何开发（以Linux为例）
-----

### 配置
1. git clone这个repo.
2. 安装python和pip.
3. 如果你不使用virtualenv：`pip install Flask`. 如果你使用virtualenv:
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
4. 确保mongo能够连接到正确的数据库weibodata

执行`python app.py`，如果出现`Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`那么就没问题啦。

### 运行方式
- 打开浏览器：127.0.0.1:5000
    - 可使用POST传入JSON格式的数据，如{"m_id": "104967351"}
    - 可以不用传m_id，因为有默认值
    - 也可以通过get显示在url上传递m_id，比较好的m_id可以在good_data中得到。
        - 什么叫比较好？
        - 数据库中绝大多数微博都只有一级转发，就是parent -> child
        - 而经过测试good_data中的m_id，作为original_mid，可以有两级转发，即grandparent -> parent -> child
    - 如：127.0.0.1:5000?m_id=3504697396195494

### 文件结构说明

- app.py: 运行程序的主文件。
- data/: 
	- good_data：比较好的m_id.
- utils/: 自己写的模组，包含自己写的各种函数，比如把txt文件变成pkl数据结构，或者读取pkl文件的函数，都写在这里面的.py文件里。
	- \_\_init\_\_.py: 用来让Python认得这个目录的，这个文件可以不予理会，不要修改。
    - helloworld.py: 一个函数的例子。
