import requests
import bs4
import pyodbc
import mysql.connector
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Scraper:

    def __init__(self, keywords):
        self.markup = requests.get('https://news.ycombinator.com/').text
        self.keywords = keywords

    def parser(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        links = soup.findAll('a', {'class': 'storylink'})
        self.savedlinks = []

        for link in links:
            for keyword in self.keywords:
                if keyword in link.text:
                    self.savedlinks.append(str(link))

    def store(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="zachSQLd$2791", database="stock_info")
        mycursor = mydb.cursor()

        if mydb:
            print("Database connection successful")

            sqlform = "INSERT INTO tableoflinks (links) VALUES (%s)"

            mycursor.executemany(sqlform, [(link,) for link in self.savedlinks])

            mydb.commit()

            # close connections
            mycursor.close()
            mydb.close()

        else:
            print("Database connection failed")

    def email(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="zachSQLd$2791", database="stock_info")
        mycursor = mydb.cursor()

        sql = "SELECT * FROM tableoflinks"

        mycursor.execute(sql)

        mylinks = list(mycursor.fetchall())

        # EMAIL
        # me == my email address
        # you == recipient's email address
        me = "downingz791junk@gmail.com"
        you = "downingz791junk@gmail.com"

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg['From'] = me
        msg['To'] = you

        # Create the body of the message (a plain-text and an HTML version).

        html = """\
        <h4> %s here are some stock links for today </h4>
        
        %s 
        
        """ % (len(mylinks), '<br/><br/>'.join(mylinks))

        # Record the MIME types of both parts - text/plain and text/html.
        mime = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(mime)

        # Send the message via local SMTP server.
        s = smtplib.SMTP('localhost')
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(me, you, msg.as_string())
        s.quit()




