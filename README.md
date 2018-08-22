# personal_respo2
<br>
本程序GitHub地址为：https://github.com/sh9369/personal_respo2<br>

# 前言<br>
本程序用于本地内网白名单检测，针对imap中记录的sip地址进行检查，若sip不存在白名单内，则发出告警信息，并将告警信息写入ES中。<br>

本程序需在Linux环境下运行，基于python 2.7语法规范编写，主要的相关依赖包如下：
json、logging、datetime、time、elasticsearch、ConfigParser、socket、struct、re、os<br>

# 使用<br>
## 下载<br>
git命令或zip下载到本地目录。<br>
## 配置文件<br>
根据需要修改配置文件中的各项参数值，请务必将ES_info设置准确。<br>
## 白名单设置<br>
请在./project/data/下修改whitelist.txt文件，输入本地白名单IP，并且以英文','作为分割；<br>
也可以在配置文件中修改filename值为个人白名单的文件名，然后将个人白名单文件复制于data目录下。<br>
## 启动<br>
请使用以下命令启动脚本：<br>
```
nohup python wl_main.py &
```
## 查看日志<br>
日志文件存放在./project/data/log/下。<br>
