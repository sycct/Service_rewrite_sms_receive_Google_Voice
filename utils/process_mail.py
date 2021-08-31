# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from requests import exceptions
from json import decoder
import os

from config import LoggingConfig
from utils import read_mail


class ProcessMail:
    # 处理邮件公共类
    def __init__(self):
        self._request_verify_url = os.environ.get('VERIFY_URI')
        self._request_post_url = os.environ.get('POST_SMS_MESSAGE_URI')
        logger_name = 'email_to_sms'
        self._logger = LoggingConfig().init_logging(logger_name)
        self._init_call_gmail = read_mail.ReadGmail()

    @staticmethod
    def process_mail_from(mail_from):
        from_str = mail_from.split('.')
        # 接收方号码
        get_to_number = from_str[0].split('<')[1]
        # 发送方号码
        get_from_number = from_str[1]
        return get_from_number, get_to_number

    def verify_sms_exits(self, message_id, to_number):
        # 验证短信是否存在于数据库中
        payload = {'messageId': message_id, 'ToNumber': to_number}
        try:
            response = requests.post(self._request_verify_url, data=payload, timeout=2)
        except (exceptions.ConnectionError, exceptions.Timeout, exceptions.HTTPError) as e:
            self._logger.error(f"验证邮件内容的时候出现网络错误，具体错误内容： {e}")
            return False
        try:
            response_json = response.json()
        except decoder.JSONDecodeError:
            return False
        try:
            get_response_result = response_json['success']
            return True if get_response_result else False
        except KeyError:
            if response_json['phoneNumberExits'] is False:
                # 号码不存在
                return False

    def send_email_to_sms(self, sms_content, to_number, from_number):
        payload = {'Body': sms_content, 'To': to_number, 'From': from_number}
        try:
            response = requests.post(self._request_post_url, data=payload, timeout=2)
        except (exceptions.ConnectionError, exceptions.Timeout, exceptions.HTTPError) as e:
            self._logger.error(f"提交短信内容时候出现网络错误，具体错误内容： {e}")
            return False
        response_json = response.json()
        if response_json['success']:
            self._logger.info('短信内容已成功提交。')
            return True

    def process_mail_main(self):
        # 获取gmail邮件内容并提交到网站api point.
        receive_mail = self._init_call_gmail.read_email_from_gmail()
        if receive_mail:
            for item in receive_mail:
                message_id = item['message_id']
                mail_from = item['from']
                message_content = item['body']
                from_number, to_number = self.process_mail_from(mail_from)
                verify_result = self.verify_sms_exits(message_id, to_number)
                if verify_result:
                    self.send_email_to_sms(message_content, to_number, from_number)
