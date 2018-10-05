# Read in IMMA records from files.

import re     #  Regular Expressions
from .structure import attachment
from .structure import parameters
from .structure import definitions
import gzip

# Convert a single-digit base36 value to base 10
def _decode_base36(t): 
    return '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'.find(t)

# Extract the parameter values from the string representation
#  of an attachment
def _decode(as_string,        # String representation of the attachment
            attachment_n):    # Attachment number
    if( as_string== None ):
        raise ValueError("Bad IMMA string: No data to decode")
    params=parameters["%02d" % attachment_n]
    defns=definitions["%02d" % attachment_n]

    Decoded={}
    Position = 0;
    for param in params:
        if ( defns[param][0] != None ):
            Value = as_string[Position:Position+defns[param][0]]
            Position += defns[param][0]
        else:                  # Undefined length - so slurp all the data
            Value = as_string[Position:len(as_string)]
            Value = Value.rstrip("\n")
            Position = len(as_string)

    # Blanks mean value is undefined
        if( re.search("\S",Value) == None ):
            Value = None
            Decoded[param]=Value
            continue    #  Next parameter

        if ( defns[param][6] == 2 ):
            Value = _decode_base36(Value)

        if ( defns[param][6] == 1 ):
            Value = int(Value)

        if ( defns[param][5] != None and
             defns[param][5] != 1.0 ):
            Value = int(Value)*defns[param][5];
        Decoded[param]=Value
    return Decoded

# Make an iterator returning IMMA records from a file
class get:
    """Turn an imma file into an iterator providing its records.

    Args:
        filename (:obj:`str`): Name of file containing IMMA records.

    Returns:
        :obj:`func`: iterator - call ``next()`` on this to get the next record.

    """

    def __init__(self, filename):
        if filename.endswith('.gz'):
            self.fh=gzip.open(filename)
        else:
            self.fh=open(filename,'r')

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()
    
    def next(self): # Python 3: def __next__(self)
        line = self.fh.readline();
        if(line == ""): raise StopIteration
        line=line.rstrip("\n")       # Remove trailing newline
        Attachment_n = 0;            # Core always first
        Length     = 108;
        record={}
        record['attachments']=[]
        while ( len(line) > 0 ):
            if ( Length != None and Length > 0 and len(line) < Length ):
                sfmt = "%%%ds" % (Length-len(line))
                line += sfmt % " "

            record.update(_decode(line,Attachment_n))
            record['attachments'].append(int(Attachment_n))
            if ( Length==None or Length == 0 ):
                break
            line = line[Length:len(line)]
            if ( len(line) > 0 ):
                Attachment_n = int(line[0:2])
                Length       = line[2:4]
                line = line[4:len(line)]
                if Attachment_n==8: Length='102' # Ugly!
                if( re.search("\S",Length)==None): 
                    Length = None
                if ( Length != None ):
                    Length = int(Length)
                    if ( Length != 0 ):
                        Length = int(Length)-4
                if(attachment["%02d" % Attachment_n]==None ):
                    raise ValueError("Bad IMMA string","Unsupported attachment ID %d" % Attachment_n)

        return record

# Function to read in all the records in a file
def read(filename):
    """Load all the records from an imma file.

    Just the same as ``list(IMMA.get(filename)``.

    Args:
        filename (:obj:`str`): Name of file containing IMMA records.

    Returns:
        :obj:`list`: List of records - each record is a :obj:`dict`:

    """

    return list(get(filename))
