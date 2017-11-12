import requests
from http import cookiejar
import re
import time
import os.path
from PIL import Image

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
}

session = requests.session()
session.cookies = cookiejar.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")


def get_xsrf():
    '''_xsrf 是一个动态变化的参数'''
    index_url = 'http://www.zhihu.com/'
    index_page = session.get(index_url, headers=headers)
    html = index_page.text
    pattern = r'name="_xsrf" value="(.*?)"'
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]

def get_captcha():
    t = str(int(time.time()*1000))
    # 千万不要在验证码 url 后边加 &lang=cn ，否则会变成让你点倒立文字的验证码
    captcha_url = 'http://www.zhihu.com/captcha.gif?{}&type=login'.format(t)
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)

    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print('请到{}目录查找 captcha.jpg 图片手动输入'.format(os.path.abspath('captcha.jpg')))
    captch = input('请输入验证码：')
    return captch

def is_login():
    url = 'https://www.zhihu.com/settings/profile'
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    return login_code == 200


# 登录函数
def login(password, account):
    ''' 登录时的数据时异步提交的，所以可以分析到对应的 url
    '''
    if re.match(r"^1\d{10}$", account):
        print("手机号登录")
        post_url = 'https://www.zhihu.com/login/phone_num'
        form_data = {
            '_xsrf': get_xsrf(),
            'password':password,
            'phone_num':account,
        }
    else:
        print('邮箱登录')
        post_url = 'https://www.zhihu.com/login/email'
        form_data = {
            '_xsrf': get_xsrf(),
            'password': password,
            'email': account,
        }

    try:
        login_page = session.post(post_url, data=form_data, headers=headers)
        login_code = login_page.text
        print(login_page.status)
        print(login_code)
    except:
        form_data['captcha'] = get_captcha()
        login_page = session.post(post_url, data=form_data, headers=headers)
        login_code = eval(login_page.text)
        print(login_code['msg'])
    session.cookies.save()

if __name__ == '__main__':
    if is_login():
        print('您已经登录')
    else:
        account = input('请输入您的账号：')
        password = input('请输入您的密码：')
        login(password, account)