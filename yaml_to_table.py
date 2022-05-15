import sys
from pathlib import Path
import oyaml as yaml
from prettytable import PrettyTable
import argparse

# Constants
SPACE_CHAR = '~'
CSS_TEXT = """
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
          <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
          <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
          <style>
        body
        {
            padding-left: 20px;
        }
        th:nth-child(1) {
          width: 200px;
          }
        
        /* the second */
        th:nth-child(2) {
          width: 200px;
        }
        
        /* the third */
        th:nth-child(3) {
          width: 100px;
         }
         /* the third */
         th:nth-child(4) {
          width: 420px;
         }
         
         pre {
            white-space: -moz-pre-wrap; /* Mozilla, supported since 1999 */
            white-space: -pre-wrap; /* Opera */
            white-space: -o-pre-wrap; /* Opera */
            white-space: pre-wrap; /* CSS3 - Text module (Candidate Recommendation) http://www.w3.org/TR/css3-text/#white-space */
            word-wrap: break-word; /* IE 5.5+ */
            width: 725px
         }
          </style>
        </head>
        """


def listToString(inList):
    """ Convert list to String """
    ret = ""
    for line in inList:
        ret = ret + line
    return ret


def printDic(inDictionary, inPTable, indent):
    """
        Iterate over Dictionary
           If needed call same function again (recursively) until we key : value dictionary
           Add key , value , isItRequired , description to pretty table object (inPTable)
    """
    global SPACE_CHAR  # No space character that will be replaced when we print this table to text/html

    # Go ver dictionary
    for item in inDictionary:
        if isinstance(item, dict):  # If it again dictionary call same function with this new dictionary
            inPTable.add_row([SPACE_CHAR, SPACE_CHAR])
            printDic(item, inPTable, indent)
        else:
            # Two way to get next item based on input type
            if isinstance(inDictionary, dict):
                moreStuff = inDictionary.get(item)
            elif isinstance(inDictionary, list):
                # If it simple array/list we just print all it's value and we are done
                for _item in inDictionary:
                    inPTable.add_row([indent + _item, SPACE_CHAR+SPACE_CHAR])
                break

            # if it is dictionary or list process them accordingly
            if isinstance(moreStuff, dict):
                inPTable.add_row([indent + item, SPACE_CHAR+SPACE_CHAR])
                printDic(moreStuff, inPTable, SPACE_CHAR + SPACE_CHAR + indent)
            elif isinstance(moreStuff, list):

                # If we are not in nested call (as indent is empty string) we add one extra row in table (for clarity)
                if indent == "":
                    inPTable.add_row([SPACE_CHAR, SPACE_CHAR])
                #
                inPTable.add_row([indent + item, ""])
                for dicInDic in moreStuff:
                    if dicInDic is not None:
                        if isinstance(dicInDic, dict):
                            printDic(dicInDic, inPTable, SPACE_CHAR + SPACE_CHAR + SPACE_CHAR + SPACE_CHAR + indent)
            else:
                inPTable.add_row([indent + item, inDictionary[item]])


def generate_table(yaml_file_object):
    i = 0
    for key in yaml_file_object:
        body_st = []
        prettyTable = PrettyTable()

        prettyTable.field_names = ["Field", "Value"]

        if not PRINT_HTML:
            prettyTable.align["Field"] = "l"
            prettyTable.align["Value"] = "l"

        if isinstance(yaml_file_object, list):
            dic = yaml_file_object[i]
            i += 1
        elif isinstance(yaml_file_object, dict):
            dic = yaml_file_object.get(key)

        if isinstance(dic, dict) or isinstance(dic, list):
            printDic(dic, prettyTable, "")
            if isinstance(yaml_file_object, dict):
                yaml_snippet = yaml.dump({key: dic})
            else:
                yaml_snippet = yaml.dump(dic)

        else:
            prettyTable.add_row([key, dic])
            yaml_snippet = yaml.dump({key: dic})

        if isinstance(yaml_file_object, dict):
            if PRINT_HTML:
                body_st.append("<h2>" + key + "</h2>")
            else:
                print("=> "+key + ":")

        table = prettyTable.get_html_string(attributes={"name": key,
                                                        "id": key,
                                                        "class": "table table-striped table-condensed",
                                                        "style": "width: 1450px;table-layout: fixed;overflow-wrap: "
                                                                 "break-word;"})
        table = table.replace(SPACE_CHAR, "&nbsp;")
        body_st.append(table)
        body_st.append("Raw yaml:")
        body_st.append("<pre>" + yaml_snippet + "</pre>")

        if PRINT_HTML:
            html_st.append(" ".join(body_st))
        else:
            print(str(prettyTable).replace(SPACE_CHAR, " "))
            print("Raw yaml:")
            print("\t" + yaml_snippet.replace("\n", "\n\t"))

    if PRINT_HTML:
        html_st.append("</html>")
        f.write(" ".join(html_st))
        f.close()
        print("File " + OUTPUT_HTML + " has been generated")


"""
    Read given yaml file
"""
def read_input_file():
    with open(INPUT_YAML) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        yaml_file_object = yaml.load(file, Loader=yaml.FullLoader)

        if PRINT_HTML:
            html_st = []
            f = open(OUTPUT_HTML, "w")
            html_st.append(CSS_TEXT)


def main():
    parser = argparse.ArgumentParser(description='YAML file to (HTML) table converter',
                    epilog='text table will be printed as STDOUT - html table will be save in html file ')
    parser.add_argument('--inputFile', dest='inputfile', help="input yaml file to process")
    parser.add_argument('--inputDirectory', dest='inputdir', help="directory of input yaml files to process")
    parser.add_argument('--outputFormat', dest='outformat', choices=['txt', 'html', 'text'], help="convert yaml to text table or html "
                                                                                      "table")
    parser.add_argument('--outputDirectory', dest='outdir', help="directory to output files to")
    args = parser.parse_args()

    # determine output format
    if args.outformat in ['text', 'txt']:
        PRINT_HTML = False
    else:
        PRINT_HTML = True

    # setup input
    if args.inputfile is not None and args.inputdir is None:
        if Path(args.inputfile).is_file():
            INPUT_YAML = args.inputfile
        else:
            sys.exit("Input file [" + args.inputfile + "] does not exists")
    elif args.inputfile is None and args.inputdir is not None:
        if Path(args.inputdir).is_dir():
            # TODO make "main" function call for each file in inputdir
            print("TODO: make main function call for each file in input dir")
        else:
            sys.exit("Input directory [" + args.inputdir + "] does not exists")
    else:
        sys.exit("Invalid option selected for input. Must specify '--inputFile' OR '--inputDirectory' but not both")


    # setup output
    # TODO make it work with input directory
    OUTPUT_HTML = INPUT_YAML.replace("yaml", "doc.html")
    
    read_input_file()
    generate_table()


if __name__ == "__main__":
    main()
