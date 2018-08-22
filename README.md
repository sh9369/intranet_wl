# personal_respo2
<br>
本程序GitHub地址为：https://github.com/sh9369/personal_respo2<br>

# 前言<br>
本程序用于本地内网白名单检测，针对imap中记录的sip地址进行检查，若sip不存在白名单内，则发出告警信息，并将告警信息写入ES中。<br>

本程序需在Linux环境下运行，基于python 2.7语法规范编写，主要的相关依赖包如下：
json、logging、datetime、time、elasticsearch、ConfigParser、socket、struct、re、requests、bs4、lxml

