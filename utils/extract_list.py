# -*- encoding: utf8 -*-
import pickle, pprint, sys

def getUserList(srcFile, reTweetList, userList, mid):
    f = open(srcFile, 'rb')
    data = pickle.load(f)
    f.close()
    if data.has_key(mid):
        if len(userList) == 0:      # 加上原始用户
            userList.add(data[mid][0])
        for item in data[mid][1]:
            userList.add(item[1])
            reTweetList.append(item[0])
    

def getData(srcFile, reTweetList, userList, origin_mid):
    reTweetList.append(origin_mid)
    getUserList(srcFile, reTweetList, userList, origin_mid)
    for current_mid in reTweetList[1:]:
        getUserList(srcFile, reTweetList, userList, current_mid)

userList = set()
reTweetList = []
srcFile = 'test_weibo_rt_dict_modified.pkl'
origin_mid = '1'
getData(srcFile, reTweetList, userList, origin_mid)

print 'userList: ',
for item in userList:
    print item,
print ' '

print 'reTweetList: ',
for item in reTweetList:
    print item,
print ' '
