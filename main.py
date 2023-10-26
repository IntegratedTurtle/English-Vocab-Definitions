import Engdef as ed


if __name__ == "__main__":
    csvfile = "/home/julian/Shared/Backup Files/Julian/Programmieren/English-Vocab-Definitions/7th-8th_grade_copy.csv"
    #ed.wordcleaner(csvfile=csvfile)
    ed.defwriter(csvfile=csvfile, makecopy=True)
    #ed.csvcleaner(csvfile=csvfile, makecopy=True)
    