#!/usr/bin/python
# -*- coding:utf8 -*-
# @Time    : 2018/8/20 18:39
# @Author  : songh
# @File    : common_tools.py
# @Software: PyCharm
import logging,os,re,socket,struct
from logging.handlers import TimedRotatingFileHandler
import lpm

# log function
def getlog():
	mylog = logging.getLogger()
	if len(mylog.handlers) == 0:  # just only one handler
		level = logging.INFO
		filename = os.getcwd() + os.path.sep + 'data' + os.path.sep +'log'+ os.path.sep+ 'testlog'
		format = '%(asctime)s %(levelname)-8s: %(message)s'
		hdlr = TimedRotatingFileHandler(filename, "midnight", 1, 0)
		hdlr.suffix = "%Y%m%d.log"
		fmt = logging.Formatter(format)
		hdlr.setFormatter(fmt)
		mylog.addHandler(hdlr)
		mylog.setLevel(level)
	return mylog

def readdata(path):
    if(os.path.exists(path)):
        #exists
        with open(path,'r')as fp:
            data=fp.read().split(',')
        return data
    else:
        return False

def separate_ip(iplist):
    regex1 = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    regex2 = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    regex3 = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}$')
    full_match = []
    rangement = []
    subnet = []
    for ip_element in iplist:
        if regex1.match(ip_element):
            full_match.append(ip_element)
        elif regex2.match(ip_element):
            rangement.append(ip_element)
        elif regex3.match(ip_element):
            subnet.append(ip_element)
    # print len(full_match_dict)
    # print len(segment)
    # print len(subnet)
    # saveAsJSON(date, full_match, path, 'full_match')
    # saveAsJSON(date, segment, path, 'segment')
    # saveAsJSON(date, subnet, path, 'subnet')
    return full_match,rangement,subnet

# range data match
def range_data_match(rangedata,esdata):
    # firstly, change ip to int
    iplong=[]
    for irange in rangedata:
        tmplist=[]
        tmp=rangedata.split('-')
        startip=socket.ntohl(struct.unpack("I",socket.inet_aton(tmp[0]))[0])
        endip=socket.ntohl(struct.unpack("I",socket.inet_aton(tmp[1]))[0])
        tmplist.append(startip)
        tmplist.append(endip)
        iplong.append(tmplist)
    #secondly, sorted
    new_range=sorted(iplong,key=lambda x:x[0])
    # finally , binary search
    remain_data=[]
    rangeLen = len(new_range)
    for ips in esdata:
        ip_es_num = socket.ntohl(struct.unpack("I",socket.inet_aton(str(ips)))[0])
        # Binary Search
        nlow=0
        nhigh=rangeLen-1
        while(nlow<=nhigh):
            nmid=(nlow+nhigh)/2
            subnet_num=new_range[nmid][1]# [start,end]
            if(subnet_num[0]<=ip_es_num<=subnet_num[1]):
                # matched
                break
            elif(subnet_num[0]>ip_es_num):
                nhigh=nmid-1
            elif(subnet_num[1]<ip_es_num):
                nlow=nmid+1
        if(nlow>nhigh):
            remain_data.append(ips)
    return remain_data

#===== zhou ===========
def ip_split_num(ip):
    ip_num = ip.split('.')
    for i in range(len(ip_num)):
        ip_num[i] = int(ip_num[i])
    return ip_num

def subnet_to_binary(num):
    nm_binary = num*'1'+(32-num)*'0'
    #socket.inet_ntoa(struct.pack('I',socket.ntohl(int(nm_binary,2)))).split('.')  -> nm_num
    nm_num = []
    for i in range(4):
        temp =  nm_binary[8*(i):8*(i+1)]
        ip_pot = 0
        for j in range(len(temp)):
            ip_pot = ip_pot + (int(temp[j])*(2**(7-j)))
            if j == 7:
                nm_num.append(int(ip_pot))
    return nm_num
# change subnet to range
def subnet_range(subnet):
    subnet_split = subnet.split('/')
    ip_num = ip_split_num(subnet_split[0])
    netMask = int(subnet_split[1])
    nm_num = subnet_to_binary(netMask)
    firstadr = []
    lastadr = []
    ip_range = []
    if netMask == 31:
        firstadr.append(str(ip_num[0] & nm_num[0]))
        firstadr.append(str(ip_num[1] & nm_num[1]))
        firstadr.append(str(ip_num[2] & nm_num[2]))
        firstadr.append(str(ip_num[3] & nm_num[3]))

        lastadr.append(str(ip_num[0] | (~ nm_num[0] & 0xff)))
        lastadr.append(str(ip_num[1] | (~ nm_num[1] & 0xff)))
        lastadr.append(str(ip_num[2] | (~ nm_num[2] & 0xff)))
        lastadr.append(str(ip_num[3] | (~ nm_num[3] & 0xff)))
        begin_addr = '.'.join(firstadr)
        end_addr = '.'.join(lastadr)
        begin_int=socket.ntohl(struct.unpack("I",socket.inet_aton(begin_addr))[0])
        end_int = socket.ntohl(struct.unpack("I", socket.inet_aton(end_addr))[0])
        ip_range.append(begin_int)
        ip_range.append(end_int)

    elif netMask == 32:
        firstadr.append(str(ip_num[0]))
        firstadr.append(str(ip_num[1]))
        firstadr.append(str(ip_num[2]))
        firstadr.append(str(ip_num[3]))

        lastadr.append(str(ip_num[0]))
        lastadr.append(str(ip_num[1]))
        lastadr.append(str(ip_num[2]))
        lastadr.append(str(ip_num[3]))
        begin_addr = '.'.join(firstadr)
        end_addr = '.'.join(lastadr)
        begin_int=socket.ntohl(struct.unpack("I",socket.inet_aton(begin_addr))[0])
        end_int = socket.ntohl(struct.unpack("I", socket.inet_aton(end_addr))[0])
        ip_range.append(begin_int)
        ip_range.append(end_int)
    else:
        lastadr.append(str(ip_num[0] | (~ nm_num[0] & 0xff)))
        lastadr.append(str(ip_num[1] | (~ nm_num[1] & 0xff)))
        lastadr.append(str(ip_num[2] | (~ nm_num[2] & 0xff)))
        lastadr.append(str((ip_num[3] | (~ nm_num[3] & 0xff))-1))

        firstadr.append(str(ip_num[0] & nm_num[0]    ))
        firstadr.append(str(ip_num[1] & nm_num[1]    ))
        firstadr.append(str(ip_num[2] & nm_num[2]    ))
        firstadr.append(str((ip_num[3] & nm_num[3])+1))
        begin_addr = '.'.join(firstadr)
        end_addr = '.'.join(lastadr)
        begin_int=socket.ntohl(struct.unpack("I",socket.inet_aton(begin_addr))[0])
        end_int = socket.ntohl(struct.unpack("I", socket.inet_aton(end_addr))[0])
        ip_range.append(begin_int)
        ip_range.append(end_int)
    return ip_range
#===== zhou ===========


#lpm match,return subnet(>24)
def lpm_match(subnet_data,remain_data):
    mylog = getlog()
    lpm.init()
    sn_gte24 = []
    # ip_subnet = subnet.keys()
    for sn in subnet_data:
        subnet_split = sn.split('/')
        ip_num = ip_split_num(subnet_split[0])
        netMask = int(subnet_split[1])
        # if (sn == '192.168.0.0/16' or sn == '172.16.0.0/12' or sn == '10.0.0.0/8'):  # 略过私网
        #     continue
            # return 'False'
        if(netMask<=8):
            idx = pow(2, 8 - netMask) - 1
            # print idx
            ip_base = ip_num[0] & (255 - idx)
            i = 0
            while (i <= idx):
                newip1 = []
                ip_num[0] = ip_base + i
                newip1.append(str(ip_num[0]))
                newip1.append('*')
                newip1.append('*')
                newip1.append('*')
                ipstr1 = '.'.join(newip1)
                # print ipstr1
                lpm.insert_rule(ipstr1)
                i = i + 1
        elif (netMask <= 16):  #
            idx = pow(2, 16 - netMask) - 1
            # print idx
            ip_base = ip_num[1] & (255 - idx)
            i = 0
            while (i <= idx):
                newip1 = []
                ip_num[1] = ip_base + i
                newip1.append(str(ip_num[0]))
                newip1.append(str(ip_num[1]))
                newip1.append('*')
                newip1.append('*')
                ipstr1 = '.'.join(newip1)
                # print ipstr1
                lpm.insert_rule(ipstr1)
                i = i + 1
        elif (netMask <= 24):
            idx = pow(2, 24 - netMask) - 1
            # print idx
            ip_base = ip_num[2] & (255 - idx)
            i = 0
            while (i <= idx):
                newip1 = []
                ip_num[2] = ip_base + i
                newip1.append(str(ip_num[0]))
                newip1.append(str(ip_num[1]))
                newip1.append(str(ip_num[2]))
                newip1.append('*')
                ipstr1 = '.'.join(newip1)
                # print ipstr1
                lpm.insert_rule(ipstr1)
                i = i + 1
        elif (netMask > 24):  # range match
            sn_gte24.append(sn)

    mylog.info('gte24 size:%d' % len(sn_gte24))
    # match
    new_remain=[]
    for ips in remain_data:
        ip_es_num = socket.ntohl(struct.unpack("I", socket.inet_aton(str(ips)))[0])
        if (lpm.search_ip(ip_es_num)):
            continue
        else:
            new_remain.append(ips)
    return sn_gte24,new_remain
