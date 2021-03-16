# VALDLinelist
This script contains some functions for downloading and manipulating Vienna Atomic Line Database (VALD) formatted line lists.

## Table of Contents
* [General info](#general-info)
* [Start Up](#start-up)

## General Info
This script was meant for use with:
* The VALD Database as of 2/15/21 (http://vald.astro.uu.se/~vald/php/vald.php)
* Plez's "vald3line-BPz-freeformat" for Turbospectrum as of 3/28/19 (https://www.lupm.in2p3.fr/users/plez/).
* Dr. Gray's SPECTRUM v2.76 (https://www.appstate.edu/~grayro/spectrum/spectrum.html)  

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

## Start Up

