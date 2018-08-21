#!/usr/bin/python
# -*- coding:utf8 -*-
# @Time    : 2018/8/20 18:39
# @Author  : songh
# @File    : config_tools.py
# @Software: PyCharm

# Functions for config.conf
import ConfigParser
import re,datetime,os
import common_tools

# ============predefine================
cp = ConfigParser.ConfigParser()
cp.read("config.conf")
section = cp.sections()
# print section
# ===================================

def getTimes():
    # start time
    timekey1=cp.options("time_info")
    starttime=cp.get("time_info",timekey1[0])
    #check frequency
    times=cp.getint("time_info",timekey1[1])
    deltatime=datetime.timedelta(minutes=times)
    return starttime,deltatime

def get_ES_info():
    # ES information
    source_store_path_key=cp.options("ES_info")
    #value=cp.get(sectionName,keyword)
    server=cp.get('ES_info',source_store_path_key[0])
    dport=cp.get('ES_info',source_store_path_key[1])
    indx=cp.get('ES_info',source_store_path_key[2])
    aggs_name=cp.get('ES_info',source_store_path_key[3])
    return server,dport,indx,aggs_name

def get_func():
    parse_blacklist_key = cp.options("parse_blacklist")
    #function module
    moudle_func = cp.get("parse_blacklist", parse_blacklist_key[0])
    moudle_list = moudle_func.split(',')
    # print moudle_list
    moudle_name = {}
    for temp in moudle_list:
        fname,ftimes=temp.split(":")
        fname = fname.strip()
        # as a dict: key is filename,value is the update frequency
        moudle_name[fname]=ftimes
    return moudle_name

def get_data_path():
    #source_data_path
    source_data_path_key = cp.options('data_path')
    source_data_path=cp.get('data_path', source_data_path_key[0])
    # depend on os, windows: nt ; linux : posix
    if(os.name == 'nt'):
        new_path=source_data_path.replace('/','\\')
        return new_path
    return source_data_path