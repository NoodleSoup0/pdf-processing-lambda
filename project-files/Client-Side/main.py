#
# Client-side python app for benford app, which is calling
# a set of lambda functions in AWS through API Gateway.
# The overall purpose of the app is to process a PDF and
# see if the numeric values in the PDF adhere to Benford's
# law.
#
# Authors:
#   Prof. Joe Hummel
#   Northwestern University
#   CS 310, Project 03
#

import requests
import jsons
import json

import uuid
import pathlib
import logging
import sys
import os
import base64

from configparser import ConfigParser
import ast


############################################################
#
# classes
#
class User:

  def __init__(self, row):
    self.userid = row[0]
    self.username = row[1]
    self.pwdhash = row[2]


class Job:

  def __init__(self, row):
    self.jobid = row[0]
    self.userid = row[1]
    self.status = row[2]
    self.originaldatafile = row[3]
    self.datafilekey = row[4]
    self.resultsfilekey = row[5]


class Keywords:

  def __init__(self, row):
    self.keywordid = row[0]
    self.keyword = row[1]


############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  print()
  print(">> Enter a command:")
  print("   0 => end")
  print("   1 => users")
  print("   2 => jobs")
  print("   3 => upload")
  print("   4 => download")
  print("   5 => reset")
  print("   6 => keywords")
  print("   7 => translate pdf")

  cmd = input()

  if cmd == "":
    cmd = -1
  elif not cmd.isnumeric():
    cmd = -1
  else:
    cmd = int(cmd)

  return cmd


############################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract users:
    #
    body = res.json()

    #
    # let's map each row into a User object:
    #
    users = []
    for row in body:
      user = User(row)
      users.append(user)
    #
    # Now we can think OOP:
    #
    if len(users) == 0:
      print("no users...")
      return

    for user in users:
      print(user.userid)
      print(" ", user.username)
      print(" ", user.pwdhash)
    #
    return

  except Exception as e:
    logging.error("users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# jobs
#
def jobs(baseurl):
  """
  Prints out all the jobs in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/jobs'
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract jobs:
    #
    body = res.json()
    #
    # let's map each row into an Job object:
    #
    jobs = []
    for row in body:
      job = Job(row)
      jobs.append(job)
    #
    # Now we can think OOP:
    #
    if len(jobs) == 0:
      print("no jobs...")
      return

    for job in jobs:
      print(job.jobid)
      print(" ", job.userid)
      print(" ", job.status)
      print(" ", job.originaldatafile)
      print(" ", job.datafilekey)
      print(" ", job.resultsfilekey)
    #
    return

  except Exception as e:
    logging.error("jobs() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# upload
#
def upload(baseurl):
  """
  Prompts the user for a local filename and user id, 
  and uploads that asset (PDF) to S3 for processing. 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  print("Enter PDF filename>")
  local_filename = input()

  if not pathlib.Path(local_filename).is_file():
    print("PDF file '", local_filename, "' does not exist...")
    return

  print("Enter user id>")
  userid = input()

  try:
    #
    # build the data packet:
    #
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()

    #
    # now encode the pdf as base64. Note b64encode returns
    # a bytes object, not a string. So then we have to convert
    # (decode) the bytes -> string, and then we can serialize
    # the string as JSON for upload to server:
    #
    data = base64.b64encode(bytes)
    datastr = data.decode()

    data = {"filename": local_filename, "data": datastr}

    #
    # call the web service:
    #
    api = '/upload'
    url = baseurl + api + "/" + userid

    res = requests.post(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # success, extract jobid:
    #
    body = res.json()

    jobid = body

    print("PDF uploaded, job id =", jobid)
    return

  except Exception as e:
    logging.error("upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# download
#
def download(baseurl):
  """
  Prompts the user for the job id, and downloads
  that asset (PDF).

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  print("Enter job id>")
  jobid = input()

  try:
    #
    # call the web service:
    #
    api = '/download'
    url = baseurl + api + '/' + jobid

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract results:
    #
    body = res.json()

    datastr = body

    base64_bytes = datastr.encode()
    bytes = base64.b64decode(base64_bytes)
    results = bytes.decode()

    print(results)
    return

  except Exception as e:
    logging.error("download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# reset
#
def reset(baseurl):
  """
  Resets the database back to initial state.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/reset'
    url = baseurl + api

    res = requests.delete(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and print message
    #
    body = res.json()

    msg = body

    print(msg)
    return

  except Exception as e:
    logging.error("reset() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
# Keywords
#
def keywords(baseurl):
  """
  Prints out all the jobs in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/keywords'
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract keywords:
    #
    body = res.json()
    body_list = ast.literal_eval(body['body'])

    # Access each keyword in the list
    for item in body_list:
      # print(item)
      keyword_id, keyword = item
      print(f"Keyword ID: {keyword_id}")
      print(" ", f"Keyword: {keyword}")

    # Now we can think OOP:
    #
    if len(body_list) == 0:
      print("no keywords...")
      return

    return

  except Exception as e:
    logging.error("jobs() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


    ############################################################
    # Translate PDF
    #
def translate_pdf(baseurl):
  """
  Prompts the user for a local PDF filename and a language code, 
  sends these details to the server for translation, and displays the translated text.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """
  print("Enter PDF filename>")
  local_filename = input()

  if not pathlib.Path(local_filename).is_file():
    print("PDF file '", local_filename, "' does not exist...")
    return

  print("Enter language code (e.g., 'es' for Spanish)>")
  language_code = input()

  try:
    # Read the PDF file
    with open(local_filename, "rb") as infile:
      pdf_bytes = infile.read()

    # Encode the PDF as base64
    encoded_pdf = base64.b64encode(pdf_bytes).decode()

    # Prepare the data packet
    data = {
      "filename": local_filename,
      "data": encoded_pdf,
      "language_code": language_code
    }

    # Call the web service
    api = '/translate'
    url = f"{baseurl}{api}"

    headers = {"Content-Type": "application/json"}
    res = requests.post(url, json=data, headers=headers)

    if res.status_code != 200:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        body = res.json()
        print("Error message:", body)
      return

    # Handle the response
    body = res.json()
    translated_text = body.get("translatedText", "No translated text found.")
    print("Translated Text:\n")
    print(translated_text)

  except Exception as e:
    logging.error("translate() failed:")
    logging.error("url: " + url)
    logging.error(e)


############################################################
# main
#
try:
  print('** Welcome to BenfordApp **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = 'benfordapp-client-config.ini'

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    config_file = s

  #
  # does config file exist?
  #
  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  #
  # setup base URL to web service:
  #
  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config.ini file with your gateway endpoint")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      users(baseurl)
    elif cmd == 2:
      jobs(baseurl)
    elif cmd == 3:
      upload(baseurl)
    elif cmd == 4:
      download(baseurl)
    elif cmd == 5:
      reset(baseurl)
    elif cmd == 6:
      keywords(baseurl)
    elif cmd == 7:
      translate_pdf(baseurl)
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
