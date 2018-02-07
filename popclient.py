#!/usr/bin/python

"""
Popclient.py
This script will be used to pull email from a POP mail server account for 
consumption by Jira.

Steps:
    1. Connect to POP enabled email account, read all emails
    2. Copy emails to target directory for Jira to read
    3. Save the date and time of the last email read. This will be used
       to determine where to start downloading the next group of emails.




"""
import poplib
from email.parser import Parser
import re
import os.path
import argparse
import shutil
from obfussee import illumit
from datetime import datetime
from smtplib import SMTP
import os
import errno
from email.mime.text import MIMEText
import logging
import ConfigParser
import email.utils
import time
import calendar


LAST_MESSAGE_READ_DATETIME_FILE = "LASTMESSAGETIME"
ARCHIVE_DIR = 'MAIL_ARCHIVE'

def isserverconnected(connect_message):
    logging.debug(connect_message)
    if '+OK' in connect_message:
        return True

    return False

def isok(server_message):
    logging.debug(server_message)
    if '+OK' in server_message:
        return True

    return False

class MailClient:

    def __init__(self, filter_sender, filter_subject, server_pop, port_pop, user_pop, pass_pop, server_smtp, port_smtp, user_smtp, pass_smtp, resp_email, resp_title, resp_body, proj_dir, archive_dir):
        self.sender_filter = filter_sender
        self.subject_filter = filter_subject
        self.filter_match = False
        self.pop_connection = None
        self.pop_port = port_pop
        self.pop_server = server_pop
        self.pop_connection_user = user_pop
        self.pop_connection_pass = pass_pop
        self.smtp_connection = None
        self.smtp_server = server_smtp
        self.smtp_port = port_smtp
        self.smtp_connection_user = user_smtp
        self.smtp_connection_pass = pass_smtp
        self.mail_sender = None
        self.mail_subject = None
        self.mail_date = None
        self.mail_file_name = None
        self.mail_body = None
        self.last_mail_time = None
        self.respond_email = resp_email
        self.respond_title = resp_title
        self.respond_body = resp_body
        self.jira_project_dir = proj_dir
        self.mail_archive_dir = archive_dir

    def save_mail(self):
        if not os.path.isdir(ARCHIVE_DIR):
            os.makedirs(ARCHIVE_DIR)

        if not os.path.isdir(self.jira_project_dir):
            os.makedirs(self.jira_project_dir)

        save_as_file = os.path.join(ARCHIVE_DIR, self.mail_file_name)

        with open(save_as_file, 'w') as mail_file:
            mail_file.write(self.mail_body)
            mail_file.close()
            shutil.copy(save_as_file, self.jira_project_dir)

    def save_last_email_time(self):
        if self.mail_date != None:
            with open(LAST_MESSAGE_READ_DATETIME_FILE, 'w') as mail_time_file:
                mail_time_file.write(self.mail_date)
                mail_time_file.close()

    def send_confirmation_msg(self):
        self.server_smtp_connect()
        m = re.search(r'[\w\.-]+@[\w\.-]+',self.mail_sender)
        msg = MIMEText(self.respond_body + "\n" + '\"'+self.mail_subject+'\"')
        msg['Subject'] = self.respond_title
        self.smtp_connection.sendmail(self.respond_email, m.group(0),msg.as_string())
        logging.info("Confirmation email sent")
        self.smtp_connection.quit()

    def get_last_email_time(self):
        with open(LAST_MESSAGE_READ_DATETIME_FILE, 'r+') as mail_time_file:
            self.last_mail_time = ''.join(mail_time_file.readlines())
            logging.info("Last mail processed time: "+self.last_mail_time)

    def server_pop_connect(self):
        popcon = poplib.POP3( self.pop_server, self.pop_port)
        if isserverconnected(popcon.getwelcome()):
            popcon.user(self.pop_connection_user)
            popcon.pass_(self.pop_connection_pass)
            self.pop_connection = popcon

    def server_smtp_connect(self):
        self.smtp_connection = SMTP(self.smtp_server, self.smtp_port)
        self.smtp_connection.login(self.smtp_connection_user,self.smtp_connection_pass)
        
    def get_mail_message(self, message_number):
        parser = Parser()
        (server_msg, body, octets) = self.pop_connection.retr(message_number)
        b = "\n".join(body)
        pb = parser.parsestr(b)
        self.mail_body = b
        self.mail_sender = pb.get('from')
        self.mail_subject = pb.get('subject')
        self.mail_date = pb.get('date')
        self.mail_file_name = (self.mail_sender + self.mail_subject + "-" + self.mail_date + ".mail").replace(" ", "")
        self.mail_file_name = re.sub(r'[/\\:*?"<>,|]', '-', self.mail_file_name)
        self.filter_match = True
        
        if self.sender_filter is not None:
            if not re.search(self.sender_filter, self.mail_sender):
                self.filter_match = False
                logging.debug("sender does not pass filter: "+self.mail_sender)
        
        if self.subject_filter is not None:
            if not re.search(self.subject_filter, self.mail_subject):
                self.filter_match = False
                logging.debug("subject does not pass filter: "+self.mail_subject)
        
        logging.debug("processing email of: " + self.mail_sender)

    def parse_mail_time(self, mail_time):
        emt = email.utils.parsedate_tz(mail_time)
        emt_tz = calendar.timegm(emt) - emt[9]
        return emt_tz
    
    def get_mail(self, msg_scope):
        self.server_pop_connect()
        (num_msgs, total_size) = self.pop_connection.stat()

        if num_msgs == 0:
            return

        self.get_last_email_time()
        saved_time_obj = self.parse_mail_time(str(self.last_mail_time).rstrip())

        if msg_scope == 'ALL':
           for i in range(num_msgs):
               self.get_mail_message( i + 1)
               mail_time = self.parse_mail_time(str(self.mail_date))

               if mail_time > saved_time_obj:
                    if self.filter_match:
                        logging.info("Processing Message")
                        self.save_mail()
                        self.send_confirmation_msg()

        elif msg_scope == 'LATEST':
            self.get_mail_message(num_msgs)
            if self.filter_match:
                self.save_mail()

        self.save_last_email_time()


def GetConfigProperties(config_file):
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    cfg={}
    logging.info("reading configuration file")
    cfg['CORP_POPSERVER'] = config.get('Default', 'CORP_POPSERVER', 0)
    cfg['CORP_POP_PORT'] = config.get('Default', 'CORP_POP_PORT', 0)
    cfg['CORP_POP_USER'] = config.get('Default', 'CORP_POP_USER', 0)
    cfg['CORP_POP_PASS'] = config.get('Default', 'CORP_POP_PASS', 0)
    cfg['FILTER_USER'] = config.get('Default', 'FILTER_USER', 0)
    cfg['FILTER_SUBJECT'] = config.get('Default', 'FILTER_SUBJECT', 0)
    cfg['RANGE'] = config.get('Default', 'RANGE', 0)
    cfg['CORP_SMTPSERVER'] = config.get('Default', 'CORP_SMTPSERVER', 0)
    cfg['CORP_SMTP_PORT'] = config.get('Default', 'CORP_SMTP_PORT', 0)
    cfg['CORP_SMTP_USER'] = config.get('Default', 'CORP_SMTP_USER', 0)
    cfg['CORP_SMTP_PASS'] = config.get('Default', 'CORP_SMTP_PASS', 0)
    cfg['JIRA_PROJECT_DIR'] = config.get('Default', 'JIRA_PROJECT_DIR', 0)
    cfg['MAIL_ARCHIVE_DIR'] = config.get('Default', 'MAIL_ARCHIVE_DIR', 0)
    cfg['RESPOND_EMAIL'] = config.get('RespondMessage', 'RESPOND_EMAIL', 0)
    cfg['RESPOND_TITLE'] = config.get('RespondMessage', 'RESPOND_TITLE', 0)
    cfg['RESPOND_BODY'] = config.get('RespondMessage', 'RESPOND_BODY', 0)
    
    return cfg


def main():
    logging.basicConfig(filename="popclient.log", level=logging.DEBUG)
    aparse = argparse.ArgumentParser(description='Email Downloader')

    aparse.add_argument('--useconfig', action="store", dest="config_file", default="popclient.cfg")
    cfg = None 
    if os.path.isfile(aparse.parse_args().config_file):
        logging.info(aparse.parse_args().config_file)
        cfg = GetConfigProperties(aparse.parse_args().config_file)

    logging.debug(cfg)
    c = MailClient(cfg['FILTER_USER'],  cfg['FILTER_SUBJECT'], cfg['CORP_POPSERVER'], \
            cfg['CORP_POP_PORT'], cfg['CORP_POP_USER'], illumit(cfg['CORP_POP_PASS']), \
            cfg['CORP_SMTPSERVER'], cfg['CORP_SMTP_PORT'], cfg['CORP_SMTP_USER'], illumit(cfg['CORP_SMTP_PASS']), \
            cfg['RESPOND_EMAIL'], cfg['RESPOND_TITLE'], cfg['RESPOND_BODY'], \
            cfg['JIRA_PROJECT_DIR'], cfg['MAIL_ARCHIVE_DIR'])

    c.get_mail(cfg['RANGE'])


if __name__ == '__main__':
    main()



