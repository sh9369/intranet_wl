#!/usr/bin/python
# -*- coding:utf8 -*-
# @Time    : 2018/8/20 18:38
# @Author  : songh
# @File    : wl_main.py
# @Software: PyCharm
import datetime,time
import common_tools
import config_tools
import whitelist_check

def start(stime,dtime,host,port,indx,aggs):
    # new running procedure
    updatetime = datetime.datetime.now()
    startTime = stime
    # beginTime = datetime.datetime.strptime(begin, '%Y-%m-%d %H:%M:%S')
    # flgnum is the running times per day
    flgnum = 0
    # get format: "yy-mm-dd"
    tday = datetime.datetime.now().date()
    # runtime=0 # elapsed time of whole process,included check and merge
    mylog = common_tools.getlog()
    while True:
        while datetime.datetime.now() < startTime:
            # print('time sleep...')
            mylog.info("Time sleeping ...")
            time.sleep((startTime - datetime.datetime.now()).total_seconds())
        try:
            # check interval time is 5mins
            all_IP = whitelist_check.start(startTime,dtime, indx, aggs, host, port, tday)
            startTime = startTime + dtime
            flgnum += 1
            # runtime=time.clock()-st# get the time of whole process
        except Exception, e:
            # print e
            mylog.error(e)

if __name__ == '__main__':
    # get params
    discard,deltatime=config_tools.getTimes()
    if (discard.lower() == 'now'):
        starttime = time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        starttime = datetime.datetime.strptime(discard, '%Y-%m-%d %H:%M:%S')

    start(starttime,deltatime)