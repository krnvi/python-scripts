# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 16:09:54 2015

@author: operational
"""

import os ; import sys ; import smtplib ; import mimetypes ; from email import *

from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText



email_from="skymet.monitoring@gmail.com" ; email_to="vineethpk@skymet.net"
file_attach='/home/OldData/IntCor/test.csv'

username='skymet.monitoring' ; password='nAKeY2-u'


msg = MIMEMultipart()
msg["From"] = email_from
msg["To"] = email_to
msg["Subject"] = "test mail"
msg.preamble ="hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"

ctype, encoding = mimetypes.guess_type(file_attach)
if ctype is None or encoding is not None:
    ctype = "application/octet-stream"

maintype, subtype = ctype.split("/", 1)


if maintype == "text":
    fp = open(file_attach)
    # Note: we should handle calculating the charset
    attachment = MIMEText(fp.read(), _subtype=subtype)
    fp.close()
elif maintype == "image":
    fp = open(file_attach, "rb")
    attachment = MIMEImage(fp.read(), _subtype=subtype)
    fp.close()
msg.attach(attachment)
server = smtplib.SMTP("smtp.gmail.com:587")
server.starttls()
server.login(username,password)
server.sendmail(email_from, email_to, msg.as_string())
server.quit()






















