# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import imaplib
import email
import os
import re
from email.header import decode_header


class ReadGmail:

    def __init__(self):
        self._from_mail = os.environ.get('FROM_MAIL')
        self._from_password = os.environ.get('FROM_MAIL_PASSWORD')
        self._smtp_server = os.environ.get('SMTP_SERVER')
        self._smtp_port = int(os.environ.get('SMTP_SERVER_PORT'))
        # number of top emails to fetch
        self._receive_number = 10

    def get_mail_client(self):
        mail = imaplib.IMAP4_SSL(self._smtp_server)
        mail.login(self._from_mail, self._from_password)
        return mail

    def read_email_from_gmail(self):
        mail = imaplib.IMAP4_SSL(self._smtp_server)
        mail.login(self._from_mail, self._from_password)
        status, messages = mail.select("INBOX")
        # total number of emails
        messages = int(messages[0])
        temp_list = []
        message_end = messages - self._receive_number if messages > self._receive_number else 0
        for i in range(messages, message_end, -1):
            # fetch the email message by ID
            res, msg = mail.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)
                    MessageId, encoding = decode_header(msg.get("Message-ID"))[0]
                    if isinstance(MessageId, bytes):
                        MessageId = MessageId.decode(encoding)
                    message_id = MessageId.replace('<+', '').replace('@txt.voice.google.com>', '')
                    message = {'from': From, 'message_id': message_id}
                    # if the email message is multipart
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # print text/plain emails and skip attachments
                                message['body'] = body
                                temp_list.append(message)
                            elif "attachment" in content_disposition:
                                message['body'] = part.get_payload(decode=True)
                                temp_list.append(message)
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        message['body'] = body
                        temp_list.append(message)
        # close the connection and logout
        mail.close()
        mail.logout()
        return temp_list

    # @staticmethod
    # def email_content_replace(email_content):
    #     """
    #     使用正则表达式匹配短信正文，并过滤掉开头的无用链接。
    #     """
    #     # 去除换行和多余空格
    #     cleaned_content = re.sub(r'\s+', ' ', email_content.strip())
    #
    #     # 正则表达式匹配短信正文，忽略前面的 URL 或无关前缀
    #     pattern = (
    #         r'(?:https?://\S+\s*)*'  # 匹配并忽略开头的链接
    #         r'([a-zA-Z\[\]0-9\u4e00-\u9fa5].*?)'  # 匹配正文的主要部分
    #         r'[\.\s]*?(https?://|Google LLC|此电子邮件|Mountain View|帮助中心|HELP FORUM|support\.google)'
    #     )
    #
    #     match = re.search(pattern, cleaned_content, re.IGNORECASE)
    #
    #     if match:
    #         return match.group(1).strip()  # 返回匹配到的短信正文
    #     else:
    #         return cleaned_content  # 如果未匹配到，返回清理后的全文
