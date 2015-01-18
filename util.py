from logging import debug, info, warning, error, critical
import traceback

# from stackoverflow:: http://stackoverflow.com/questions/251464/how-to-get-the-function-name-as-string-in-python

def who_am_i(depth):
   stack = traceback.extract_stack()
   filename, codeline, funcName, text = stack[-depth]
   return filename, codeline, funcName

def dbgfname():
    fn, cl, func = who_am_i(3)
    debug("In "+fn+":"+str(cl)+" "+func)
