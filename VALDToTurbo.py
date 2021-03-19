"""
Contains functions for converting VALD3 line lists to Turbospectrum format using "vald3line-BPz-freeformat.exe".
Built to be used in a linux OS.

Functions:
    VALDToTurbo: Runs a single VALD line list through "vald3line-BPz-freeformat.exe" to reformat into
    Turbospectrum format.

    VALDToTurboAuto: Runs a folder full of VALD line lists through "vald3line-BPz-freeformat.exe" to reformat into
    Turbospectrum format.

    TurboSort: Takes a folder full of Turbospectrum formatted line lists and combines the atomic data from the files.

    VALDToSortedTurbo: Runs a folder full of VALD line lists through "vald3line-BPz-freeformat.exe" to reformat into
    Turbospectrum format and combines the atomic data from the files into one file.
"""


import os
import subprocess


__format_path = "/home/virtual/Turbospectrum2019-19.1.2/Utilities/vald3line-BPz-freeformat.exe"


def VALDToTurbo(input_file, output_file):
    """ Runs a single VALD line list through "vald3line-BPz-freeformat.exe" to reformat into Turbospectrum format.

    :param input_file: (str) The line list to be reformatted.
    :param output_file: (str) The reformatted line list.
    """

    shellname = os.path.dirname(__format_path) + "/format_auto.sh"
    file_string = "#!/bin/csh -f\n\n" + \
          str(__format_path) + " << EOF\n" + \
          input_file + "\n" + \
          output_file + "\n" + \
          "end\n\n"

    with open(shellname, "w") as f:
        f.write(file_string)

    os.chdir(os.path.dirname(shellname))
    subprocess.run(["csh", os.path.basename(shellname)])
    os.system("rm " + shellname)


def VALDToTurboAuto(input_folder, output_folder):
    """ Runs a folder full of VALD line lists through "vald3line-BPz-freeformat.exe" to reformat into
    Turbospectrum format.

    :param input_folder: (str) The folder containing the line lists to be reformatted.
    :param output_folder: (str) The folder where the reformatted line lists will go.
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for linelist in [file for file in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, file))]:
        outfile = os.path.join(output_folder, os.path.splitext(linelist)[0] + "_TS.lst")
        VALDToTurbo(os.path.join(input_folder, linelist), outfile)


def TurboSort(input_folder, output_file):
    """ Takes a folder full of Turbospectrum formatted line lists and combines the atomic data from the files into
    one file.

    :param input_folder: (str) The folder that contains your line lists (should only contain those line list files).
    :param output_file: (str) The desired output file name.
    """

    atom_dict = {}
    for linelist in os.listdir(input_folder):
        file_line = 1
        with open(os.path.join(input_folder, linelist), "r") as fin:
            lines = fin.readlines()
            while file_line < len(lines):
                line_index = file_line - 1
                header, atomic_sym = lines[line_index], lines[line_index + 1]
                atomic_lines = int(header.split()[4])
                start = line_index + 2
                end = start + atomic_lines
                splice = lines[start: end]
                file_line = end + 1
                if atomic_sym in atom_dict.keys():
                    atomic_lines_previous = int(atom_dict[atomic_sym][0].split()[4])
                    atomic_lines += atomic_lines_previous
                    start_line, end_line_previous = atom_dict[atomic_sym][0][:27], atom_dict[atomic_sym][0][27:]
                    end_line_updated = end_line_previous.replace(str(atomic_lines_previous), str(atomic_lines))
                    if len(end_line_updated) > 10:
                        diff = len(end_line_updated) - 10
                        end_line_updated = end_line_updated[diff:]
                        atom_dict[atomic_sym][0] = start_line + end_line_updated
                    elif len(end_line_updated) < 10:
                        diff = 10 - len(end_line_updated)
                        atom_dict[atomic_sym][0] = start_line + " "*diff + end_line_updated
                    else:
                        atom_dict[atomic_sym][0] = start_line + end_line_updated
                    # Sorts each element by wavelength
                    atom_dict[atomic_sym].extend(splice)
                    temp = atom_dict[atomic_sym][2:]
                    temp.sort()
                    atom_dict[atomic_sym] = atom_dict[atomic_sym][:2]
                    atom_dict[atomic_sym].extend(temp)
                else:
                    header = [header, atomic_sym]
                    header.extend(splice)
                    atom_dict[atomic_sym] = header

    # Sorts each element block by atomic number
    vals = list(atom_dict.values())
    for val in vals:
        "\n".join(val)
    vals.sort()
    lines = []
    for val in vals:
        lines.extend(val)

    with open(output_file, "w") as fout:
        for line in lines:
            fout.write(line)


def VALDToSortedTurbo(input_folder, output_file):
    """ Runs a folder full of VALD line lists through "vald3line-BPz-freeformat.exe" to reformat into Turbospectrum
    format and combines the atomic data from the files into one file.

    :param input_folder: (str) The folder containing the line lists to be reformatted.
    :param output_file: (str) The desired name of the formatted and combined output file.
    """

    temp_folder = input_folder + "tmp/"
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    VALDToTurboAuto(input_folder, temp_folder)
    TurboSort(temp_folder, output_file)
    for root, dirs, files in os.walk(temp_folder):
        for file in files:
            os.remove(os.path.join(root, file))
    os.rmdir(temp_folder)
