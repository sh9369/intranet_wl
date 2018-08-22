#!/usr/bin/python
# -*- coding:utf8 -*-
# @Time    : 2018/8/20 19:48
# @Author  : songh# @File    : whitelist_check.py
# @Software: PyCharm
from elasticsearch import Elasticsearch
import datetime,time
import common_tools
import config_tools

# ES class: get es data / insert into es
class ESclient(object):
	def __init__(self,server='192.168.0.122',port='9222'):
		self.__es_client=Elasticsearch([{'host':server,'port':port}])

	def get_es_ip(self,index,gte,lte,aggs_name,time_zone,size=500000):
		search_option={
            "size": 0,
            "query": {
              "bool": {
                "must": [
                    {
                        "query_string": {
                            "query": "unknown_conn:0",
                            "analyze_wildcard": True
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": gte,
                                "lte": lte,
                                "format": "yyyy-MM-dd HH:mm:ss",
                                "time_zone":time_zone
                            }
                        }
                    }
                ],
                "must_not": []
              }
            },
            "_source": {
                "excludes": []
            },
            "aggs": {
                "getSip": {
                    "terms": {
                        "field": aggs_name,
                        "size": size,
                        "order": {
                            "_count": "desc"
                        }
                    }
                }
            }
        }

		search_result=self.__es_client.search(
			index=index,
			body=search_option
			)
		clean_search_result = search_result['aggregations']["getSip"]['buckets']
		ip = []
		for temp in clean_search_result:
			ip.append(temp['key'])
		return ip

	def es_index(self,doc):
		'''
		数据回插es的alert-*索引
		'''
		ret = self.__es_client.index(
			index = 'alert-{}'.format(datetime.datetime.now().strftime('%Y-%m-%d')),
			doc_type = 'netflow_v9',
			body = doc
			)

#get white list
def get_wl(logs):
    logs.info("start read white list.")
    filename=config_tools.get_file()
    datapath=config_tools.get_data_path()+ filename
    wl_data=common_tools.readdata(datapath)
    logs.info("white list size:{0}".format(len(wl_data)))
    return wl_data

# change subnet to range type
def subnet_to_range(subnet):
    subnet_range=[]
    for sn in subnet:
        tmp_range=common_tools.subnet_range(sn)
        subnet_range.append(tmp_range)
    return subnet_range

# check_func()
def check_func(esdata,wldata,mylogs):
    mylogs.info("start check!")
    # separate white list data
    full_data,range_data,subnet_data=common_tools.separate_ip(wldata)
    # start match
    reamain_data=esdata
    # first: full match
    if(full_data):
        remain_data=list(set(esdata)-set(full_data))
    if (subnet_data):  # subnet: 1->lpm; 2-> subnet大于24用range
        # serapate the subnet(8/16-24/->lpm, others -> range)
        mylogs.info("check lpm...")
        remain_sub, remain_data = common_tools.lpm_match(subnet_data, remain_data)
        remain_range = subnet_to_range(remain_sub)
        mylogs.info("lpm finish!")
    else:
        remain_range=[]
    #merge list
    # print type(range_data)
    # print type(remain_range)
    range_data=list(set(range_data+remain_range))
    mylogs.info("range date size :{0}".format(len(range_data)))
    if(range_data):
        mylogs.info("check range data...")
        remain_data=common_tools.range_data_match(range_data,remain_data)
        mylogs.info("range_data finish!")
    return remain_data



# start
def start(sTime,deltatime, indx, aggs_name, iserver, iport, tday):
    # new check function
    mylog = common_tools.getlog()
    try:
        # print("Starting check command."), time.ctime()
        mylog.info("[Starting check command.Time is:{}]".format((sTime).strftime('%Y-%m-%d %H:%M:%S')))
        # set time zone
        gte = (sTime - deltatime).strftime('%Y-%m-%d %H:%M:%S')
        lte = (sTime).strftime('%Y-%m-%d %H:%M:%S')
        time_zone = ''
        if (time.daylight == 0):  # 1:dst;
            time_zone = "%+03d:%02d" % (-(time.timezone / 3600), time.timezone % 3600 / 3600.0 * 60)
        else:
            time_zone = "%+03d:%02d" % (-(time.altzone / 3600), time.altzone % 3600 / 3600.0 * 60)
        # timestamp is used to insert function
        timestamp = (sTime).strftime('%Y-%m-%dT%H:%M:%S.%f') + time_zone
        # get es data
        es=ESclient(server=iserver,port=iport)
        es_data=es.get_es_ip(indx,gte,lte,aggs_name,time_zone)
        mylog.info("es data size:{0}".format(len(es_data)))
        mylog.info("es data :{0}".format(es_data))
        # get white list
        wlist=get_wl(mylog)
        # check
        all_ip=[]
        if(wlist and es_data):# get data
            all_ip = check_func(es_data,wlist,mylog)
        elif(wlist==False):
            mylog.error(" NO white list!")
        # print("check finish."), time.ctime()
        mylog.info("{0}check finish.{1}".format("=" * 30, "=" * 30))
        # print"="*40
        # insert
        for ii in all_ip:
            # create data stracture
            doc={}
            doc["aggs_name"]=ii
            doc["type"]="suspect_ip"
            doc["desc_type"]="[suspect_ip] Request of suspect IP detection."
            doc["subtype"]="fake_ip"
            doc["desc_subtype"]="Suspect IP is out of white list."
            doc["level"]="info"
            doc['@timestamp']=timestamp
            doc['index']='tcp-*'
            es.es_index(doc)
    except Exception,e:
        mylog.error("check_start error!")

# example:
if __name__ == '__main__':
    start()