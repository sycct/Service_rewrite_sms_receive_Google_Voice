# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import imaplib
import email
import os
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
                                message['body'] = self.email_content_replace(body)
                                temp_list.append(message)
                            elif "attachment" in content_disposition:
                                message['body'] = self.email_content_replace(part.get_payload(decode=True))
                                temp_list.append(message)
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        message['body'] = self.email_content_replace(body)
                        temp_list.append(message)
        # close the connection and logout
        mail.close()
        mail.logout()
        return temp_list

    @staticmethod
    def email_content_replace(email_content):
        # 替换无用内容
        message_content_replace = email_content.replace('\r\n', '').replace('<https://voice.google.com>', '') \
            .replace('Google Voice ', '')
        message_content_index = message_content_replace.find('要回复此短信，请回复此电子邮件或访问 Google Voice。')
        """此处过滤文本示例：
        <https://voice.google.com>
        Your TrafficJunky one-time code is RTW62A. If this action was not initiated
        by you please contact our Support Team or call +1-877-467-2875.
        您的帐号 <https://voice.google.com> 帮助中心
        <https://support.google.com/voice#topic=1707989> 帮助论坛
        <https://productforums.google.com/forum/#!forum/voice>
        您收到此电子邮件，是因为您曾表示愿意接收有关短信的电子邮件通知。如果您不希望 
        日后再收到这类电子邮件，请更新您的电子邮件通知设置
        <https://voice.google.com/settings#messaging>。
        Google LLC
        1600 Amphitheatre Pkwy
        Mountain View CA 94043 USA
        """
        if message_content_index == -1:
            message_content_index = message_content_replace.find('您的帐号  帮助中心')
        message_content = message_content_replace[0:message_content_index]
        return message_content
