#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.get_config import get_config, Base_Dir
from lib.dnspod_api import *
from lib.cloudflare_api import *
from conf.get_mylogger import mylogger, console_logger


# 多线程执行
thread_list = []
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None



def main():
    '''主程序：添加域名、从dnspod导出所有record添加入CloudFlare'''
    # 1、添加域名
    console_logger.info(f"\033[35m#####开始添加域名#####\033[0m")
    for d in domains:
        domain_thread = MyThread(Cloudfare_Domain_Instance.add_domain, args=(d,))
        thread_list.append(domain_thread)
        domain_thread.start()
    for t in thread_list:
        t.join()
        return_data = t.get_result()

        if return_data['status']:
            console_logger.info(f"\033[32m域名{return_data['data']['domain']}添加到 <CloudFlare> 成功 \033[0m")
            mylogger.info(f"域名{return_data['data']['domain']}添加到 <CloudFlare> 成功")
        else:
            if return_data['data']['code'] == 1061:
                console_logger.info(f"\033[33m域名{return_data['data']['domain']}已在 <CloudFlare> 存在，忽略此次添加\033[0m")
            else:
                console_logger.error(f"\033[31m域名{return_data['data']['domain']}添加失败，请检查日志...\033[0m")
                mylogger.error(f"域名{return_data['data']['domain']}添加到 <CloudFlare> 失败，错误代码：{return_data['data']['code']}，失败原因：{return_data['data']['message']}")
    console_logger.info(f"\033[35m#####域名添加结束#####\033[0m")
    thread_list.clear()


    # 2、获取dnspod所有record去除NS记录，导入CloudFlare
    console_logger.info(f"\033[35m#####开始添加记录#####\033[0m")
    # 从dnspod获取record记录
    for d in domains:
        get_record_thread = MyThread(Dnspod_Record_Instance.get_record_list, args=(d,))
        thread_list.append(get_record_thread)
        get_record_thread.start()
    for t in thread_list:
        t.join()
        return_data = t.get_result()
        record_data = return_data['data']['records']

        record_list = []
        for r in record_data:
            if r['type'] != 'NS':
                tmp_dict = {}
                tmp_dict['domain'] = return_data['data']['belong_domain']
                tmp_dict['type'] = r['type']
                tmp_dict['sub'] = r['name']
                tmp_dict['content'] = r['value']
                record_list.append(tmp_dict)

        # 导入到CloudFlare
        for new_record in record_list:
            return_data = Cloudfare_Record_Instance.add_record(**new_record)

            if return_data['status']:
                console_logger.info(f"\033[32m域名{return_data['data']['domain']}添加主机头{return_data['data']['sub']}到记录{return_data['data']['value']}成功 \033[0m")
                mylogger.info(f"域名{return_data['data']['domain']}添加主机头{return_data['data']['sub']}到记录{return_data['data']['value']}成功")
            else:
                console_logger.info(f"\033[31m域名{return_data['data']['domain']}添加主机头{return_data['data']['sub']}到记录{return_data['data']['value']}失败，请检查日志... \033[0m")
                mylogger.info(f"域名{return_data['data']['domain']}添加主机头{return_data['data']['sub']}到记录{return_data['data']['value']}，失败错误代码：{return_data['data']['code']}，失败原因：{return_data['data']['message']}")

    console_logger.info(f"\033[35m#####记录添加结束#####\033[0m")



if __name__ == '__main__':

    ### domain.txt
    domain_init = input(f"\033[33m请输入要操作的域名(已,为分隔符),直接回车则从文件 {Base_Dir}/bin/domain.txt 读入域名：\033[0m")
    with open(f"{Base_Dir}/bin/domain.txt", 'r') as f:
        domains = domain_init.split(',') if domain_init else f.read().splitlines()


    ### conf
    dnspod_token = get_config('dnspod_api')['d_token']
    cloudflare_email = get_config('cloudflare_api')['c_email']
    cloudflare_token = get_config('cloudflare_api')['c_token']


    ### instance
    # Dnspod
    # Dnspod_Domain_Instance = Dnspod_Api_Domain(dnspod_token)
    Dnspod_Record_Instance = Dnspod_Api_Record(dnspod_token)
    # Cloudflare
    Cloudfare_Domain_Instance = Cloudflare_Api_Zone(cloudflare_email, cloudflare_token)
    Cloudfare_Record_Instance = Cloudflare_Api_ZoneRecord(cloudflare_email, cloudflare_token)


    ### main program
    main()


      

