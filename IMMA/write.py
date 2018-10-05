# Read in IMMA records from files.

#import re     #  Regular Expressions
from .structure import attachment
from .structure import parameters
from .structure import definitions
import gzip

import sys

py3 = sys.version[0] == '3'

# Write out a record to a file
def write(record,fh):           # fh is a filehandle
    """Write the given record to a file.

    File should be result of  :func:`open` (or anything with a ``write`` method).

    Args:
        record (:obj:`dict`): One IMMA record.
        fh (:obj:`file`): File to write to (from :func:`open` function).

    """

    Result = ""
    
    for attachment_n in record['attachments']:
        Result += _encode(record,attachment_n)
    
    Result += "\n"
    
    if py3:
        Result = bytes(Result, 'utf-8')
        
    fh.write( Result )
        
# Make a string representation of an attachment
def _encode (attachment,
             attachment_n):    # Attachment number
    params=parameters["%02d" % attachment_n]
    defns=definitions["%02d" % attachment_n]
    Result = ""
    for param in params:
        if ( attachment[param] != None):
            Tmp = attachment[param]

            # Scale to integer units for output
            if ( defns[param][5] != None ):
                Tmp = float(Tmp)/defns[param][5];
                Tmp = int(round(Tmp))  # nint

            # Encode as base36 if required
            if ( defns[param][6] == 2 ):
                Tmp = _encode_base36(Tmp);

            # Print as an string of the correct length
            if ( defns[param][6] == 1 ):  # Integer

                if ( defns[param][0] != None ):
                    Lstring = "%%%dd" % (defns[param][0])
                    Tmp = Lstring % (Tmp)
                else:
                    # Undefined length - don't try to constrain it
                    Tmp = "%d" % (Tmp)

            else:                                      # String

                if ( defns[param][0] != None ):
                    Lstring = "%%-%ds" % (defns[param][0])
                    Tmp = Lstring % (Tmp)
                else:
                    Tmp = "%-s" % (Tmp)

            Result += Tmp

        else:  # Undefined data - make a blank string of the corect length

            if ( defns[param][0] != None ):
                Lstring = "%%%ds" % (defns[param][0])
                Result += Lstring % (" ")

            else: # Undefined data with unknown length - should never happen
                Result += " ";

# Done all the parameters, add the ID and length to the start
# (except for core)
    if ( attachment_n != 0 ):
        if ( attachment_n == 99 ):
            Result = "%2d 0%s" % (attachment_n, Result)
        elif attachment_n == 8:
            Result = "%2d2U%s" % (attachment_n, Result)
        else:
            Result = "%2d%2d%s" % (attachment_n, len(Result) + 4, Result)

    return Result

# Convert a base 10 value in the range 0-35 to base36
def _encode_base36(t):
    return '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[t:t+1]
