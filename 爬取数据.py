import json
import re
from bs4 import BeautifulSoup as bs
import requests as r
import os
import pandas as pd
import logging
# 你需要pip install openpyxl

# 有人可能就说了： 你闲的蛋疼吧， 拿个无头浏览器早解决了， 弄一堆字符串处理累死你！
# 一个是无头浏览器要配环境麻烦， 还有一个就是我是傻逼， 忘了这茬了
# 不过确实无头浏览器很麻烦

logging.basicConfig(filename='logs.log',level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

city = {
    '蒙德城': 'mondstadt',
    '璃月港': 'liyue',
    '稻妻城': 'inazuma',
    '须弥城': 'sumeru'
}
original_url = r'https://ys.mihoyo.com/main/character/'

image_directory = r'./images'
audio_directory = r'./audios'
profile_directory = r'./profiles'


class Character:
    def __init__(self):
        self.title: str
        self.icon: str
        self.cover1: str
        self.cover2: str
        self.name: str
        self.attr: str
        self.intro: str
        self.sen: str
        self.cv_Chinese: list
        self.cv_Japanese: list


def convert(s: str):
    pattern = re.compile(r'\\u[0-9a-fA-F]{4}')
    res = pattern.sub(lambda x: chr(int(x.group()[2:], 16)), s)
    soup = bs(res, 'html.parser')
    res = soup.text.replace('\\n', '\n')
    logging.info('converted-----'+res)
    return res


def process_properties(obj, operation):
    for attr in obj.__dict__:
        if not callable(getattr(obj, attr)) and not attr.startswith("__"):
            v = getattr(obj, attr)
            if type(v) == str:
                new_value = operation(v)
                setattr(obj, attr, new_value)
            if type(v) == list:
                temp = []
                for x in range(0, len(v[1])):
                    temp.append(operation(v[1][x]))
                v[0] = operation(v[0])
                v[1] = temp
                setattr(obj, attr, v)


def solo_filter(org: str, spe: str):
    # print(org)
    i = org.find(spe)
    st = org[i:].find(':')
    e = org[i + st + 1:].find(',')
    res = org[i + st + 2: i + st + e]
    # print(res)
    return res


def get_cv(org: str, func_list: list):
    xorg = org[org.find('cv:[{')+5:]
    cn_name = solo_filter(xorg, 'name')
    if xorg[xorg.find('name:')+5] == 'h':
        cn_name = func_list[-2]
    if xorg[xorg.find('name:')+5] == 'i':
        cn_name = func_list[-1]
    l = xorg[xorg.find('[')+1: xorg.find(']')]
    l = l.replace('"', '').split(',')
    res = {'cn': [cn_name, l]}
    i = xorg.find('name') + 4
    new_org = xorg[i:]
    jp_name = solo_filter(new_org, 'name')
    l = new_org[new_org.find('[') + 1: new_org.find(']')]
    l = l.replace('"', '').split(',')
    res['jp'] = [jp_name, l]
    # print(res['cn'], res['jp'])
    return res


results = {}

for key, value in city.items():
    results[key] = []
    rep = r.get(original_url + value)
    content = str(rep.content.decode('utf-8'))
    content = content.encode('unicode_escape').decode('unicode_escape')
    new_content = content[content.find('charList:') + 9: content.rfind(']') + 1]

    func_v = content[content.rfind('(')+1: content[:content.rfind(')')].rfind(')')]
    func_v = json.loads('['+func_v+']')
    # print(func_v)
    temp = new_content.split('{title:')[1:]
    for s in temp:
        # print(s)
        cha = Character()
        cha.title = solo_filter(':'+s, ':')
        cha.icon = solo_filter(s, 'icon:')
        cha.cover1 = solo_filter(s, 'cover1:')
        cha.cover2 = solo_filter(s, 'cover2:')
        cha.name = solo_filter(s, 'name:')
        cha.attr = solo_filter(s, 'attr:')
        cha.intro = solo_filter(s, 'intro:')
        cha.sen = solo_filter(s, 'sen:')
        cv = get_cv(s, func_v)
        cha.cv_Chinese = cv['cn']
        cha.cv_Japanese = cv['jp']
        process_properties(cha, convert)
        # print('-'*20)
        # print('\n\n')
        # print(cha.title)
        results[key].append(cha)
        # print(results)

    # 至此，我们获取了所有需要的信息，下面我们需要整理数据并保存下来
    # title icon cover1 cover2 name attr intro sen cv {name audio}


def download(url: str, _dir: str, name: str):
    logging.info(f'saving file: {_dir + name}, from {url}')
    image = r.get(url).content
    with open(_dir+name, 'wb') as f:
        f.write(image)
    logging.info(f'file saved: {_dir + name}')
    return


for _city, characters in results.items():
    # 我们使用角色所属地区和角色名字作为文件夹索引保存
    for cha in characters:
        title = cha.title
        print(title)
        imgdir = image_directory + '/' + _city + '/' + title + '/'
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)
        auddir = audio_directory + '/' + _city + '/' + title + '/'
        if not os.path.exists(auddir):
            os.makedirs(auddir)
        for attr in cha.__dict__:
            if not callable(getattr(cha, attr)) and not attr.startswith("__"):
                v = getattr(cha, attr)
                if type(v) == str:
                    if v.endswith('.png'):
                        download(v, imgdir, attr+'.png')
                if type(v) == list:
                    cv_name = v[0]
                    d = auddir+cv_name+'/'
                    if not os.path.exists(d):
                        os.makedirs(d)
                    for i, c in enumerate(v[1]):
                        download(c, d, cv_name+'-'+str(i)+'.mp3')

        # 下载自此完成， 下面保存excel文件
        # 每个角色都保存一个excel文件， 便于浏览
        # 分开写提高代码可读性， 不过貌似损失性能了诶
        # 问题不大， 这个程序性能瓶颈在网络和io上
        # 另外提一嘴 ， 这个obj.__dict__真好用

        exceldir = profile_directory + '/' + _city + '/'
        excel_name = profile_directory + '/' + _city + '/' + title + '.xlsx'
        data = {}
        for attr in cha.__dict__:
            if not callable(getattr(cha, attr)) and not attr.startswith("__"):
                v = getattr(cha, attr)
                if type(v) == str:
                    data[attr] = [v]
                if type(v) == list:
                    data[attr] = [v[0]]
                    for i, c in enumerate(v[1]):
                        data[attr + '-' + str(i)] = [c]
        # print(data)
        df = pd.DataFrame.from_dict(data)
        if not os.path.exists(exceldir):
            os.makedirs(exceldir)
        df.to_excel(excel_name, )
print('爬取结束，再见原批，快滚吧')
logging.info('All tasks completed')
