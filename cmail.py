import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,subject,body):#ho whom we are sending the mail
    server=smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login('yamini.adduri12@gmail.com','lusrsqtmhettkejp')
    msg=EmailMessage()
    msg['From']='yamini.adduri12@gmail.com'
    msg['Subject']=subject
    msg['To']=to
    msg.set_content(body)
    server.send_message(msg)
    server.quit()
