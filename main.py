#!/usr/bin/python3

import os
import glob
import time
import datetime
import random
import traceback
import requests
import json
from time import sleep
import picamera
import atexit
import sys
import socket
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE
from gui import Button, render_widgets, touchscreen_event
import config
import auth

########################
### Variables ###
########################

total_pics = 3 # number of pics to be taken
capture_delay = 1 # delay between pics
prep_delay = 3 # number of seconds at step 1 as users prep to have photo taken
gif_delay = 30 # How much time between frames in the animated gif
restart_delay = 5 # how long to display finished message before beginning a new session
test_server = 'www.google.com'

# full frame of v1 camera is 2592x1944. Wide screen max is 2592,1555
# if you run into resource issues, try smaller, like 1920x1152.
# or increase memory http://picamera.readthedocs.io/en/release-1.12/fov.html#hardware-limits
high_res_w = 2592 # width of high res image, if taken
high_res_h = 1944 # height of high res image, if taken
frame_rate = 15

now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
gif_file_name = ""

# touch screen setup
ts = Touchscreen()

# set up camera

camera = picamera.PiCamera()
camera.vflip = False
camera.hflip = True # flip for preview, showing users a mirror image
camera.resolution = (high_res_w, high_res_h)
camera.framerate = frame_rate


#############################
### Variables that Change ###
#############################
# Do not change these variables, as the code will change it anyway
transform_x = int(config.monitor_w) # how wide to scale the jpg when replaying
transfrom_y = int(config.monitor_h) # how high to scale the jpg when replaying
offset_x = 0 # how far off to left corner to display photos
offset_y = 0 # how far off to left corner to display photos
replay_delay = 1 # how much to wait in-between showing pics on-screen after taking
replay_cycles = 2 # how many times to show each photo on-screen after taking

####################
### Other Config ###
####################
real_path = os.path.dirname(os.path.realpath(__file__))
file_path = real_path + '/pics/'
overlay_path = real_path + '/graphics/grace-hopper-overlay.png'

# initialize pygame
pygame.init()
pygame.display.set_mode((config.monitor_w, config.monitor_h))
screen = pygame.display.get_surface()
pygame.display.set_caption('NM Photo Booth')
pygame.mouse.set_visible(False)
pygame.display.toggle_fullscreen()

#################
### Functions ###
#################

# Exit button function
def exit_screen(b, e, t):
  pygame.display.quit()
  running = False
  sys.exit()

# Start photobooth function
def enter_game(b, e, t):
  start_photobooth()
  global running
  running = False

# clean up running programs as needed when main program exits
def cleanup():
  print('Ended abruptly')
  pygame.quit()

atexit.register(cleanup)

#delete files in folder
def clear_pics():
  files = glob.glob(file_path + '*.jpg')
  for f in files:
    os.remove(f)
  print("Deleted previous pics")

# check if connected to the internet
def is_connected():
  try:
    # see if we can resolve the host name -- tells us if there is a DNS listening
    host = socket.gethostbyname(test_server)
    # connect to the host -- tells us if the host is actually reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False

def get_token():
  try:
    url = 'https://dat-day-z.auth0.com/oauth/token'
    data = {
      "audience": "http://ec2-34-221-7-217.us-west-2.compute.amazonaws.com/api",
      "grant_type": "client_credentials",
      "client_id": auth.client_id,
      "client_secret": auth.client_secret
    }
    headers = { 'content-type': 'application/json' }
    r = requests.post(url, data=json.dumps(data), headers=headers).json()
    token = r['access_token']
    return token
  except:
    print('Something getting token')
    sys.exit(0)

# display one image on screen
def show_image(image_path):

  # clear the screen
  screen.fill( (0,0,0) )

  # load the image
  img = pygame.image.load(image_path)
  img = img.convert()

  # rescale the image to fit the current display
  img = pygame.transform.scale(img, (transform_x,transfrom_y))
  screen.blit(img,(offset_x,offset_y))
  pygame.display.flip()

# display a blank screen
def clear_screen():
  screen.fill( (0,0,0) )
  pygame.display.flip()


# Taking pics
def taking_pics():

  try:
    for i in range(1,total_pics+1):
      show_image(real_path + "/graphics/graphics_new/" + str(i) + ".png")
      time.sleep(capture_delay)
      camera.hflip = True # preview a mirror image
      camera.start_preview(resolution=(config.monitor_w, config.monitor_h))
      time.sleep(2)
      filename = file_path + now + '-0' + str(i) + '.jpg'
      camera.hflip = False
      camera.capture(filename)
      clear_screen()
      camera.stop_preview()
      if i == total_pics+1:
        break
  except:
    print('Something went wrong while trying to take pics')
    sys.exit(0)

# Covert image to gif
def convert():

  for x in range(1, total_pics+1): #batch process all the images
    overlayname = file_path + now + '-0'+  str(x) + '-overlay.jpg'
    addOverlayCmd = 'gm composite -geometry +0+1567 -compose Over ' + overlay_path + ' ' + file_path + now + "-0" +str(x) + ".jpg" + ' ' + ' ' + overlayname
    os.system(addOverlayCmd)
    graphicsmagick = "gm convert -size 1500x1500 " + file_path + now + "-0" + str(x) + "-overlay.jpg -thumbnail 1500x1500 " + file_path + now + "-0" + str(x) + "-sm.jpg"
    os.system(graphicsmagick)
  
  global gif_file_name
  gif_file_name = file_path + now + str(random.randint(1,1000000000000000))
  graphicsmagick = "gm convert -delay " + str(gif_delay) + " " + file_path + now + "*-sm.jpg " + gif_file_name + ".gif"

  os.system(graphicsmagick)

# Trigger photobooth workflow
def start_photobooth():

  ########################## Begin Step 1 Set up Camera ###########################

  print("Get Ready")
  show_image(real_path + "/graphics/graphics_new/StrikeAPose.png")
  sleep(prep_delay)

	# clear the screen
  clear_screen()

  ################################# Begin Step 2 #################################
  print("Taking pics")

  taking_pics()

  ########################### Begin Step 3 #################################

  print("Creating an animated gif")

  show_image(real_path + "/graphics/graphics_new/uploading.png")

  convert()

  ########################### Begin Step 4 #################################

  print("Uploading")

  ########################### check for internet connection ###########################

  connected = is_connected()
  if (connected==False):
   	print('bad internet connection')

  while connected:
    try:
      file_to_upload = gif_file_name + ".gif"
      data = { "folder" : config.s3_folder}
      url = 'http://api.thepbcam.com/api/upload'
      token = get_token()
      headers = { "Authorization" : "Bearer %s" %token}
      files = [( 'files' , open(file_to_upload, 'rb') )]
      r = requests.post(url, files=files, data=data, headers=headers)
      print(r)
      break
    except ValueError:
      print("Oops. No internect connection. Upload later.")
      #make a text file as a note to upload the .gif later
      try:
        file = open(file_path + "uploads.txt",'a')
        file.write(file_to_upload)
        file.close()
      except:
        print('Something went wrong. Could not write file.')
        sys.exit(0)

########################### Begin Step 5 #################################
  print("Done")
  show_image(real_path + "/graphics/graphics_new/AllDone.png")

 ########################### Restart photobooth ###########################
  time.sleep(restart_delay)
  clear_pics()
  global running
  running = True
  show_image(real_path + "/graphics/graphics_new/start.png")




####################
### Main Program ###
####################s

## clear the previously stored pics based on config settings
if config.clear_on_startup:
  clear_pics()

print("Photo booth app running...")

show_image(real_path + "/graphics/graphics_new/start.png")

#Widgets
render_widgets(screen)
Button(
  "",
  (0, 0, 0, 0),
  (760, 0),
  (40, 40),
  exit_screen
  )

Button(
  "",
  (255, 0, 0),
  (305, 357),
  (300, 100),
  enter_game
  )

ts.run()
running = True
while running:
  for touch in ts.touches:
    touch.on_press = touchscreen_event
    touch.on_release = touchscreen_event



