#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import unittest
from dotenv import load_dotenv

from utils.read_mail import ReadGmail


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        # 获取当前文件所在目录的上级目录
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # loading env config file
        dotenv_path = os.path.join(parent_dir, '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

    def test_add_numbers(self):
        init_read_mail = ReadGmail()
        message = '''
        <https://voice.google.com>
        [bilibili]439441短信登录验证码，5分钟内有效，请勿泄露。
        您的账号 <https://voice.google.com> 帮助中心
        <https://support.google.com/voice#topic=1707989> 帮助论坛
        <https://productforums.google.com/forum/#!forum/voice>
        您收到此电子邮件，是因为您曾表示愿意接收有关短信的电子邮件通知。如果您不希望 
        日后再收到这类电子邮件，请更新您的电子邮件通知设置
        <https://voice.google.com/settings#messaging>。
        Google LLC
        1600 Amphitheatre Pkwy
        Mountain View CA 94043 USA
        '''
        result = init_read_mail.email_content_replace(message)
        self.assertEqual(result, '[bilibili]439441短信登录验证码，5分钟内有效，请勿泄露。', "测试成功！")
