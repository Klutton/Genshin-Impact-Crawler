# Genshin Impact Crawler

 Happy April Fool's Day, to celebrate, I wrote a py crawler that downloads images, audios and profiles using only requests package('also openpyxl to save excel using pandas')
 
 我有女朋友了！愚人节快乐！我还是单身狗🙂  为了庆祝愚人节以及作为原批的实力展示，我只用了python和requests库爬取了图片，音频和个人设定（其实还有openpyxl用来保存excel文件）

### dependencies

```
pip install requests, openpyxl
```

### output

- directories: images, audios, profiles
- log: logs.log

Naming issue, all names are Chinese, because this website targets towards Chinese users. 

~~*If Chinese is not your mother language, consider this as an opportunity to learn Chinese?*~~ 

The following content contains inside jokes that are specific to China. There is no malicious intent, please do not misunderstand.

![](https://s3.bmp.ovh/imgs/2023/04/01/9d37b6db6d478961.jpg)

### 写码体验

雪豹闭嘴，上面怎么一直在写英语？你不爱国吗？

我们原神的反爬做得就是好，没有前后端分离，js脚本看起来像是自动生成的，是为了加载动画流畅么？

仅使用requests库只能获取到脚本内容，是完全没法作为html文件使用beautifulsoup解析的！怎么办呢？难道我要用无头浏览器？或者我又要再配置并运行一个js平台？那岂不是增加了环境配置的麻烦！显得我们原神玩家很low!

因此我拿出我看家本领if else，给脚本洗了一遍数据，把关键内容从字符串中摘出来！期间还有特别蠢比的问题就是很莫名其妙的代码混淆（你这个算是混淆吗？）

```javascript
cv:[
    {
        name:g,
        audio:
        [
            "https:\u002F\u002Fwebstatic.mihoyo.com\u002Fupload\u002Fop-public\u002F2020\u002F02\u002F20\u002F987e7000667c567a29f9abc3d14bb0d5_2911413560906889269.mp3",
            "https:\u002F\u002Fwebstatic.mihoyo.com\u002Fupload\u002Fop-public\u002F2020\u002F02\u002F20\u002F5da4d36bbe53fe5fcd3ce14782cc84ab_5501045953849136389.mp3",
            "https:\u002F\u002Fwebstatic.mihoyo.com\u002Fupload\u002Fop-public\u002F2020\u002F02\u002F20\u002F5a7100c2fbc68452006afa4dbd7f757a_4139067739853698717.mp3"]},
    {
        name:"松冈祯丞",
        audio:[
            "https:\u002F\u002Fwebstatic.mihoyo.com\u002Fupload\u002Fop-public\u002F2020\u002F02\u002F20\u002F402c89fffc5886be0ecf3e5200b3f999_2355186733651359703.mp3",
            "https:\u002F\u002Fwebstatic.mihoyo.com\u002Fupload\u002Fop-public\u002F2020\u002F02\u002F20\u002F9eacc534d687e3f7f26a470b5145783f_38915976500974336.mp3",
            "https:\u002F\u002Fwebstatic.mihoyo.com\u002Fupload\u002Fop-public\u002F2020\u002F02\u002F20\u002Fb2ecb0debf8954bb35925e6bacc06e6c_4187366727687115513.mp3"
            ]
        }
    ]
("","中","日",true,false,{},"kinsen","唐雅菁",0)
```

聪明的小伙伴们猜到了g是什么吗？哇哦，g原来是js脚本最后一段的第七个变量，kinsen诶，为什么要这么搞呢？小编也不知道为什么。

因此我还得在我的垃圾匹配代码里加上特殊情况的处理😄

```python
func_list = content[content.rfind('(')+1: content[:content.rfind(')')].rfind(')')]
    func_list = json.loads('['+func_v+']')
    temp = new_content.split('{title:')[1:]
if xorg[xorg.find('name:')+5] == 'h':
    cn_name = func_list[-2]
if xorg[xorg.find('name:')+5] == 'i':
    cn_name = func_list[-1]
```

从requests.content获取的裸数据竟然是utf-8里夹杂着Unicode，这样你才知道你拿到的是脚本，你选择了decode，你获得了带着Unicode的中文；你选择了decode('unicode_escape')，你获得了带着编码的呃，有符号的字符串？

所以只能先decode()再自己转换辣，感谢ltkk大学霸教我

```python
def convert(s: str):
    pattern = re.compile(r'\\u[0-9a-fA-F]{4}')
    res = pattern.sub(lambda x: chr(int(x.group()[2:], 16)), s)
    soup = bs(res, 'html.parser')
    res = soup.text.replace('\\n', '\n')
    logging.info('converted-----'+res)
    return res
```

经过这么折腾终于可以把数据洗好辣

我构建了一个类用来操作数据

```python
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
```

一定要记得通过 cha = Character()来new一个对象哦，我太笨了不会new对象，检查的时候排查出来的

最后拿着url将获取的数据以二进制流形式存储在本地即可了

```python
def download(url: str, _dir: str, name: str):
    logging.info(f'saving file: {_dir + name}, from {url}')
    image = r.get(url).content
    with open(_dir+name, 'wb') as f:
        f.write(image)
    logging.info(f'file saved: {_dir + name}')
    return
```

哦我实在是太贴心了还准备有日志，真是个细心的男孩子

顺带一提保存下来的excel没有自动排版看着真难看！

### 你闲得做这个干嘛？你做这些什么目的？

我才不会告诉你我是为了帮一个网上认识的不选计算机的女生做python作业才写这个爬虫呢！

捏妈妈的为什么原神这网页爬着这么费劲啊，如果要交作业的话肯定要做到环境好配，你学python都跑到谷歌内核nodejs去了那老师怎么给你批作业？！😡😡😡

Q：哦那你的女网友肯定很高兴吧

- 🤡四月一日凌晨零点截止，我高估自己了，晚上十点一刻才开始写，现在改口说这是愚人节代码了，你这废物能找到女朋友真对不起别人。~~幸好她不会上GitHub还很谅解我这是我最后的尊严了~~

什么小丑啊🤣👉愚人节人家该出去的都出去跟女孩玩，不出去的在宿舍和好兄弟和女生打游戏你在这儿写你这个没人看的b代码太丢面了

我们原神玩家的精神状态是这样的😁👍下面我要去弄今天截止的实验报告了😁👍🤣👉🤡🤡🤡
![](https://s3.bmp.ovh/imgs/2023/04/01/50323922e605e6e5.jpg)