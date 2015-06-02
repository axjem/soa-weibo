## 运行方式
- 确保mongo能够连接到正确的数据库weibodata
- python app_by_6z.py
- 打开浏览器：127.0.0.1:5000
    - 可以不用传m_id，因为有默认值
    - 也可以通过get显示在url上传递m_id，比较好的m_id可以在good_data中得到。
        - 什么叫比较好？
        - 数据库中绝大多数微博都只有一级转发，就是parent -> child
        - 而经过测试good_data中的m_id，作为original_mid，可以有两级转发，即grandparent -> parent -> child
    - 如：127.0.0.1:5000?m_id=3504697396195494

