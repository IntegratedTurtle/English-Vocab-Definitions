import csv
import re
import requests
import shutil
import time

from nltk.corpus import wordnet
from PyDictionary import PyDictionary

##################################################
#                                                #
# Make sure that the english unformated words    #  
# are in the first column and the second row     #
# is empty. The third row is for the definitions #
#                                                #
##################################################

def clean_csv(csvfile="", makecopy=True):
    """
    Cleans up a CSV file by combining the 4th, 5th, 6th and 7th column in each row.
    (Is to get rid of a specific problem of mine)
    
    Args:
    - csvfile (str): The path to the CSV file to be cleaned.
    - makecopy (bool): Whether or not to create a copy of the original file before modifying it.

    Returns:
    - None
    """
    
    vocabs = []
    new_rows = []

    # create a copy of the current file in the same directory
    if makecopy:
        shutil.copyfile(csvfile, csvfile[:-4] + '_copy.csv')

    # read the content of the file
    with open(csvfile, "r") as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:
            
            # append empty items to the row to fill up the seven columns
            while len(row) < 7:
                row.append("")
            # add the values of the 5th, 6th, and 7th columns to the 4th column separated by a comma
            row[3] = f"{row[3]} {row[4]} {row[5]} {row[6]}"
            # remove the 5th, 6th, and 7th columns
            row.pop(4)
            row.pop(4)
            row.pop(4)
            # append the modified row to the new list
            new_rows.append(row)

    # write the modified rows to the new file
    with open(csvfile, "w", newline="") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(new_rows)

def clean_words(csvfile="", makecopy=True):
    """
    Takes the path of the csvfile and writes directly in it.
    Make sure it is formatted correctly. Otherwise the script will overwrite the existing file.

    Args:
    - csvfile (str): path of the csv file to be cleaned
    - makecopy (bool): whether to create a copy of the original file or not

    Returns:
    - None
    """

    vocabs = []

    # create a copy of the current file in the same directory
    if makecopy:
        shutil.copyfile(csvfile, csvfile[:-4] + '_copy.csv')

    # read the content of the file
    with open(csvfile, "r") as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:
            vocabs.append(row)

        # format the vocabs in the second row
        for vocabulary in vocabs:
            if vocabulary[1] == "":
                continue
            else:
                # clean the vocabulary string
                vocabulary[1] = vocabulary[1].replace("(to)", "").replace("sb./ sth.", " ").replace("sth./ sb.", " ").replace("sb./sth.", " ").replace("sth./sb.", " ").replace("sth.", "").replace("sb.", "").replace(" sth", " ").replace(" sb ", " ").replace("(n)", "").replace("for/to", "").replace(" 's ", " ")
                vocabulary[1] = re.sub(r'\(.*?\)', '', vocabulary[1]) # get rid of braces
                vocabulary[1] = re.sub(r'\[.*?\]', '', vocabulary[1]) # get rid of braces
                vocabulary[1] = vocabulary[1].strip() # delete unnecessary spaces

        print(vocabs[5])

    # write changes to file
    with open(csvfile, "w") as file:
        csv_writer = csv.writer(file)

        for vocabulary in vocabs:
            csv_writer.writerow(vocabulary)

def write_defs(csvfile="", makecopy=True):
    """
    This function takes a CSV file containing English vocabulary words in the second column and writes their definitions
    in the third column using OxfordLearnersDictionaries.

    Args:
    - csvfile (str): The path to the CSV file containing the vocabulary words and definitions
    - makecopy (bool): Whether to create a copy of the original file before making changes, defaults to True
    Returns:
    - None
    """

    # create a copy of the current file in the same directory
    if makecopy:
        shutil.copyfile(csvfile, csvfile[:-4] + '_copy.csv')
    # read the content of the file
    vocabs = []
    url = "https://www.oxfordlearnersdictionaries.com/definition/english/"
    with open(csvfile, "r") as file:
        csv_reader = csv.reader(file)

        # append each row to the vocabs list
        for row in csv_reader:
            vocabs.append(row)

        # get the definition of the vocabulary in the second column
        for i, vocabulary in enumerate(vocabs):
            print(f"\nRow{i}: {vocabulary} ")
            # skip empty vocabulary words
            if vocabulary[1] == "":
                continue
            else:
                response = requests.get(url+vocabulary[1].replace(" ", "-"), headers={"User-Agent":"Mozilla/5.0"})
                time.sleep(1)
                site = response.content

                pattern1 = r'<span class="def" hclass="def" htag="span">(.+?)</span>'
                pattern2 = r'<span class="def" htag="span" hclass="def">(.+?)</span>'

                match = re.search(pattern1, site.decode('utf-8'))
                if match == None:
                    match = re.search(pattern2, site.decode('utf-8'))

                if match != None:
                    definition = match.group(1)
                    definition = re.sub(r'<.*?>', '', definition) # exclude everything between < and > signs
                    vocabulary[2] = definition
                    print(f"Vocabulary: {vocabulary[1]}\nDefinition: {definition}")
                else:
                    print(f"No Match for: {vocabulary[1]}")
                    vocabulary[2] = ""

            # write changes to file every ten rows
            if (i+1) % 10 == 0:
                with open(csvfile, "w") as file:
                    csv_writer = csv.writer(file)
                    for row in vocabs:
                        csv_writer.writerow(row)

    # write changes to file
    with open(csvfile, "w") as file:
        csv_writer = csv.writer(file)

        for vocabulary in vocabs:
            csv_writer.writerow(vocabulary)

def get_nodef(csvfile=""):
    """
    Returns all rows where there is text in the second but not in the third column.

    Args:
    - csvfile (str): The path to the CSV file

    Returns:
    - rows (list): A list of the content of all rows that miss definitions
    """
    with open(csvfile, "r") as f:
        reader = csv.reader(f)
        rows = [row for row in reader if row[1] and not row[2]]
    return rows

def write_defs(csvfile="", dictionary={}, makecopy=True):
    """
    Goes through every line of a given csvfile and looks the first column up in a dictionary.
    If it fits than write the content of the entry in the third column of the same row.

    Args:
    - csvfile (str): The path to the CSV file to be updated.
    - dictionary (dict): A dictionary containing the words to be looked up and their definitions.
    - makecopy (bool): Whether or not to create a copy of the original CSV file before updating it.

    Returns:
    - None
    """
    # create a copy of the current file in the same directory
    if makecopy:
        shutil.copyfile(csvfile, csvfile[:-4] + '_copy.csv')
    with open(csvfile, "r") as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            row[0] = row[0].strip()
            if row[0] in dictionary:
                row[2] = dictionary[row[0]]
            elif row[0].replace("(to) ", "") in dictionary:
                row[2] = dictionary[row[0].replace("(to) ", "")]
            rows.append(row)
    with open(csvfile, "w") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

