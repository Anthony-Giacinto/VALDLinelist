# VALDLinelist
This script contains some functions for downloading and manipulating Vienna Atomic Line Database (VALD) formatted line lists. Can reformat a VALD3 line list for use with Dr. Gray's SPECTRUM or for Dr. Plez's line list re-formatting file, "vald3line-BPz-freeformat.f" in TURBOSPECTRUM and for using this re-formatting file.

## Table of Contents
* [General info](#general-info)
* [On First Use](#on-first-use)
* [Functions](#functions)

## General Info

These scripts are meant for use with:
* The VALD Database as of 2/15/21 (http://vald.astro.uu.se/~vald/php/vald.php)
* Dr. Plez's "vald3line-BPz-freeformat.f" for Turbospectrum as of 3/28/19 (https://www.lupm.in2p3.fr/users/plez/).
* Dr. Gray's SPECTRUM v2.76 (https://www.appstate.edu/~grayro/spectrum/spectrum.html)  
---------------------------------------------------------------------------------------------------------------------------------  
*VALDLinelist.py:*  

This script was designed in a Windows 10 OS.  

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
---------------------------------------------------------------------------------------------------------------------------------  
*VALDToTurbo.py:*  

This script was designed for use in a linux OS.

---------------------------------------------------------------------------------------------------------------------------------  

## On First Use
---------------------------------------------------------------------------------------------------------------------------------  
*VALDLinelist.py:*  

* Make sure that you follow the GMAIL API link from *General Info* if you wish to use VALDEmail() or VALDDownload().
* In VALDForm(), change:
  1. *email=""*  -->  *email=YOUR_EMAIL_ADDRESS*
  2. *web_driver=""*  -->  *web_driver=LOCATION_OF_WEBDRIVER*
* In VALDDownload(), change:
  1. *email=""*  -->  *email=YOUR_EMAIL_ADDRESS*
  2. *web_driver=""*  -->  *web_driver=LOCATION_OF_WEBDRIVER*
  3. *download_folder=""*  -->  *download_folder=LOCATION_OF_YOUR_DOWNLOAD_FOLDER*  
---------------------------------------------------------------------------------------------------------------------------------  
*VALDToTurbo.py:*  

* Change the global variable, "format_path", to the location of your "vald3line-BPz-freeformat" executable file.  
---------------------------------------------------------------------------------------------------------------------------------  

## Functions
---------------------------------------------------------------------------------------------------------------------------------  
*VALDLinelist.py:*  

* VALDForm(): Fills out the Extract All form on the VALD website ("http://vald.astro.uu.se/"). The VALD website might not give the full wavelength range of data. For large wavelength ranges, one must fill out multiple forms or use VALDDownload().
* VALDEmail(): Uses the Gmail API to grab the newest gmail email from VALD and returns the message along with the received date. This function requires a credentials.JSON file and a token.pickle file that gives this function permission to view your Gmail account.
* VALDDownload(): Fills out the Extract All form on the VALD website ("http://vald.astro.uu.se/") as many times as needed to extract the desired wavelength range, accesses your Gmail emails from VALD to click the download links, and saves the un-zipped versions of the files to the desired output folder.
* VALDFormat(): Updates the 4th element lines within a single line list so that they will work with Turbospectrum's "vald3line-BPz-freeformat". Use VALDCombineFormat if you also want to combine VALD files.
* VALDCombineNoFormat(): Appends multiple VALD line lists together while NOT updating the 4th element lines.
* VALDCombineFormat(): Appends multiple VALD line lists together while also updating the 4th element lines so that they will work with Turbospectrum's "vald3line-BPz-freeformat".
* VALDSplit(): Splits a VALD line list file into multiple files of the desired file size. Used for input into Turbospectrum's "vald3line-BPz-freeformat" which has an input file size limit (~100 mb).
* VALDToSpectrum(): Converts a VALD formatted line list into a SPECTRUM (https://www.appstate.edu/~grayro/spectrum/spectrum.html) formatted line list.  
--------------------------------------------------------------------------------------------------------------------------------- 
*VALDToTurbo.py:*  

* VALDToTurbo(): Runs a single VALD line list through "vald3line-BPz-freeformat.exe" to reformat into Turbospectrum format.
* VALDToTurboAuto(): Runs a folder full of VALD line lists through "vald3line-BPz-freeformat.exe" to reformat into Turbospectrum format.
* TurboSort(): Takes a folder full of Turbospectrum formatted line lists and combines the atomic data from the files.
* VALDToSortedTurbo(): Runs a folder full of VALD line lists through "vald3line-BPz-freeformat.exe" to reformat into Turbospectrum format and combines the atomic data from the files into one file.  
--------------------------------------------------------------------------------------------------------------------------------- 
