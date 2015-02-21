from __future__ import absolute_import

from logging import debug, info, warning, error, critical
import traceback
import sys

# from stackoverflow:: http://stackoverflow.com/questions/251464/how-to-get-the-function-name-as-string-in-python

def who_am_i(depth):
   stack = traceback.extract_stack()
   filename, codeline, funcName, text = stack[-depth]
   return filename, codeline, funcName

def dbgfname():
    fn, cl, func = who_am_i(3)
    debug("In "+fn+":"+str(cl)+" "+func)

NOT_SET = False
SET = True
HAS_OPTION = True
NO_OPTION = False

def parse_args(args):
    skip = False
    for i, arg in enumerate(sys.argv):
        if skip:
            skip = False
            continue
        if arg in args:
            if args[arg]["has_option"] == HAS_OPTION:
                try:
                    args[arg]["option"] = sys.argv[i+1]
                except:
                    print "expected option for argument", arg, ", but it doesnt exist"
                    print usage
                    exit()
                else:
                    args[arg]["is_set"] = SET
                    skip = True
            else:
                args[arg]["is_set"] = SET
