import requests
import json
import random
import smbus
import time

ip = 'http://192.168.1.20'

bus = smbus.SMBus(1)
# I2C address 0x29
# Register 0x12 has device ver.
# Register addresses must be OR'ed with 0x80
bus.write_byte(0x29,0x80|0x12)
ver = bus.read_byte(0x29)
# version # should be 0x44
if ver == 0x44:
  print "Color Sensor found\n"
  bus.write_byte(0x29, 0x80|0x00) # 0x00 = ENABLE register
  bus.write_byte(0x29, 0x01|0x02) # 0x01 = Power on, 0x02 RGB sensors enabled
  bus.write_byte(0x29, 0x80|0x14) # Reading results start register 14, LSB then MSB
else:
  print "Color sensor not found\n"


while 1:
  # Get Location from camera
  url = ip + ':8081/location'
  request = requests.get(url)
  location = request.json()
  x = location[0]
  y = location[1]
  print 'Current Location:'
  print x
  print y

  # Read color from sensor
  data = bus.read_i2c_block_data(0x29, 0)
  clear = clear = data[1] << 8 | data[0]
  red = data[3] << 8 | data[2]
  green = data[5] << 8 | data[4]
  blue = data[7] << 8 | data[6]
  crgb = "C: %s, R: %s, G: %s, B: %s\n" % (clear, red, green, blue)
  print 'Color:'
  print crgb

  # Send server color
  url = ip + ':8081/colorData'
  data = {"color": color, "position":[x,y]}
  data_json = json.dumps(data)
  headers = {'Content-type': 'application/json'}
  response = requests.post(url, data=data_json, headers=headers)
  print 'Send data to server:'
  print response.text
