# Read in IMMA records from files.

from .structure import attachment
from .structure import parameters
from .structure import definitions
import gzip
import sys

py3 = sys.version[0] == '3'

# Convert a single-digit base36 value to base 10
def _decode_base36(t): 
    return '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'.find(t)

# Extract the parameter values from the string representation
#  of an attachment
def _decode(as_string,        # String representation of the attachment
            attachment_n,
            whitelist = None):    # Attachment number
    
    if( as_string== None ):
        raise ValueError("Bad IMMA string: No data to decode")
    params=parameters[attachment_n]
    defns=definitions[attachment_n]

    Decoded={}
    Position = 0;
    for param in params:
        defn = defns[param]
        if whitelist is not None and param not in whitelist:
            Position += defn[0]            
            continue
        if ( defn[0] != None ):
            Value = as_string[Position:Position+defn[0]]
            Position += defn[0]
        else:                  # Undefined length - so slurp all the data
            Value = as_string[Position:len(as_string)]
            Value = Value.rstrip("\n")
            Position = len(as_string)

        # Blanks mean value is undefined
        if Value.isspace():
            Value = None
            Decoded[param] = Value
            continue
        
        if ( defn[6] == 2 ):
            Value = _decode_base36(Value)
        elif ( defn[6] == 1 ):
            Value = int(Value)

        if ( defn[5] != None and defn[5] != 1.0 ):
            Value = int(Value)*defn[5]
        Decoded[param]=Value
    return Decoded

# Make an iterator returning IMMA records from a file
class get:
    """Turn an imma file into an iterator providing its records.

    Args:
        filename (:obj:`str`): Name of file containing IMMA records.
        keys (:obj:`list`): List of keys to return for each parsed record.
                            If None (the default) the full record is returned.
    
    Returns:
        :obj:`func`: iterator - call ``next()`` on this to get the next record.

    """

    def __init__(self, filename, keys = None):
        if filename.endswith('.gz'):
            self.fh=gzip.open(filename, 'r')
        else:
            self.fh=open(filename,'r')
        if keys is not None:
            self.keys = set(keys)
        else:
            self.keys = None
            
    def __iter__(self):
        for line in self.fh:
            yield self.parse(line)

    def __next__(self):
        return self.next()
    
    def next(self): # Python 3: def __next__(self)
        line = self.fh.readline();
        return self.parse(line)
    
    def parse(self, line):
        if(line == ""): raise StopIteration
        if py3 and isinstance(line, bytes):
            # Convert from bytes
            try:
                line = line.decode("utf-8")
            except UnicodeDecodeError:
                line = line.decode("latin-1")

        line=line.rstrip("\n")       # Remove trailing newline

    
        Attachment_n = 0;            # Core always first
        Length     = 108;
        record={}
        record['attachments']=[]
        while ( len(line) > 0 ):
            if ( Length != None and Length > 0 and len(line) < Length ):
                sfmt = "%%%ds" % (Length-len(line))
                line += sfmt % " "

            record.update(_decode(line,Attachment_n, self.keys))
            record['attachments'].append(int(Attachment_n))
            if ( Length==None or Length == 0 ):
                break
            line = line[Length:len(line)]
            if ( len(line) > 0 ):
                Attachment_n = int(line[0:2])
                Length       = line[2:4]
                line = line[4:len(line)]
                if Attachment_n==8: Length='102' # Ugly!
                if Length.isspace():
                    Length = None
                if ( Length != None ):
                    Length = int(Length)
                    if ( Length != 0 ):
                        Length = int(Length)-4
                if(attachment["%02d" % Attachment_n]==None ):
                    raise ValueError("Bad IMMA string","Unsupported attachment ID %d" % Attachment_n)

        return record

# Function to read in all the records in a file
def read(filename, keys = None):
    """Load all the records from an imma file.

    Just the same as ``list(IMMA.get(filename)``.

    Args:
        filename (:obj:`str`): Name of file containing IMMA records.
        keys (:obj:`list`): List of keys to return for each parsed record.
                            If None (the default) the full record is returned.

    Returns:
        :obj:`list`: List of records - each record is a :obj:`dict`:

    """

    return list(get(filename, keys = keys))
