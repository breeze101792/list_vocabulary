from third_party.ecdict.stardict import *

if __name__ == '__main__':
    if len(sys.argv) == 3:
        print("ecdict init: convert " + sys.argv[1] + " to " +  sys.argv[2] + '\n')
        # convert_dict("dict.db", "stardict.csv")
        convert_dict(sys.argv[1], sys.argv[2])
    else:
        print("Usage: ./ecdict.py filename.dict startdict.csv\n")

