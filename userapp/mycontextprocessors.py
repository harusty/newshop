# coding=utf-8

def getUserInfo(requset):
    return {
        'suser':requset.session.get('user',None)
    }