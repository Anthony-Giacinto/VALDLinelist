"""
This script contains some functions for downloading and manipulating Vienna Atomic Line Database (VALD) formatted
line lists.

This code was meant for use with the VALD Database as of 2/15/21 (http://vald.astro.uu.se/~vald/php/vald.php)
and for "vald3line-BPz-freeformat" as of 3/28/19 (https://www.lupm.in2p3.fr/users/plez/).

Functions:
    VALDForm: Fills out the Extract All form on the VALD website ("http://vald.astro.uu.se/"). The VALD website
    might not give the full wavelength range of data. For large wavelength ranges, one must fill out multiple forms or
    use VALDDownload.

    VALDEmail: Uses the Gmail API to grab the newest email from VALD and returns the message along with the
    received date. This function requires a credentials.JSON file and a token.pickle file that gives this function
    permission to view your Gmail account.

    VALDDownload: Fills out the Extract All form on the VALD website ("http://vald.astro.uu.se/") as many
    times as needed to extract the desired wavelength range, accesses your Gmail emails from VALD to click the
    download links, and saves the un-zipped versions of the files to the desired output folder.

    VALDFormat: Updates the 4th element lines within a single line list so that they will work with
    Turbospectrum's "vald3line-BPz-freeformat". Use VALDCombineFormat if you also want to combine VALD files.

    VALDCombineNoFormat: Appends multiple VALD line lists together while NOT updating the 4th element lines.

    VALDCombineFormat: Appends multiple VALD line lists together while also updating the 4th element lines so
    that they will work with Turbospectrum's "vald3line-BPz-freeformat".

    VALDSplit: Splits a VALD line list file into multiple files of the desired file size. Used for input
    into Turbospectrum's "vald3line-BPz-freeformat" which has an input file size limit (~100 mb).

    VALDToSpectrum: Converts a VALD formatted line list into a SPECTRUM (https://www.appstate.edu/~grayro/spectrum/spectrum.html)
    formatted line list.
"""


import os
import time
import gzip
import datetime
import base64
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def VALDForm(wave_start, wave_end, extraction_format="long", data_retrieval="ftp", linelist_config="custom", comment="",
             email="", web_driver="", server="uppsala", show_browser=False):
    """ Fills out the Extract All form on the VALD website ("http://vald.astro.uu.se/"). The VALD website
    might not give the full wavelength range of data. For large wavelength ranges, one must fill out multiple forms or
    use VALDDownload.

    This function requires the use of Selenium and a chrome driver
    (https://sites.google.com/a/chromium.org/chromedriver/downloads).

    :param wave_start: (float) The desired starting wavelength value in angstroms.
    :param wave_end: (float) The desired ending wavelength value in angstroms.
    :param extraction_format: (str) The desired extraction formatting; Long or Short (default is "long").
    :param data_retrieval: (str) The desired data retrieval method; Email or FTP (default is "ftp").
    :param linelist_config: (str) The desired line list configuration; Default or Custom (default is custom).
    :param comment: (str) An optional comment that can be added to the request (default is "").
    :param email: (str) Your registered VALD email address.
    :param web_driver: (str) The path to your Chrome driver.
    :param server: (str) The desired server; moscow, montpellier, or uppsala (default is "uppsala").
    :param show_browser: (bool) Opens up your web browser while running (default is False).
    """

    # Find the Chrome webdriver
    if show_browser:
        driver = webdriver.Chrome(web_driver)
    else:
        option = webdriver.ChromeOptions()
        option.add_argument("headless")
        driver = webdriver.Chrome(web_driver, options=option)

    # Go to VALD Interface
    driver.get("http://vald.astro.uu.se/")

    # Choose the server
    server = server.lower()
    if isinstance(server, str) and (server == "montpellier" or server == "moscow"):
        server_dict = {"moscow": "VALD3 Mirror Moscow", "montpellier": "VALD3 Mirror Montpellier"}
        driver.find_element_by_link_text(server_dict[server]).click()

    # Log in with a registered email address
    login = driver.find_element_by_name("user")
    login.send_keys(email)
    login.send_keys(Keys.RETURN)

    # Select the Extract All option and fill out the form
    driver.find_element_by_xpath("//input[@value='Extract All']").send_keys(Keys.RETURN)
    driver.find_element_by_xpath("//table/tbody/tr[2]/td[2]/input").send_keys(str(wave_start))
    driver.find_element_by_xpath("//table/tbody/tr[3]/td[2]/input").send_keys(str(wave_end))
    if extraction_format.lower() == "long":
        driver.find_element_by_xpath("//table/tbody/tr[5]/td[2]/input").click()
    if data_retrieval.lower() == "ftp":
        driver.find_element_by_xpath("//table/tbody/tr[7]/td[2]/input").click()
    if linelist_config.lower() == "custom":
        driver.find_element_by_xpath("//table/tbody/tr[18]/td[2]/input").click()
    if comment != "" and isinstance(comment, str):
        driver.find_element_by_xpath("//table/tbody/tr[22]/td[2]/input").send_keys(comment)
    driver.find_element_by_xpath("//table/tbody/tr[24]/td[1]/input").send_keys(Keys.RETURN)

    # Quits the driver
    driver.quit()


def VALDEmail(VALDserver="uppsala", display_message=True):
    """ Uses the Gmail API to grab the newest email from VALD and returns the message along with the received date.
    This function requires a credentials.JSON file and a token.pickle file that gives this function permission
    to view your Gmail account.

    Used this link to start working with the Gmail API:
    https://developers.google.com/gmail/api/quickstart/python

    :param VALDserver: (str) The server that the email will be coming from; uppsala, montpellier, or moscow
    (default is "uppsala").
    :param display_message: (bool) Prints the email message to the console (default is True).
    :return: (str/NoneType) The message from the VALD email. If no such email exists, returns None.
    """

    server = {"uppsala": "vald@physics.uu.se", "montpellier": "vald@vald.lupm.univ-montp2.fr",
              "moscow": "vald3@inasan.ru"}

    # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None

    # The file token.pickle contains the user access token.
    # Check if it exists
    if os.path.exists('token.pickle'):
        # Read the token from the file and store it in the variable creds
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If credentials are not available or are invalid, ask the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.readonly'])
            creds = flow.run_local_server(port=0)

        # Save the access token in token.pickle file for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Connect to the Gmail API
    service = build('gmail', 'v1', credentials=creds)

    # Request the newest VALD message and decode it
    result = service.users().messages().list(userId='me', labelIds=['INBOX'], q=server[VALDserver.lower()]).execute()
    message = result.get('messages', [])[0]
    if not message:
        return None
    else:
        txt = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = txt['payload']
        date_line = payload['headers'][1]['value']
        date = date_line[date_line.index(';') + 1:].lstrip()
        parts = payload.get('parts')

        # Grab the correct email from an email chain
        for part in parts:
            try:
                data = part['body']['data'].replace("-", "+").replace("_", "/")
                decoded_data = date + '\n' + str(base64.b64decode(data), 'utf-8')
                if "http://" in decoded_data:
                    if display_message:
                        print(decoded_data)
                    return decoded_data
            except:
                return None


def VALDDownload(output_folder, wave_start, wave_end, extraction_format="long", data_retrieval="ftp",
                 linelist_config="custom", email="", server="uppsala", web_driver="", download_folder="", silent=False,
                 show_browser=False):
    """ Fills out the Extract All form on the VALD website ("http://vald.astro.uu.se/") as many times as needed to
    extract the desired wavelength range, accesses your Gmail emails from VALD to click the download links, and saves
    the un-zipped versions of the files to the desired output folder.

    Used this link to start working with the Gmail API:
    https://developers.google.com/gmail/api/quickstart/python

    :param output_folder: (str) The desired output folder for the unzipped VALD files.
    :param wave_start: (float) The desired starting wavelength value in angstroms.
    :param wave_end: (float) The desired ending wavelength value in angstroms.
    :param extraction_format: (str) The desired extraction formatting; Long or Short (default is "long").
    :param data_retrieval: (str) The desired data retrieval method; Email or FTP (default is "ftp").
    :param linelist_config: (str) The desired line list configuration; Default or Custom (default is custom).
    :param email: (str) Your registered VALD email address.
    :param server: (str) The desired server; moscow, montpellier, uppsala, or vienna (default is "uppsala").
    :param web_driver: (str) The path to your Chrome driver.
    :param download_folder: (str) The path to your download folder.
    :param silent: (bool) Will not print lines to the console (default is False).
    :param show_browser: (bool) Opens up your web browser while running (default is False).
    """

    month_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                  "Nov": 11, "Dec": 12}

    last_wavelength, count = 0, 1
    while last_wavelength < wave_end:

        # Fills out the Extract All form on VALD website
        VALDForm(wave_start, wave_end+5, extraction_format=extraction_format, data_retrieval=data_retrieval,
                 linelist_config=linelist_config, comment="Range " + str(count), email=email, server=server,
                 web_driver=web_driver, show_browser=show_browser)
        start_date = datetime.datetime.now()

        # Finds the VALD download link in my email and downloads the file
        wait_time = 0
        if not silent:
            print("\n---------------------------------------------------------------------\n",
                  "Waiting for an email(" + str(count) + ") from VALD...")
        while True:
            message = VALDEmail(server, display_message=False)
            if message is not None:
                date = message.split("\n")[0].split()
                year, month, day = int(date[3]), month_dict[date[2]], int(date[1])
                hour, minute, second = int(date[4][:2].lstrip("0")), int(date[4][3:5].lstrip("0")), int(date[4][6:8].lstrip("0"))
                received_date = datetime.datetime(year, month, day, hour, minute, second)
                if received_date > start_date:
                    break
            time.sleep(60)
            wait_time += 60
            if wait_time > 1800:
                if not silent:
                    print("\nEmail was not received in time.\nTry a different server.")
                break
            else:
                if not silent:
                    print("Still waiting for email(" + str(count) + ")...")
        if wait_time > 1800:
            break
        if not silent:
            print("Found email(" + str(count) + ") from VALD: \n", message, "\n")
        link = message[message.index("http"): message.index("gz")+2]
        request_num = link.split(".")[4]
        if show_browser:
            driver = webdriver.Chrome(web_driver)
        else:
            option = webdriver.ChromeOptions()
            option.add_argument("headless")
            driver = webdriver.Chrome(web_driver, options=option)
        driver.get(link)

        # Unzips the downloaded VALD file
        file_not_downloaded = True
        if not silent:
            print("Waiting for VALD file(" + str(count) + ") to download...")
        while file_not_downloaded:
            # To make sure that the file is fully downloaded
            time.sleep(5)
            for file in os.listdir(download_folder):
                if request_num in file and "crdownload" not in file:
                    input_name = os.path.join(download_folder, file)
                    output_name = os.path.join(output_folder, os.path.splitext(file)[0] + "_" + str(count) + ".lst")
                    with gzip.open(input_name, mode="rt") as fin:
                        out = fin.read()
                        with open(output_name, "w") as fout:
                            fout.write(out)
                    os.remove(input_name)
                    file_not_downloaded = False
                    break
            if not silent:
                print("Still waiting for file(" + str(count) + ")...")
        if not silent:
            print("VALD file(" + str(count) + ") downloaded.\n")

        # Finds the last wavelength value
        with open(output_name, "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if " References:" in line:
                    last_wavelength = wave_start = float(lines[lines.index(line) - 5].split()[2][:-1])
                    break
        if not silent:
            print("Last wavelength value for file(" + str(count) + "): " + str(last_wavelength))
        count += 1
        driver.quit()


def VALDFormat(input_file, output_file, silent=True):
    """ Updates the 4th element lines within a single line list so that they will work
    with Turbospectrum's "vald3line-BPz-freeformat". Use VALDCombineFormat if you also want to combine VALD files.

    :param input_file: (str) The input file name.
    :param output_file: (str) The output file name.
    :param silent: (bool) Will not print lines to the console (default is True).
    """

    stop_string = "* oscillator strengths"
    with open(input_file, "r") as fin:
        with open(output_file, "a") as fout:
            for line in fin:
                if stop_string in line:
                    break
                elif line[0] == "'":
                    if ":" in line:
                        # Finds the element symbol string at the end of the 4th element line.
                        chars = line[line.rfind(" "):-2]
                        # Finds any atomic masses in parenthesis within the element symbol strings.
                        r = [i for i in range(len(chars)) if chars[i] == ")"]
                        l = [j for j in range(len(chars)) if chars[j] == "("]
                        # Removes the atomic masses from the element symbol strings.
                        if len(l) > 0:
                            chars = "".join([chars[r[-1]+1:] if k == range(len(l))[-1] else chars[r[k]+1:l[k+1]]
                                             for k in range(len(l))])
                        file_line = "'_" + " " * 29 + chars + " " * 5 + "'\n"
                    else:
                        file_line = line
                    if not silent:
                        print(file_line)
                    fout.write(file_line)


def VALDCombineNoFormat(input_folder, output_file, silent=True):
    """ Appends multiple VALD line lists together while NOT updating the 4th element lines.

    :param input_folder: (str) The input folder; Must only contain VALD line list files!
    :param output_file: (str) The desired output file name.
    :param silent: (bool) Will not print lines to the console (default is True).
    """

    stop_string = "* oscillator strengths"
    for input_file in [file for file in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, file))]:
        with open(input_folder + "\\" + input_file, "r") as fin:
            with open(output_file, "a") as fout:
                for line in fin:
                    if stop_string in line:
                        break
                    elif line[0] == "'":
                        fout.write(line)
                        if not silent:
                            print(line)


def VALDCombineFormat(input_folder, output_file, silent=True):
    """ Appends multiple VALD line lists together while also updating the 4th element lines so that they will work
    with Turbospectrum's "vald3line-BPz-freeformat".

    :param input_folder: (str) The input folder; Must only contain VALD line list files!
    :param output_file: (str) The desired output file name.
    :param silent: (bool) Will not print lines to the console (default is True).
    """

    if os.path.exists(output_file):
        os.remove(output_file)
    
    for input_file in [file for file in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, file))]:
        VALDFormat(input_folder + "\\" + input_file, output_file, silent=silent)


def VALDSplit(input_file, max_size=(100, "mb"), silent=True):
    """ Splits a VALD line list file into multiple files of roughly the desired file size (never larger).
    Used for input into Turbospectrum's "vald3line-BPz-freeformat" which has an input file size limit (~100 mb).

    :param input_file: (str) The name of the VALD line list.
    :param max_size: (tuple(int, str)) The desired maximum size of the output files with units
    of "b", "kb", "mb", or "gb"; (the value, the unit) (default is (150, "mb")).
    :param silent: (bool) Will not print lines to the console; recommended for larger files (default is True).
    """

    byte_dict = {"b": 1, "kb": 1e3, "mb": 1e6, "gb": 1e9}
    max_size = max_size[0]*byte_dict[max_size[1].lower()]
    with open(input_file, "r") as fin:
        lines, file_num = fin.readlines(), 1
        while lines:
            with open(os.path.splitext(input_file)[0] + "_" + str(file_num) + ".cut", "w", encoding="utf-8") as fout:
                length = 0
                for index, line in enumerate(lines, 1):
                    length += len(line) + 1  # number of characters per line including "\n"
                    fout.write(line)
                    if not silent:
                        print(line.rstrip("\n"))
                    if max_size - length < 500 and line[1] == "_":
                        new_start = index
                        break
                lines = lines[new_start:]
                file_num += 1


def VALDToSpectrum(input_file, output_file, eV=True, isotope=False, silent=False):
    """ Converts a VALD formatted line list into a SPECTRUM (https://www.appstate.edu/~grayro/spectrum/spectrum.html)
    formatted line list.

    SPECTRUM line list format:
    wavelength, species_code, mass_number (for isotope mode), e_low, e_high, loggf, fudge_factor, transition, source

    :param input_file: (str) The VALD formatted file.
    :param output_file: (str) The name of the SPECTRUM formatted output file.
    :param eV: (bool) True if the energy unit is eV, False for cm**-1 (default is True).
    :param isotope: (bool) True if you want to add the mass_number column (default is False).
    :param silent: (bool) Will not print lines to the console (default is False).
    """

    elem_dict = {'H': '1', 'He': '2', 'Li': '3', 'Be': '4', 'B': '5', 'C': '6', 'N': '7', 'O': '8', 'F': '9',
                 'Ne': '10', 'Na': '11', 'Mg': '12', 'Al': '13', 'Si': '14', 'P': '15', 'S': '16', 'Cl': '17',
                 'Ar': '18', 'K': '19', 'Ca': '20', 'Sc': '21', 'Ti': '22', 'V': '23', 'Cr': '24', 'Mn': '25',
                 'Fe': '26', 'Co': '27', 'Ni': '28', 'Cu': '29', 'Zn': '30', 'Ga': '31', 'Ge': '32', 'As': '33',
                 'Se': '34', 'Br': '35', 'Kr': '36', 'Rb': '37', 'Sr': '38', 'Y': '39', 'Zr': '40', 'Nb': '41',
                 'Mo': '42', 'Tc': '43', 'Ru': '44', 'Rh': '45', 'Pd': '46', 'Ag': '47', 'Cd': '48', 'In': '49',
                 'Sn': '50', 'Sb': '51', 'Te': '52', 'I': '53', 'Xe': '54', 'Cs': '55', 'Ba': '56', 'La': '57',
                 'Ce': '58', 'Pr': '59', 'Nd': '60', 'Pm': '61', 'Sm': '62', 'Eu': '63', 'Gd': '64', 'Tb': '65',
                 'Dy': '66', 'Ho': '67', 'Er': '68', 'Tm': '69', 'Yb': '70', 'Lu': '71', 'Hf': '72', 'Ta': '73',
                 'W': '74', 'Re': '75', 'Os': '76', 'Ir': '77', 'Pt': '78', 'Au': '79', 'Hg': '80', 'Tl': '81',
                 'Pb': '82', 'Bi': '83', 'Po': '84', 'At': '85', 'Rn': '86', 'Fr': '87', 'Ra': '88', 'Ac': '89',
                 'Th': '90', 'Pa': '91', 'U': '92'}

    ion_dict = {'1': '.0', '2': '.1', '3': '.2', '4': '.3', '5': '.4', '6': '0.5', '7': '0.6', '8': '0.7',
                '9': '0.8', '10': '0.9'}

    mol_dict = {'MgH': '112.0', 'TiO': '822.0', 'C2': '606.0', 'H2': '101.0', 'CN': '607.0', 'SiO': '814.0',
                'CH': '106.0', 'OH': '608.0', 'SiH': '114'}

    with open(input_file, "r") as fin:
        with open(output_file, "w") as fout:
            for line in fin:
                line = line.split(",")
                if isinstance(line, list) and len(line) >= 13:
                    symbol = line[0][1:line[0].index(" ")]
                    element = elem_dict.get(symbol)
                    if element is None:
                        code = mol_dict.get(symbol)
                    else:
                        code = element + ion_dict.get(line[0][line[0].index(" ")+1:-1])

                    wavelength = "{:<12}".format(line[1].strip())
                    species_code = "{:<8}".format(code)
                    if isotope:
                        mass_number = "{:<4}".format("0")  # for isotope mode
                    else:
                        mass_number = ""
                    if eV:
                        e_low = "{:<12}".format(int(float(line[3].strip())/1.23981e-4))
                        e_high = "{:<12}".format(int(float(line[5].strip())/1.23981e-4))
                    else:
                        e_low = "{:<12}".format(int(line[3].strip()))
                        e_high = "{:<12}".format(int(line[5].strip()))
                    loggf = "{:<12}".format(line[2])
                    fudge = "{:<10}".format("1.000")
                    transition = "{:<4}".format("99")
                    source = "{:<8}".format("VALD")

                    out = wavelength + species_code + mass_number + e_low + e_high + loggf + fudge + transition + source
                    fout.write(out + "\n")
                    if not silent:
                        print(out)
                elif line[0] == "*":
                    break
