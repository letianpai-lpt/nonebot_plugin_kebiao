# nonebot_plugin_kebiao
实现对正方教务系统课表的推送

别的教务系统应该不支持

比较菜不会写别的配置,也不会传pip里,建议直接复制代码到本地插件文件夹使用

## 主要是__init__.py和qqinfo.json文件
## json文件里写使用人的QQ,课表文件路径,开学时间和所在城市,

## __init__.py文件最开始指定一下qqinfo.json的路径和你的和风天气个人开发者API

就这样吧,我是菜鸡

# 手动抓课表的方法

先到课表页面按F12打开开发者界面

![1](https://user-images.githubusercontent.com/96228495/183881616-6f10141f-cad4-4f6b-bd01-b2d303776155.png)

然后再点一次查询按钮让数据加载一下

![2](https://user-images.githubusercontent.com/96228495/183881799-3c4b290a-d921-48d2-9749-c60cf3817353.png)

点开第一个,对准最上面的直接复制值,然后粘到你的课表文件json里

全凭兴趣爱好写的,代码肯定细碎,介意可以自己优化优化或者完全自己重写一个
