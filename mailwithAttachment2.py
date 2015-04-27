# -*- coding: utf-8 -*-
"""
Created on Fri Jan  9 12:50:11 2015

@author: operational
"""

import os ; import sys ; import smtplib ; import mimetypes ; 
from smtplib import SMTP
from smtplib import SMTPException
from email.mime.multipart import MIMEMultipart ; 
from email import encoders
from email.message import Message ; 
from email.mime.image import MIMEImage
from email.mime.text import MIMEText


_from     =   "skymet.monitoring@gmail.com" ; 
_to       =   "vineethpk@skymet.net" ;
_sub      =   "test mail"
_attach   =   "/home/OldData/IntCor/test.csv"
_content  =   "Test mail"
_username =   'skymet.monitoring' ; 
_password =   'nAKeY2-u'

_smtp         = "smtp.gmail.com:587" ;
_text_subtype = "plain"


mail=MIMEMultipart()
mail["Subject"]  =  _sub
mail["From"]     =  _from
mail["To"]       =  ','.join(_to)

#ctype, encoding = mimetypes.guess_type(_attach)
#if ctype is None or encoding is not None:
#    ctype = "application/octet-stream"
#maintype, subtype = ctype.split("/", 1)

body = MIMEMultipart('alternative')
body.attach(MIMEText(_content, _text_subtype ))
mail.attach(MIMEText(file(_attach).read()))

try:
      smtpObj = SMTP(_smtp)
      #Identify yourself to GMAIL ESMTP server.
      smtpObj.ehlo()
      #Put SMTP connection in TLS mode and call ehlo again.
      smtpObj.starttls()
      smtpObj.ehlo()
      #Login to service
      smtpObj.login(user=_username, password=_password)
      #Send email
      smtpObj.sendmail(_from, _to, mail.as_string())
      #close connection and session.
      smtpObj.quit()
except SMTPException as error:
      print "Error: unable to send email :  {err}".format(err=error)























 