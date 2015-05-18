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

执行`python app.py`，如果出现`Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)`那么就没问题啦。

### 文件结构说明

- data/: 微博转发数据，*.txt是原始数据，*.pkl是Python数据结构文件（见pickle模块）。
	- test-weibo-rt-data.txt: 测试用的原始数据。
	- test_weibo_rt_dict.pkl: 测试用的数据结构。
- utils/: 自己写的函数，比如把txt文件变成pkl数据结构，或者读取pkl文件的函数，都写在这里面的.py文件里。
	- __utils__.py: 用来让Python认得这个目录的，这个文件可以不予理会，不要修改。
- app.py: 运行程序的主文件。