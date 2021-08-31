# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from apscheduler.schedulers.blocking import BlockingScheduler
import os
from dotenv import load_dotenv

from utils import process_mail


class ReadGoogleVoiceSMSContentByGmail(object):
    def __init__(self):
        # loading env config file
        dotenv_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

        self._init_process_gmail = process_mail.ProcessMail()

    def run(self):
        self._init_process_gmail.process_mail_main()


if __name__ == '__main__':
    # 实例化一个调度器
    scheduler = BlockingScheduler()
    monitor = ReadGoogleVoiceSMSContentByGmail()
    # 添加任务并设置触发方式每30s执行一次
    scheduler.add_job(monitor.run, 'interval', seconds=30)
    # 开始运行调度器
    scheduler.start()
