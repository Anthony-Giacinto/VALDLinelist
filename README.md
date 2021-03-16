# VALDLinelist
This script contains some functions for downloading and manipulating Vienna Atomic Line Database (VALD) formatted line lists.

## Table of Contents
* [General info](#general-info)
* [Functions](#functions)
* [On First Use](#on-first-use)

## General Info
This script was designed in a Windows 10 OS and was meant for use with:
* The VALD Database as of 2/15/21 (http://vald.astro.uu.se/~vald/php/vald.php)
* Plez's "vald3line-BPz-freeformat" for Turbospectrum as of 3/28/19 (https://www.lupm.in2p3.fr/users/plez/).
* Dr. Gray's SPECTRUM v2.76 (https://www.appstate.edu/~grayro/spectrum/spectrum.html)  

Some of these functions require the use of google chrome web driver. You can download one here:
* https://sites.google.com/a/chromium.org/chromedriver/downloads  

Some of these functions require the use of the GMAIL API for downloading requested VALD data. For those functions to work, you must follow the instrunctions given here:
* https://developers.google.com/gmail/api/quickstart/python  

You must keep the files that were generated from the GMAIL API instructions in the same directory as VALDLinelist.py. This should allow VALDEmail() to access your gmail emails to look for emails send from VALD.  
  
If you do not wish to follow the instructions from the GMAIL API link, you may remove VALDEmail() and VALDDownload() from VALDLinelist.py, and you may remove these imports from the script as well:
* "import pickle"
* "from googleapiclient.discovery import build"
* "from google_auth_oauthlib.flow import InstalledAppFlow"
* "from google.auth.transport.requests import Request"
* "import base64"
* "import datetime"
* "import gzip"
* "import time"

## Functions
* VALDForm(): Fills out the Extract All form on the VALD website ("http://vald.astro.uu.se/"). The VALD website might not give the full wavelength range of data. For large wavelength ranges, one must fill out multiple forms or use VALDDownload().
* VALDEmail(): Uses the Gmail API to grab the newest email from VALD and returns the message along with the received date. This function requires a credentials.JSON file and a token.pickle file that gives this function permission to view your Gmail account.
* VALDDownload(): Fills out the Extract All form on the VALD website ("http://vald.astro.uu.se/") as many times as needed to extract the desired wavelength range, accesses your Gmail emails from VALD to click the download links, and saves the un-zipped versions of the files to the desired output folder.
* VALDFormat(): Updates the 4th element lines within a single line list so that they will work with Turbospectrum's "vald3line-BPz-freeformat". Use VALDCombineFormat if you also want to combine VALD files.
* VALDCombineNoFormat(): Appends multiple VALD line lists together while NOT updating the 4th element lines.
* VALDCombineFormat(): Appends multiple VALD line lists together while also updating the 4th element lines so that they will work with Turbospectrum's "vald3line-BPz-freeformat".
* VALDSplit(): Splits a VALD line list file into multiple files of the desired file size. Used for input into Turbospectrum's "vald3line-BPz-freeformat" which has an input file size limit (~100 mb).
* VALDToSpectrum(): Converts a VALD formatted line list into a SPECTRUM (https://www.appstate.edu/~grayro/spectrum/spectrum.html) formatted line list.

## On First Use
* Make sure that you follow the GMAIL API link from *General Info* if you wish to use VALDEmail() or VALDDownload().
* In VALDForm(), change:
  1. *email=""* to *email=YOUR_EMAIL_ADDRESS*
  2. *web_driver=""* to *web_driver=LOCATION_OF_WEBDRIVER*
* In VALDDownload(), change:
  1. *email=""* to *email=YOUR_EMAIL_ADDRESS*
  2. *web_driver=""* to *web_driver=LOCATION_OF_WEBDRIVER*
  3. *download_folder=""* to *download_folder=LOCATION_OF_YOUR_DOWNLOAD_FOLDER*
