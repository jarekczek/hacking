import http.server
import os
import signal
import subprocess
import sys
import threading
import time
from subprocess import Popen, CREATE_NEW_PROCESS_GROUP, PIPE, STDOUT

configCount = int(os.environ['CONFIG_COUNT'])
currentConfig = int(os.environ.get('START_CONFIG', '0')) - 1
espeakExecutable = os.environ.get('ESPEAK', None)
httpPort = int(os.environ['PORT'])
maxRetries = int(os.environ.get('RETRIES', '3'))
serviceExecutable = os.environ['SERVICE']
serviceTimeout = int(os.environ.get('SERVICE_TIMEOUT', '0'))
successMessage = os.environ['SUCCESS_MESSAGE']

stopApp = False

class ServiceProcess():

  def __init__(self):
    self.success = False
    self.forceStop = True
    self._process = None
    
  def start(self):
    global serviceExecutable
    self.forceStop = False
    cfg = self.nextConfig()
    t0 = time.time()
    print('starting from config: ' + str(cfg))
    self._process = Popen(['cmd', '/c', serviceExecutable, str(cfg)],
        stdout=PIPE, stderr=STDOUT,
        creationflags = CREATE_NEW_PROCESS_GROUP
        )
    reader = Reader(self._process.stdout, self)
    reader.start()
    while True:
      time.sleep(1)
      if self._process.poll() != None:
        speak('start ' + str(currentConfig) + ' failed')
        return 500
      if self.success:
        speak('start ' + str(currentConfig) + ' succeeded')
        return 200
      elapsed = time.time() - t0
      if serviceTimeout != 0 and elapsed > serviceTimeout:
        speak('should timeout')
        stopCode = self.stop()
        if stopCode != 200:
          return 501
        return 502
      
  def stop(self):
    self.forceStop = True
    os.kill(self._process.pid, signal.CTRL_BREAK_EVENT)
    self._process.terminate()
    while True:
      time.sleep(1)
      if self._process.poll() != None:
        speak('stopped ' + str(currentConfig))
        return 200
      
  def handleRead(self, line):
    global successMessage
    if not self.forceStop and successMessage in line:
      self.success = True
      
  def nextConfig(self):
    global currentConfig, configCount
    currentConfig += 1
    if currentConfig >= configCount:
      currentConfig = 0
    return currentConfig

class MyServer(http.server.HTTPServer):
  def __init__(self, a1, a2):
    http.server.HTTPServer.__init__(self, a1, a2)
    self._service = None
    
class MyRequestHandler(http.server.BaseHTTPRequestHandler):
  
  def __init__(self, a1, a2, a3):
    http.server.BaseHTTPRequestHandler.__init__(self, a1, a2, a3)
    
  def do_GET(self):
    global stopApp
    handled = False
    
    if self.path == '/hello':
      speak("hello")
      self.send_response(200)
      handled = True
    
    if self.path == '/status':
      self.send_response(200)
      handled = True
    
    if self.path == '/shutdown':
      print('shutdown called')
      self.send_response(200)
      stopApp = True
      handled = True
      
    if self.path == '/start':
      assert self.server._service == None
      self.server._service = ServiceProcess()
      startCode = self.server._service.start()
      if startCode != 200:
        self.server._service = None
      self.send_response(startCode)
      handled = True

    if self.path == '/stop':
      assert self.server._service != None
      stopCode = self.server._service.stop()
      print('service ' + str(currentConfig) + ' stopped: ' + str(stopCode))
      self.server._service = None
      self.send_response(stopCode)
      handled = True

    if self.path == '/restart':
      self.restartService()
      handled = True
      
    if not handled:
      print('path not handled: ' + self.path)
      self.send_error(404)
      
    self.end_headers()
      
  def restartService(self):
    global maxRetries
    startedOk = False
    if self.server._service != None:
      stopCode = self.server._service.stop()
      print('service ' + str(currentConfig) + ' stopped: ' + str(stopCode))
      if stopCode != 200:
        raise Exception('problem stopping server ' + str(stopCode))
      # after stopping, give it a while to make all resources really free
      time.sleep(2)

    # now it is stopped, let's start until success
    for i in range(0, maxRetries):
      self.server._service = ServiceProcess()
      startCode = self.server._service.start()
      if startCode == 200:
        startedOk = True
        break
      else:
        self.server._service = None
        
    if startedOk:
      self.send_response(200)
    else:
      speak('failed to restart service after ' + str(maxRetries) + ' retries')
      self.send_error(500)
  
      
class Reader(threading.Thread):
  def __init__(self, stream, handlerClass):
    threading.Thread.__init__(self)
    self.daemon = True
    self.stream = stream
    self._lines = []
    self._stopFlag = False
    self._handlerClass = handlerClass
    
  def stop(self):
    self._stopFlag = True

  def run(self):
    while not self._stopFlag:
      line = self.stream.readline()
      if len(line) == 0:
        break
      lineStr = line.decode('iso-8859-1')
      if lineStr[-1] == '\n':
        lineStr = lineStr[0:-1]
      print("service output: " + lineStr)
      self._lines.append(lineStr)
      if self._handlerClass.handleRead(lineStr):
        break
    print('reader finished')
  def output(self):
    return self._lines

def speak(text):
  global espeakExecutable
  print(text)
  if espeakExecutable == None:
    return
  try:
    Popen([espeakExecutable, '-s', '250', '-a', '200', text])
  except:
    pass

httpd = MyServer(('localhost', httpPort), MyRequestHandler)
print('http server ready')

while not stopApp:
  #print('still handling: ' + str(stopApp))
  httpd.handle_request()
  
print('app finished')

