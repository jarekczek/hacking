import http.server
import os
import pyodbc
import re
import sys
import time
import urllib

def dumpRows(cursor):
  rows = cursor.fetchall()
  for row in rows:
    print(row)

class Dao:
  def __init__(self):
    password = os.environ.get('PGPASS')
    cnxn = pyodbc.connect('DRIVER=PostgreSQL ODBC Driver(ANSI);SERVER=localhost;'
                          + 'DATABASE=pwd;UID=postgres;PWD=' + password)
    self.cursor = cnxn.cursor()

  def addPassword(self, password, source):
    self.cursor.execute('select count(*) from password where password=? and source=? limit 1', password, source)
    if self.cursor.fetchall()[0][0] > 0:
      return 0
    self.cursor.execute('insert into password(password, source) values (?, ?)', password, source)
    self.cursor.commit()
    return 1

  def getNotUsed(self, target):
    self.cursor.execute("select password from password p where not exists "
      + "(select * from used u where u.password = p.password and target = ?)",
      target)
    passwords = []
    for row in self.cursor.fetchall():
      passwords.append(row[0])
    return passwords

  def markUsed(self, password, target):
    self.cursor.execute('select count(*) from used where password=? and target=? limit 1', password, target)
    if self.cursor.fetchall()[0][0] > 0:
      return 0
    self.cursor.execute('insert into used(password, target) values (?, ?)', password, target)
    self.cursor.commit()
    return 1

class MyServer(http.server.HTTPServer):
  def __init__(self, a1, a2):
    http.server.HTTPServer.__init__(self, a1, a2)
    self.stopFlag = False
    self.dao = Dao()

class MyRequestHandler(http.server.BaseHTTPRequestHandler):

  def __init__(self, a1, a2, a3):
    self.bodyBytes = None
    http.server.BaseHTTPRequestHandler.__init__(self, a1, a2, a3)

  def pathOnly(self):
    return self.path.split('?')[0]

  def bodyStr(self):
    content_len = int(self.headers.get('Content-Length'))
    if self.bodyBytes == None:
      self.bodyBytes = self.rfile.read(content_len)
    return self.bodyBytes.decode('iso-8859-1')

  def do_GET(self):
    handled = False
    body = []

    if self.pathOnly() == '/hello':
      self.send_response(200)
      handled = True

    if self.pathOnly() == '/status':
      self.send_response(200)
      handled = True

    if self.pathOnly() == '/shutdown':
      print('shutdown called')
      self.send_response(200)
      self.server.stopFlag = True
      handled = True

    if self.pathOnly() == '/dump':
      self.send_response(200)
      self.server.dao.cursor.execute("select * from password")
      for row in self.server.dao.cursor.fetchall():
        body.append(str(row))
      handled = True

    if self.path.startswith('/getNotUsed/'):
      target = self.path.split('/')[2]
      self.send_response(200)
      passwords = self.server.dao.getNotUsed(target)
      for password in passwords:
        body.append(password)
      handled = True

    if not handled:
      print('GET path not handled: ' + self.path)
      self.send_error(404)

    self.end_headers()
    if len(body) > 0:
      for line in body:
        self.wfile.write(bytes(line + '\n', 'iso-8859-1'))

  def do_POST(self):
    handled = False
    respBody = []

    if self.path.startswith('/add/'):
      source = self.path.split('/')[2]
      if source == '':
        raise 'no source given'
      print('handling ' + self.bodyStr())
      added = 0
      for word in self.bodyStr().split('\n'):
        word = re.sub("[ \r\n]", "", word)
        if word == '':
          continue
        added += self.server.dao.addPassword(word, source)
      self.send_response(200)
      respBody.append('added: ' + str(added))
      handled = True

    if self.pathOnly().startswith("/markUsed/"):
      target = self.path.split('/')[2]
      password = self.bodyStr()
      self.send_response(200)
      respBody.append('marking ' + password + ' for ' + target + '')
      marked = self.server.dao.markUsed(password, target)
      respBody.append(str(marked))
      handled = True

    if not handled:
      print('POST path not handled: ' + self.path)
      self.send_error(404)

    self.end_headers()
    if len(respBody) > 0:
      for line in respBody:
        self.wfile.write(bytes(line + '\n', 'iso-8859-1'))

httpd = MyServer(('localhost', 7978), MyRequestHandler)
print('http password server ready')

while not httpd.stopFlag:
  httpd.handle_request()
