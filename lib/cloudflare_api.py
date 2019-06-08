#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import requests


class Plublic_parameter(object):
    '''公共参数'''
    def __init__(self, email, login_token):
        self.URL = 'https://api.cloudflare.com/client/v4/zones/'
        self.record_url = '/dns_records'

        self.headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": login_token,
            "Content-Type": "application/json"
        }
        self.data = {}



class Cloudflare_Api_Zone(Plublic_parameter):
    '''域名操作'''
    def list_zones(self, name, match=None, order=None, page=None, per_page=None, status=None, direction=None):
        return_data = {}

        try:
            get_url = f"{self.URL}?name={name}"
            r = requests.get(url=get_url, headers=self.headers)
            result_json = r.json()

            return_data['status'] = result_json['success']
            return_data['message'] = result_json['messages']
            data = {}

            if return_data['status']:
                data['zone_id'] = result_json['result'][0]['id']
                return_data['data'] = data
            else:
                return_data['message'] = result_json['errors'][0]['message']
                data['code'] = result_json['errors'][0]['code']
                return_data['data'] = data

            return return_data

        except KeyError as e:
            return_data['status'] = 'Error'
            return_data['message'] = f"{self.URL} 连接失败 --> {e.__str__()}"
            return return_data

    '''
    jump_start 是否自动提取DNS记录，可选true或false
    type 是否完全由CloudFlare接管，可选"full"或"partial"
    '''
    def add_domain(self, name, jump_start=None, type=None):
        return_data = {}
        self.data['name'] = name
        self.data['jump_start'] = jump_start
        self.data['type'] = type

        try:
            r = requests.post(url=self.URL, headers=self.headers, json=self.data)
            result_json = r.json()

            return_data['status'] = result_json['success']
            return_data['message'] = result_json['messages']
            data = {}

            if return_data['status']:
                data['zone_id'] = result_json['result']['id']
                data['domain'] = result_json['result']['name']
                data['status'] = result_json['result']['status']
                return_data['data'] = data
            else:
                data['domain'] = name
                data['code'] = result_json['errors'][0]['code']
                data['message'] = result_json['errors'][0]['message']
                return_data['data'] = data

            return return_data

        except KeyError as e:
            return_data['status'] = 'Error'
            return_data['message'] = f"{self.URL} 连接失败 --> {e.__str__()}"
            return return_data




class Cloudflare_Api_ZoneRecord(Plublic_parameter):
    '''记录操作'''
    def list_dns_records(self):
        pass


    @staticmethod
    def get_zone_id(domain, url, headers):
        try:
            get_url = f"{url}?name={domain}"
            r = requests.get(url=get_url, headers=headers)
            result_json = r.json()

            return result_json['result'][0]['id']
        except:
            return None


    def add_record(self, domain, type, sub, content, ttl=1, priprity=None, proxied=None):
        return_data = {}
        self.data['type'] = type
        self.data['name'] = sub
        self.data['content'] = content
        self.data['ttl'] = ttl

        try:
            zone_id = self.get_zone_id(domain, self.URL, self.headers)
            add_record_url = f"{self.URL}{zone_id}{self.record_url}"

            r = requests.post(url=add_record_url, headers=self.headers, json=self.data)
            result_json = r.json()

            return_data['status'] = result_json['success']
            return_data['message'] = result_json['messages']
            data = {}

            if return_data['status']:
                data['domain'] = domain
                data['sub'] = sub
                data['value'] = content
                return_data['data'] = data
            else:
                data['code'] = result_json['errors'][0]['code']
                data['message'] = result_json['errors'][0]['message']
                data['domain'] = domain
                data['sub'] = sub
                data['value'] = content
                return_data['data'] = data

            return return_data

        except KeyError as e:
            return_data['status'] = 'Error'
            return_data['message'] = f"{self.URL} 连接失败 --> {e.__str__()}"
            return return_data



if __name__ == '__main__':
    pass


