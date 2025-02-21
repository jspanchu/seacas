import sys
from ctypes import *
import os

"""
exodus.py v 1.16 (seacas-beta) is a python wrapper of some of the exodus library
(Python 2 Version)

Copyright(C) 1999-2020, 2022 National Technology & Engineering Solutions
of Sandia, LLC (NTESS).  Under the terms of Contract DE-NA0003525 with
NTESS, the U.S. Government retains certain rights in this software.

See packages/seacas/LICENSE for details
"""

EXODUS_PY_COPYRIGHT_AND_LICENSE = __doc__

EXODUS_PY_VERSION = "1.16 (seacas-py2)"

EXODUS_PY_COPYRIGHT = """
You are using exodus.py v 1.16 (seacas-py2), a python wrapper of some of the exodus library.

Copyright (c) 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020 National Technology &
Engineering Solutions of Sandia, LLC (NTESS).  Under the terms of
Contract DE-NA0003525 with NTESS, the U.S. Government retains certain
rights in this software.
"""

EXODUS_PY_CONTACTS = """
Authors:
  Timothy Shelton  (trshelt@sandia.gov)
  Michael Veilleux (mgveill@sandia.gov)
  David Littlewood (djlittl@sandia.gov)
  Greg Sjaardema   (gdsjaar@sandia.gov)
"""

sys.dont_write_bytecode = True

ONELINE = "Gather from or export to Exodus files using the Exodus library"

if sys.version_info[0] >= 3:
    raise Exception("Python-2 version. If using python-3, try `import exodus3 as exodus`")


def basename(file_name):
    """
    Extract base name from file_name.
    basename("test.e") -> "test"
    """
    fileParts = file_name.split(".")
    base_name = ".".join(fileParts[:-1])
    return base_name


def getExodusVersion():
    """
    Parse the exodusII.h header file and return the version number or 0 if not
    found.
    """
    version_major = 0
    version_minor = 0
    ACCESS = os.getenv('ACCESS', '@ACCESSDIR@')
    for line in open(ACCESS + "/@SEACAS_INCLUDEDIR@/exodusII.h"):
        fields = line.split()
        if (len(fields) == 3 and
                fields[0] == '#define' and
                fields[1] == 'EXODUS_VERSION_MAJOR'):
            version_major = int(fields[2])
        if (len(fields) == 3 and
                fields[0] == '#define' and
                fields[1] == 'EXODUS_VERSION_MINOR'):
            version_minor = int(fields[2])
        if (version_major > 0 and version_minor > 0):
           return 100 * version_major + version_minor
    return 0

ACCESS = os.getenv('ACCESS', '@ACCESSDIR@')
if os.uname()[0] == 'Darwin':
    EXODUS_SO = ACCESS + "/@SEACAS_LIBDIR@/libexodus.dylib"
else:
    EXODUS_SO = ACCESS + "/@SEACAS_LIBDIR@/libexodus.so"
EXODUS_LIB = cdll.LoadLibrary(EXODUS_SO)

MAX_STR_LENGTH = 32      # match exodus default
MAX_NAME_LENGTH = 256     # match exodus default
MAX_LINE_LENGTH = 80      # match exodus default

EX_API_VERSION_NODOT = getExodusVersion()
EX_VERBOSE = 1  # verbose mode message flag
if EX_API_VERSION_NODOT >= 608:
    EX_READ = 0x0002  # ex_open(): open file for reading (default)
else:
    EX_READ = 0x0000  # ex_open(): open file for reading (default)
EX_WRITE = 0x0001  # ex_open(): open existing file for appending.
EX_NOCLOBBER = 0x0004  # does not overwrite existing exodus file
EX_CLOBBER = 0x0008  # overwrites existing exodus file

EX_NORMAL_MODEL = 0x0010  # disable mods that permit storage of larger models
EX_64BIT_OFFSET = 0x0020  # enable mods that permit storage of larger models
# enable mods that permit storage of larger models
EX_LARGE_MODEL = EX_64BIT_OFFSET
EX_64BIT_DATA = 0x400000  # CDF-5 format: classic model but 64 bit dimensions and sizes
EX_NETCDF4 = 0x0040  # use the hdf5-based netcdf4 output
EX_NOSHARE = 0x0080  # Do not open netcdf file in "share" mode
EX_SHARE = 0x0100  # Do open netcdf file in "share" mode
EX_NOCLASSIC = 0x0200  # Do not force netcdf to classic mode in netcdf4 mode

EX_DISKLESS = 0x100000  # Experimental
EX_MMAP = 0x200000  # Experimental

# Need to distinguish between storage on database (DB in name) and
# passed through the API functions (API in name).
EX_MAPS_INT64_DB = 0x0400  # All maps (id, order, ...) store int64_t values
# All entity ids (sets, blocks, maps) are int64_t values
EX_IDS_INT64_DB = 0x0800
# All integer bulk data (local indices, counts, maps); not ids
EX_BULK_INT64_DB = 0x1000
# All of the above...
EX_ALL_INT64_DB = EX_MAPS_INT64_DB + EX_IDS_INT64_DB + EX_BULK_INT64_DB

EX_MAPS_INT64_API = 0x2000  # All maps (id, order, ...) store int64_t values
# All entity ids (sets, blocks, maps) are int64_t values
EX_IDS_INT64_API = 0x4000
# All integer bulk data (local indices, counts, maps); not ids
EX_BULK_INT64_API = 0x8000
EX_INQ_INT64_API = 0x10000  # Integers passed to/from ex_inquire are int64_t
# All of the above...
EX_ALL_INT64_API = EX_MAPS_INT64_API + EX_IDS_INT64_API + \
    EX_BULK_INT64_API + EX_INQ_INT64_API

# Parallel IO mode flags...
EX_MPIIO = 0x20000
EX_MPIPOSIX = 0x40000  # \deprecated As of libhdf5 1.8.13.
EX_PNETCDF = 0x80000

# set exodus error output option
exErrPrintMode = c_int(EX_VERBOSE)
EXODUS_LIB.ex_opts(exErrPrintMode)


def ex_inquiry(inquiry):
    # create dictionary for return types
    inquiry_dictionary = {
        'EX_INQ_FILE_TYPE': 1,                    # inquire EXODUS file type
        'EX_INQ_API_VERS': 2,                     # inquire API version number
        'EX_INQ_DB_VERS': 3,                      # inquire database version number
        'EX_INQ_TITLE': 4,                        # inquire database title
        'EX_INQ_DIM': 5,                          # inquire number of dimensions
        'EX_INQ_NODES': 6,                        # inquire number of nodes
        'EX_INQ_ELEM': 7,                         # inquire number of elements
        'EX_INQ_ELEM_BLK': 8,                     # inquire number of element blocks
        'EX_INQ_NODE_SETS': 9,                    # inquire number of node sets
        'EX_INQ_NS_NODE_LEN': 10,                 # inquire length of node set node list
        'EX_INQ_SIDE_SETS': 11,                   # inquire number of side sets
        'EX_INQ_SS_NODE_LEN': 12,                 # inquire length of side set node list
        'EX_INQ_SS_ELEM_LEN': 13,                 # inquire length of side set element list
        'EX_INQ_QA': 14,                          # inquire number of QA records
        'EX_INQ_INFO': 15,                        # inquire number of info records
        # inquire number of time steps in the database
        'EX_INQ_TIME': 16,
        # inquire number of element block properties
        'EX_INQ_EB_PROP': 17,
        'EX_INQ_NS_PROP': 18,                     # inquire number of node set properties
        'EX_INQ_SS_PROP': 19,                     # inquire number of side set properties
        # inquire length of node set distribution factor list
        'EX_INQ_NS_DF_LEN': 20,
        # inquire length of side set distribution factor list
        'EX_INQ_SS_DF_LEN': 21,
        'EX_INQ_LIB_VERS': 22,                    # inquire API Lib vers number
        'EX_INQ_EM_PROP': 23,                     # inquire number of element map properties
        'EX_INQ_NM_PROP': 24,                     # inquire number of node map properties
        'EX_INQ_ELEM_MAP': 25,                    # inquire number of element maps
        'EX_INQ_NODE_MAP': 26,                    # inquire number of node maps
        'EX_INQ_EDGE': 27,                        # inquire number of edges
        'EX_INQ_EDGE_BLK': 28,                    # inquire number of edge blocks
        'EX_INQ_EDGE_SETS': 29,                   # inquire number of edge sets
        # inquire length of concat edge set edge list
        'EX_INQ_ES_LEN': 30,
        # inquire length of concat edge set dist factor list
        'EX_INQ_ES_DF_LEN': 31,
        # inquire number of properties stored per edge block
        'EX_INQ_EDGE_PROP': 32,
        # inquire number of properties stored per edge set
        'EX_INQ_ES_PROP': 33,
        'EX_INQ_FACE': 34,                        # inquire number of faces
        'EX_INQ_FACE_BLK': 35,                    # inquire number of face blocks
        'EX_INQ_FACE_SETS': 36,                   # inquire number of face sets
        # inquire length of concat face set face list
        'EX_INQ_FS_LEN': 37,
        # inquire length of concat face set dist factor list
        'EX_INQ_FS_DF_LEN': 38,
        # inquire number of properties stored per face block
        'EX_INQ_FACE_PROP': 39,
        # inquire number of properties stored per face set
        'EX_INQ_FS_PROP': 40,
        'EX_INQ_ELEM_SETS': 41,                   # inquire number of element sets
        # inquire length of concat element set element list
        'EX_INQ_ELS_LEN': 42,
        # inquire length of concat element set dist factor list
        'EX_INQ_ELS_DF_LEN': 43,
        # inquire number of properties stored per elem set
        'EX_INQ_ELS_PROP': 44,
        'EX_INQ_EDGE_MAP': 45,                    # inquire number of edge maps
        'EX_INQ_FACE_MAP': 46,                    # inquire number of face maps
        'EX_INQ_COORD_FRAMES': 47,                # inquire number of coordinate frames
        # inquire size of MAX_NAME_LENGTH dimension on database
        'EX_INQ_DB_MAX_ALLOWED_NAME_LENGTH': 48,
        # inquire size of MAX_NAME_LENGTH dimension on database
        'EX_INQ_DB_MAX_USED_NAME_LENGTH': 49,
        # inquire client-specified max size of returned names
        'EX_INQ_MAX_READ_NAME_LENGTH': 50,
        # inquire size of floating-point values stored on database
        'EX_INQ_DB_FLOAT_SIZE': 51
    }
    # search dictionary for the requested code
    if inquiry in inquiry_dictionary:
        return inquiry_dictionary[inquiry]
    # none found, must be invalid
    return -1  # EX_INQ_INVALID


def ex_entity_type(varType):
    entity_dictionary = {
        'EX_ELEM_BLOCK': 1,  # element block property code
        'EX_NODE_SET': 2,  # node set property code
        'EX_SIDE_SET': 3,  # side set property code
        'EX_ELEM_MAP': 4,  # element map property code
        'EX_NODE_MAP': 5,  # node map property code
        'EX_EDGE_BLOCK': 6,  # edge block property code
        'EX_EDGE_SET': 7,  # edge set property code
        'EX_FACE_BLOCK': 8,  # face block property code
        'EX_FACE_SET': 9,  # face set property code
        'EX_ELEM_SET': 10,  # face set property code
        'EX_EDGE_MAP': 11,  # edge map property code
        'EX_FACE_MAP': 12,  # face map property code
        'EX_GLOBAL': 13,  # global 'block' for variables
        'EX_NODAL': 14,  # nodal 'block' for variables
        'EX_NODE_BLOCK': 14,  # alias for EX_NODAL
        'EX_COORDINATE': 15,  # kluge so some internal wrapper functions work
    }
    # search dictionary for the requested code
    if varType in entity_dictionary:
        return entity_dictionary[varType]
    # none found, must be invalid
    return -1  # EX_INVALID


# init params struct
class ex_init_params(Structure):
    """
    Parameters defining the model dimension, note that many are optional.

    <int>     num_dim        number of model dimensions
    <int>     num_nodes      number of model nodes
    <int>     num_edge       number of model edges
    <int>     num_edge_blk   number of model edge blocks
    <int>     num_face       number of model faces
    <int>     num_face_blk   number of model face blocks
    <int>     num_elem       number of model elements
    <int>     num_elem_blk   number of model element blocks
    <int>     num_node_sets  number of model node sets
    <int>     num_edge_sets  number of model edge sets
    <int>     num_face_sets  number of model face sets
    <int>     num_side_sets  number of model side sets
    <int>     num_elem_sets  number of model elem sets
    <int>     num_node_maps  number of model node maps
    <int>     num_edge_maps  number of model edge maps
    <int>     num_face_maps  number of model face maps
    <int>     num_elem_maps  number of model elem maps
    """
    _fields_ = [("title", c_char * (MAX_LINE_LENGTH + 1)),
                ("num_dim", c_longlong),
                ("num_nodes", c_longlong),
                ("num_edge", c_longlong),
                ("num_edge_blk", c_longlong),
                ("num_face", c_longlong),
                ("num_face_blk", c_longlong),
                ("num_elem", c_longlong),
                ("num_elem_blk", c_longlong),
                ("num_node_sets", c_longlong),
                ("num_edge_sets", c_longlong),
                ("num_face_sets", c_longlong),
                ("num_side_sets", c_longlong),
                ("num_elem_sets", c_longlong),
                ("num_node_maps", c_longlong),
                ("num_edge_maps", c_longlong),
                ("num_face_maps", c_longlong),
                ("num_elem_maps", c_longlong)]


#
# ----------------------------------------------------------------------
#

class exodus:
    """
    ex_pars = ex_init_params(num_dim=numDims,num_nodes=numNodes,
                             num_elem=numElems, num_elem_blk=numElemBlocks)

    exo = exodus(file_name, \\
      mode=mode, \\
      title=title, \\
      array_type=array_type, \\
      init_params=init_params)

      -> open exodus database for data insertion/extraction

      input value(s):
        <string>  file_name   name of exodus file to open
        <string>  mode        'r' for read,
          'a' for append,
          'w' for write
        <string>  title       database title
        <string>  array_type  'ctype' for c-type arrays,
          'numpy' for numpy arrays
        <int>     num_dims    number of model dimensions ('w' mode only)
        <int>     num_nodes   number of model nodes ('w' mode only)
        <int>     num_elems   number of model elements ('w' mode only)
        <int>     num_blocks  number of model element blocks ('w' mode only)
        <int>     num_ns      number of model node sets ('w' mode only)
        <int>     num_ss      number of model side sets ('w' mode only)

        <ex_init_params>
                  init_params see ex_init_params for more info.

      return value(s):
        <exodus>  exo  the open exodus database
    """

    #
    # construction of a new exodus object
    #
    # --------------------------------------------------------------------

    def __init__(self, file, mode=None, array_type='ctype', title=None,
                 numDims=None, numNodes=None, numElems=None, numBlocks=None,
                 numNodeSets=None, numSideSets=None,
                 init_params=None, io_size=0):
        print(EXODUS_PY_COPYRIGHT)
        if mode is None:
            mode = 'r'
        if array_type == 'numpy':
            # Import numpy to convert from c-type arrays to numpy arrays
            # (Numpy is imported here rather than at the module level, so that
            # the import only occurs if the user specifies a numpy array type.
            # This way, platforms without numpy installed can still import the
            # exodus.py module and just use ctype arrays.)
            import numpy as np
            self.np = np
            self.use_numpy = True
            # Warnings module is needed to suppress the invalid warning when
            # converting from c-type arrays to numpy arrays
            # http://stackoverflow.com/questions/4964101/pep-3118-warning-when-using-ctypes-array-as-numpy-array
            import warnings
            self.warnings = warnings
        else:
            self.use_numpy = False
        self.EXODUS_LIB = EXODUS_LIB
        self.fileName = str(file)
        self.basename = basename(file)
        self.modeChar = mode
        self.__open(io_size=io_size)
        EXODUS_LIB.ex_set_max_name_length(self.fileId, MAX_NAME_LENGTH)
        if mode.lower() == 'w':
            if init_params is not None:
                self.init_params = init_params
                if title is not None:
                    self.init_params.title = title
                self.put_info_ext(self.init_params)
            else:
                if numNodeSets is None:
                    numNodeSets = 0
                if numSideSets is None:
                    numSideSets = 0
                if numNodes is None:
                    numNodes = 0
                if numElems is None:
                    numElems = 0
                if numBlocks is None:
                    numBlocks = 0

                info = [title, numDims, numNodes, numElems, numBlocks,
                        numNodeSets, numSideSets]
                assert None not in info
                self.__ex_put_info(info)

            self.numTimes = c_int(0)
        else:
            self.__ex_get_info()
            self.numTimes = c_int(
                self.__ex_inquire_int(
                    ex_inquiry("EX_INQ_TIME")))

    #
    # build the info struct
    #
    # --------------------------------------------------------------------

    def put_info_ext(self, p):
        """
          e.put_info_ext(self,info_struct)
          -> put initialization information into exodus file
        """
        if len(p.title)>MAX_LINE_LENGTH:
            print('WARNING: Exodus title "%s" exceeds maximum line length (%i). It will be truncated.' %
                  (p.title,MAX_LINE_LENGTH))
            p.title = p.title[-1*MAX_LINE_LENGTH:]

        self.Title = create_string_buffer(p.title, MAX_LINE_LENGTH + 1)
        self.numDim = c_longlong(p.num_dim)
        self.numNodes = c_longlong(p.num_nodes)
        self.numElem = c_longlong(p.num_elem)
        self.numElemBlk = c_longlong(p.num_elem_blk)
        self.numNodeSets = c_longlong(p.num_node_sets)
        self.numSideSets = c_longlong(p.num_side_sets)

        EXODUS_LIB.ex_put_init_ext(self.fileId, byref(p))
        return True

    #
    # copy to a new database
    #
    # --------------------------------------------------------------------

    def copy(self, fileName, include_transient=False):
        """
        exo_copy = exo.copy(file_name)

          -> copies exodus database to file_name and returns this copy as a
            new exodus object

          input value(s):
            <string>  file_name  name of exodus file to open

          return value(s):
            <exodus>  exo_copy  the copy
        """
        i64Status = EXODUS_LIB.ex_int64_status(self.fileId)
        fileId = EXODUS_LIB.ex_create_int(fileName, EX_NOCLOBBER|i64Status,
                                          byref(self.comp_ws),
                                          byref(self.io_ws),
                                          EX_API_VERSION_NODOT)


        self.__copy_file(fileId, include_transient)
        EXODUS_LIB.ex_close(fileId)

        return exodus(fileName, "a")

    #
    # general info
    #
    # --------------------------------------------------------------------

    def title(self):
        """
        title = exo.title()

          -> get the database title

          return value(s):
            <string>  title
        """
        return self.Title.value

    # --------------------------------------------------------------------

    def version_num(self):
        """
        version = exo.version_num()

          -> get exodus version number used to create the database

          return value(s):
            <string>  version  string representation of version number
        """
        return "%1.2f" % self.version.value

    # --------------------------------------------------------------------

    def put_info(self, Title, numDim, numNodes, numElem, numElemBlk,
                 numNodeSets, numSideSets):
        """
        status = exo.put_info(self, \\
          title, \\
          num_dims, \\
          num_nodes, \\
          num_elems, \\
          num_blocks, \\
          num_ns, \\
          num_ss)

          -> initialize static metadata for the database

          input value(s):
            <string>  title       database title
            <int>     num_dims    number of model dimensions
            <int>     num_nodes   number of model nodes
            <int>     num_elems   number of model elements
            <int>     num_blocks  number of model element blocks
            <int>     num_ns      number of model node sets
            <int>     num_ss      number of model side sets

          return value(s):
            <bool>  status  True = successful execution
        """
        self.__ex_put_info([Title, numDim, numNodes, numElem,
                            numElemBlk, numNodeSets, numSideSets])
        return True

    # --------------------------------------------------------------------

    def get_qa_records(self):
        """
        qa_recs = exo.get_qa_records()

          -> get a list of QA records where each QA record is a length-4
            tuple of strings:
              1) the software name that accessed/modified the database
              2) the software descriptor, e.g. version
              3) additional software data
              4) time stamp

          return value(s):
            <list<tuple[4]<string>>>  qa_recs
        """
        return self.__ex_get_qa()

    # --------------------------------------------------------------------

    def put_qa_records(self, records):
        """
        status = exo.put_qa_records()

          -> store a list of QA records where each QA record is a length-4
            tuple of strings:
              1) the software name that accessed/modified the database
              2) the software descriptor, e.g. version
              3) additional software data
              4) time stamp

          input value(s):
            <list<tuple[4]<string>>>  qa_recs

          return value(s):
            <bool>  status  True = successful execution
        """
        for rec in records:
            assert len(rec) == 4
            for recEntry in rec:
                assert len(str(recEntry)) < MAX_STR_LENGTH
        return self.__ex_put_qa(records)

    # --------------------------------------------------------------------

    def num_info_records(self):
        """
        num_info_recs = exo.num_info_records()

          -> get the number of info records

          return value(s):
            <int>  num_info_recs
        """
        return int(self.__ex_inquire_int(ex_inquiry("EX_INQ_INFO")))

    # --------------------------------------------------------------------
    def get_info_records(self):
        """
        info_recs = exo.get_info_records()

          -> get a list info records where each entry in the list is one
            info record, e.g. a line of an input deck

          return value(s):
            <list<string>>  info_recs
        """
        info_recs = self.__ex_get_info_recs()
        return info_recs

    # --------------------------------------------------------------------

    def put_info_records(self, info):
        """
        status = exo.put_info_records(info)

          -> store a list of info records where each entry in the list is
            one line of info, e.g. a line of an input deck

          input value(s):
            <list<tuple[4]<string>>>  info_recs

          return value(s):
            <bool>  status  True = successful execution
        """
        for rec in info:
            if len(str(rec)) > MAX_LINE_LENGTH:
                print("WARNING: max line length reached for one or more info records;")
                print(
                    "         info stored to exodus file is incomplete for these records")
                break
        return self.__ex_put_info_recs(info)

    # --------------------------------------------------------------------

    def get_sierra_input(self, inpFileName=None):
        """
        inp = exo.get_sierra_input(inpFileName=inp_file_name)

          -> parse sierra input deck from the info records
            if inp_file_name is passed the deck is written to this file;
            otherwise a list of input deck file lines is returned

          input value(s):
            (optional)<string>  inp_file_name

          return value(s):
            list<string>  inp  file lines if inp_file_name not provided;
              otherwise, an empty list
        """
        info_recs = self.__ex_get_info_recs()
        sierra_inp = []
        begin = False
        for rec in info_recs:
            vals = rec.split()
            if not begin:  # have not reached Sierra block
                if len(vals) >= 2 and vals[0].lower(
                ) == 'begin' and vals[1].lower() == "sierra":
                    begin = True
            if begin:  # inside Sierra block
                sierra_inp.append(rec)
                if len(rec) > MAX_LINE_LENGTH:
                    print(
                        "WARNING: max line length reached for one or more input lines;")
                    print("         input data might be incomplete for these lines")
                    break
                if len(vals) >= 2 and vals[0].lower(
                ) == "end" and vals[1].lower() == "sierra":
                    break  # end of Sierra block
        if inpFileName:
            fd = open(inpFileName, "w")
            for fileLine in sierra_inp:
                print >> fd, fileLine
            fd.close()
            return []
        return sierra_inp

    #
    # time steps
    #
    # --------------------------------------------------------------------

    def num_times(self):
        """
        num_times = exo.num_times()

          -> get the number of time steps

          return value(s):
            <int>  num_times
        """
        return self.numTimes.value

    # --------------------------------------------------------------------

    def get_times(self):
        """
        time_vals = exo.get_times()

          -> get the time values

          return value(s):

            if array_type == 'ctype':
              <list<c_double>>  time_vals

            if array_type == 'numpy':
              <np_array<double>>  time_vals
        """
        if self.numTimes.value == 0:
            self.times = []
        else:
            self.__ex_get_all_times()
        if self.use_numpy:
            self.times = ctype_to_numpy(self, self.times)
        return self.times

    # --------------------------------------------------------------------

    def put_time(self, step, value):
        """
        exo.put_time(time_step, time_val)

          -> store a new time

          input value(s):
            <int>    time_step  time step index (1-based)
            <float>  time_val   time value for this step

          return value(s):
            <bool>  status  True = successful execution
        """
        self.__ex_put_time(step, value)
        self.numTimes = c_int(self.__ex_inquire_int(ex_inquiry("EX_INQ_TIME")))
        return True

    #
    # coordinate system
    #
    # --------------------------------------------------------------------

    def num_dimensions(self):
        """
        num_dims = exo.num_dimensions()

          -> get the number of model dimensions

          return value(s):
            <int>  num_dims
        """
        return self.numDim.value

    # --------------------------------------------------------------------

    def get_coord_names(self):
        """
        coord_names = exo.get_coord_names()

          -> get a list of length exo.num_dimensions() that has the name
            of each model coordinate direction, e.g. ['x', 'y', 'z']

          return value(s):
            <list<string>>  coord_names
        """
        names = self.__ex_get_coord_names()
        return names

    # --------------------------------------------------------------------

    def put_coord_names(self, names):
        """
        exo.put_coord_names()

          -> store a list of length exo.num_dimensions() that has the name
            of each model coordinate direction, e.g. ['x', 'y', 'z']

          input value(s):
            <list<string>>  coord_names
        """
        self.__ex_put_coord_names(names)

    #
    # nodes
    #
    # --------------------------------------------------------------------

    def num_nodes(self):
        """
        num_nodes = exo.num_nodes()

          -> get the number of nodes in the model

          return value(s):
            <int>  num_nodes
        """
        return self.numNodes.value

    # --------------------------------------------------------------------

    def get_coords(self):
        """
        x_coords, y_coords, z_coords = exo.get_coords()

          -> get model coordinates of all nodes; for each coordinate
            direction, a length exo.num_nodes() list is returned

          return value(s):

            if array_type == 'ctype':
              <list<c_double>>  x_coords  global x-direction coordinates
              <list<c_double>>  y_coords  global y-direction coordinates
              <list<c_double>>  z_coords  global z-direction coordinates

            if array_type == 'numpy':
              <np_array<double>>  x_coords  global x-direction coordinates
              <np_array<double>>  y_coords  global y-direction coordinates
              <np_array<double>>  z_coords  global z-direction coordinates
        """
        self.__ex_get_coord()
        if self.use_numpy:
            self.coordsX = ctype_to_numpy(self, self.coordsX)
            self.coordsY = ctype_to_numpy(self, self.coordsY)
            self.coordsZ = ctype_to_numpy(self, self.coordsZ)
        return (self.coordsX, self.coordsY, self.coordsZ)

    # --------------------------------------------------------------------

    def get_coord(self, i):
        """
        x_coord, y_coord, z_coord = exo.get_coord(node_index)

          -> get model coordinates of a single node

          input value(s):
            <int>  node_index  the 1-based node index
              (indexing is from 1 to exo.num_nodes())

          return value(s):
            <c_double>  x_coord  global x-direction coordinate
            <c_double>  y_coord  global y-direction coordinate
            <c_double>  z_coord  global z-direction coordinate

          note:
            >>> x_coords, y_coords, z_coords = exo.get_coords()
            >>> x_coord = x_coords[node_index-1]
            >>> y_coord = y_coords[node_index-1]
            >>> z_coord = z_coords[node_index-1]
            ... is equivalent to ...
            >>> x_coord, y_coord, z_coord = exo.get_coords(node_index)
        """
        listX, listY, listZ = self.__ex_get_n_coord(i, 1)
        return (listX[0], listY[0], listZ[0])

    # --------------------------------------------------------------------

    def put_coords(self, xCoords, yCoords, zCoords):
        """
        status = exo.put_coords(x_coords, y_coords, z_coords)

          -> store model coordinates of all nodes; for each coordinate
            direction, a length exo.num_nodes() list is input

          input value(s):
            <list<float>>  x_coords  global x-direction coordinates
            <list<float>>  y_coords  global y-direction coordinates
            <list<float>>  z_coords  global z-direction coordinates

          return value(s):
            <bool>  status  True = successful execution
        """
        self.__ex_put_coord(xCoords, yCoords, zCoords)
        return True

    # --------------------------------------------------------------------

    def get_node_num_map(self):
        """
        node_id_map = exo.get_node_num_map()

          -> **DEPRECATED** use: exo.get_node_id_map()

            get mapping of exodus node index to user- or application-
            defined node id; node_id_map is ordered the same as the nodal
            coordinate arrays returned by exo.get_coords() -- this ordering
            follows the exodus node *INDEX* order, a 1-based system going
            from 1 to exo.num_nodes(); a user or application can optionally
            use a separate node *ID* numbering system, so the node_id_map
            points to the node *ID* for each node *INDEX*

          return value(s):
            <list<c_int>>  node_id_map
        """
        nodeNumMap = self.__ex_get_node_num_map()
        return nodeNumMap

    # --------------------------------------------------------------------

    def get_node_id_map(self):
        """
        node_id_map = exo.get_node_id_map()

          -> get mapping of exodus node index to user- or application-
            defined node id; node_id_map is ordered the same as the nodal
            coordinate arrays returned by exo.get_coords() -- this ordering
            follows the exodus node *INDEX* order, a 1-based system going
            from 1 to exo.num_nodes(); a user or application can optionally
            use a separate node *ID* numbering system, so the node_id_map
            points to the node *ID* for each node *INDEX*

          return value(s):

            if array_type == 'ctype':
              <list<int>>  node_id_map

            if array_type == 'numpy':
              <np_array<int>>  node_id_map
        """
        objType = ex_entity_type("EX_NODE_MAP")
        inqType = ex_inquiry("EX_INQ_NODES")
        nodeIdMap = self.__ex_get_id_map(objType, inqType)
        if self.use_numpy:
            nodeIdMap = self.np.array(nodeIdMap)
        return nodeIdMap

    # --------------------------------------------------------------------

    def put_node_id_map(self, map):
        """
        status = exo.put_node_id_map(node_id_map)

          -> store mapping of exodus node index to user- or application-
            defined node id; node_id_map is ordered the same as the nodal
            coordinate arrays returned by exo.get_coords() -- this ordering
            follows the exodus node *INDEX* order, a 1-based system going
            from 1 to exo.num_nodes(); a user or application can optionally
            use a separate node *ID* numbering system, so the node_id_map
            points to the node *ID* for each node *INDEX*

          input value(s):
            <list<int>>  node_id_map

          return value(s):
            <bool>  status  True = successful execution
        """
        objType = ex_entity_type("EX_NODE_MAP")
        inqType = ex_inquiry("EX_INQ_NODES")
        return self.__ex_put_id_map(objType, inqType, map)

    # --------------------------------------------------------------------

    def get_node_variable_names(self):
        """
        nvar_names = exo.get_node_variable_names()

          -> get the list of nodal variable names in the model

            return value(s):
              <list<string>>  nvar_names
        """
        if self.__ex_get_var_param('n').value == 0:
            return []
        return self.__ex_get_var_names("n")

    # --------------------------------------------------------------------

    def get_node_variable_number(self):
        """
        num_nvars = exo.get_node_variable_number()

          -> get the number of nodal variables in the model

            return value(s):
              <int>  num_nvars
        """
        ndType = ex_entity_type("EX_NODAL")
        num = self.__ex_get_variable_param(ndType)
        return num.value

    # --------------------------------------------------------------------

    def set_node_variable_number(self, number):
        """
        status = exo.set_node_variable_number(num_nvars)

          -> update the number of nodal variables in the model

            input value(s):
              <int>  num_nvars

            return value(s):
              <bool>  status  True = successful execution
        """
        ndType = ex_entity_type("EX_NODAL")
        self.__ex_put_variable_param(ndType, number)
        return True

    # --------------------------------------------------------------------

    def put_node_variable_name(self, name, index):
        """
        status = exo.put_node_variable_name(nvar_name, nvar_index)

          -> add the name and index of a new nodal variable to the model;
            nodal variable indexing goes from 1 to
            exo.get_node_variable_number()

          input value(s):
            <string>  nvar_name   name of new nodal variable
            <int>     nvar_index  1-based index of new nodal variable

          return value(s):
            <bool>  status  True = successful execution

          NOTE:
            this method is often called within the following sequence:
            >>> num_nvars = exo.get_node_variable_number()
            >>> new_nvar_index = num_nvars + 1
            >>> num_nvars += 1
            >>> exo.set_node_variable_number(num_nvars)
            >>> exo.put_node_variable_name("new_nvar_name", new_nvar_index)
        """
        ndType = ex_entity_type("EX_NODAL")
        NDvarNames = self.get_node_variable_names()
        if name in NDvarNames:
            print("WARNING: node variable \"", name, "\" already exists.")
        if index > len(NDvarNames):
            raise Exception("ERROR: variable index out of range.")
        self.__ex_put_variable_name(ndType, index, name)
        return True

    # --------------------------------------------------------------------

    def get_node_variable_values(self, name, step):
        """
        nvar_vals = exo.get_node_variable_values(nvar_name, time_step)

          -> get list of nodal variable values for a nodal variable name
            and time step

          input value(s):
            <string>  nvar_name  name of nodal variable
            <int>     time_step  1-based index of time step

          return value(s):

            if array_type == 'ctype':
              <list<c_double>>  nvar_vals

            if array_type == 'numpy':
              <np_array<double>>  nvar_vals
        """
        names = self.get_node_variable_names()
        var_id = names.index(name) + 1
        ndType = ex_entity_type("EX_NODAL")
        numVals = self.num_nodes()
        values = self.__ex_get_var(step, ndType, var_id, 0, numVals)
        if self.use_numpy:
            values = ctype_to_numpy(self, values)
        return values

    # --------------------------------------------------------------------

    def put_node_variable_values(self, name, step, values):
        """
        status = exo.put_node_variable_values(nvar_name, \\
          time_step, \\
          nvar_vals)

          -> store a list of nodal variable values for a nodal variable
            name and time step

          input value(s):
            <string>       nvar_name  name of nodal variable
            <int>          time_step  1-based index of time step
            <list<float>>  nvar_vals

          return value(s):
            <bool>  status  True = successful execution
        """
        names = self.get_node_variable_names()
        var_id = names.index(name) + 1
        ndType = ex_entity_type("EX_NODAL")
        numVals = self.num_nodes()
        self.__ex_put_var(step, ndType, var_id, 0, numVals, values)
        return True

    #
    # elements
    #
    # --------------------------------------------------------------------

    def num_elems(self):
        """
        num_elems = exo.num_elems()

          -> get the number of elements in the model

          return value(s):
            <int>  num_elems
        """
        return self.numElem.value

    # --------------------------------------------------------------------

    def get_elem_num_map(self):
        """
        elem_id_map = exo.get_elem_num_map()

          -> **DEPRECATED** use: exo.get_elem_id_map()

            get mapping of exodus element index to user- or application-
            defined element id; elem_id_map is ordered by the element
            *INDEX* ordering, a 1-based system going from 1 to
            exo.num_elems(), used by exodus for storage and input/output
            of array data stored on the elements; a user or application
            can optionally use a separate element *ID* numbering system,
            so the elem_id_map points to the element *ID* for each
            element *INDEX*

          return value(s):
            <list<c_int>>  elem_id_map
        """
        elemNumMap = self.__ex_get_elem_num_map()
        return elemNumMap

    # --------------------------------------------------------------------

    def get_elem_id_map(self):
        """
        elem_id_map = exo.get_elem_id_map()

          -> get mapping of exodus element index to user- or application-
            defined element id; elem_id_map is ordered by the element
            *INDEX* ordering, a 1-based system going from 1 to
            exo.num_elems(), used by exodus for storage and input/output
            of array data stored on the elements; a user or application
            can optionally use a separate element *ID* numbering system,
            so the elem_id_map points to the element *ID* for each
            element *INDEX*

          return value(s):

            if array_type == 'ctype':
              <list<int>>  elem_id_map

            if array_type == 'numpy':
              <np_array<int>>  elem_id_map
        """
        objType = ex_entity_type("EX_ELEM_MAP")
        inqType = ex_inquiry("EX_INQ_ELEM")
        elemIdMap = self.__ex_get_id_map(objType, inqType)
        if self.use_numpy:
            elemIdMap = self.np.array(elemIdMap)
        return elemIdMap

    # --------------------------------------------------------------------

    def put_elem_id_map(self, map):
        """
        status = exo.put_elem_id_map(elem_id_map)

          -> store mapping of exodus element index to user- or application-
            defined element id; elem_id_map is ordered by the element
            *INDEX* ordering, a 1-based system going from 1 to
            exo.num_elems(), used by exodus for storage and input/output
            of array data stored on the elements; a user or application
            can optionally use a separate element *ID* numbering system,
            so the elem_id_map points to the element *ID* for each
            element *INDEX*

          input value(s):
            <list<int>>  elem_id_map

          return value(s):
            <bool>  status  True = successful execution
        """
        objType = ex_entity_type("EX_ELEM_MAP")
        inqType = ex_inquiry("EX_INQ_ELEM")
        return self.__ex_put_id_map(objType, inqType, map)

    # --------------------------------------------------------------------

    def get_elem_order_map(self):
        """
        elem_order_map = exo.get_elem_order_map()

          -> get mapping of exodus element index to application-defined
            optimal ordering; elem_order_map is ordered by the element
            index ordering used by exodus for storage and input/output
            of array data stored on the elements; a user or application
            can optionally use a separate element ordering, e.g. for
            optimal solver performance, so the elem_order_map points to
            the index used by the application for each exodus element
            index

          return value(s):

            if array_type == 'ctype':
              <list<int>>  elem_order_map

            if array_type == 'numpy':
              <np_array<int>>  elem_order_map
        """

        elemOrderMap = self.__ex_get_elem_order_map()
        if self.use_numpy:
            elemOrderMap = ctype_to_numpy(self, elemOrderMap)
        return elemOrderMap

    #
    # element blocks
    #
    # --------------------------------------------------------------------

    def num_blks(self):
        """
        num_elem_blks = exo.num_blks()

          -> get the number of element blocks in the model

          return value(s):
            <int>  num_elem_blks
        """
        return self.numElemBlk.value

    # --------------------------------------------------------------------

    def get_elem_blk_ids(self):
        """
        elem_blk_ids = exo.get_elem_blk_ids()

          -> get mapping of exodus element block index to user- or
            application-defined element block id; elem_blk_ids is ordered
            by the element block *INDEX* ordering, a 1-based system going
            from 1 to exo.num_blks(), used by exodus for storage
            and input/output of array data stored on the element blocks; a
            user or application can optionally use a separate element block
            *ID* numbering system, so the elem_blk_ids array points to the
            element block *ID* for each element block *INDEX*

          return value(s):

            if array_type == 'ctype':
              <list<int>>  elem_blk_ids

            if array_type == 'numpy':
              <np_array<int>>  elem_blk_ids
        """
        self.__ex_get_elem_blk_ids()
        elemBlkIds = self.elemBlkIds
        if self.use_numpy:
            elemBlkIds = ctype_to_numpy(self, elemBlkIds)
        return elemBlkIds

    # --------------------------------------------------------------------

    def get_elem_blk_name(self, id):
        """
        elem_blk_name = exo.get_elem_blk_name(elem_blk_id)

          -> get the element block name

          input value(s):
            <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):
            <string>  elem_blk_name
        """
        objType = ex_entity_type("EX_ELEM_BLOCK")
        elemBlkName = self.__ex_get_name(objType, id)
        return elemBlkName

    # --------------------------------------------------------------------

    def put_elem_blk_name(self, id, name):
        """
        exo.put_elem_blk_name(elem_blk_id, elem_blk_name)

          -> store the element block name

          input value(s):
            <int>     elem_blk_id    element block *ID* (not *INDEX*)
            <string>  elem_blk_name
        """
        objType = ex_entity_type("EX_ELEM_BLOCK")
        self.__ex_put_name(objType, id, name)

    # --------------------------------------------------------------------

    def get_elem_blk_names(self):
        """
        elem_blk_names = exo.get_elem_blk_names()

          -> get a list of all element block names ordered by block *INDEX*;
            (see description of get_elem_blk_ids() for explanation of the
            difference between block *ID* and block *INDEX*)

          return value(s):
            <list<string>>  elem_blk_names
        """
        objType = ex_entity_type("EX_ELEM_BLOCK")
        inqType = ex_inquiry("EX_INQ_ELEM_BLK")
        elemBlkNames = self.__ex_get_names(objType, inqType)
        return elemBlkNames

    # --------------------------------------------------------------------

    def put_elem_blk_names(self, names):
        """
        exo.put_elem_blk_names(elem_blk_names)

          -> store a list of all element block names ordered by block *INDEX*;
            (see description of get_elem_blk_ids() for explanation of the
            difference between block *ID* and block *INDEX*)

          input value(s):
            <list<string>>  elem_blk_names
        """
        objType = ex_entity_type("EX_ELEM_BLOCK")
        inqType = ex_inquiry("EX_INQ_ELEM_BLK")
        self.__ex_put_names(objType, inqType, names)

    # --------------------------------------------------------------------

    def elem_blk_info(self, id):
        """
        elem_type, \\
        num_blk_elems, \\
        num_elem_nodes, \\
        num_elem_attrs = exo.elem_blk_info(elem_blk_id)

          -> get the element block info

          input value(s):
            <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):
            <string>  elem_type       element type, e.g. 'HEX8'
            <int>     num_blk_elems   number of elements in the block
            <int>     num_elem_nodes  number of nodes per element
            <int>     num_elem_attrs  number of attributes per element
        """
        (elemType, numElem, nodesPerElem, numAttr) = self.__ex_get_elem_block(id)
        return elemType.value, numElem.value, nodesPerElem.value, numAttr.value

    # --------------------------------------------------------------------

    def put_elem_blk_info(self, elem_blk_id, elem_type, num_blk_elems,
                          num_elem_nodes, num_elem_attrs):
        """
        exo.put_elem_blk_info(elem_blk_id, \\
          elem_type, \\
          num_blk_elems, \\
          num_elem_nodes, \\
          num_elem_attrs)

          -> store the element block *ID* and element block info

          input value(s):
            <int>     elem_blk_id      element block *ID* (not *INDEX*)
            <string>  elem_type        element type (all caps), e.g. 'HEX8'
            <int>     num_blk_elems    number of elements in the block
            <int>     num_elem_nodes   number of nodes per element
            <int>     num_elem_attrs   number of attributes per element
        """
        self.__ex_put_elem_block(elem_blk_id, elem_type, num_blk_elems,
                                 num_elem_nodes, num_elem_attrs)

    # --------------------------------------------------------------------

    def put_concat_elem_blk(self, elem_blk_ids, elem_type, num_blk_elems,
                            num_elem_nodes, num_elem_attrs, defineMaps):
        """
        status = exo.put_concat_elem_blk(elem_blk_ids, \\
          elem_types, \\
          num_blk_elems, \\
          num_elem_nodes, \\
          num_elem_attrs)

          -> same as exo.put_elem_blk_info() but for all blocks at once

          input value(s):
            <list<int>>     elem_blk_ids     element block *ID* (not *INDEX*)
              for each block
            <list<string>>  elem_types       element type for each block
            <list<int>>     num_blk_elems    number of elements for each
              block
            <list<int>>     num_elem_nodes   number of nodes per element
              for each block
            <list<int>>     num_elem_attrs   number of attributes per
              element for each block

          return value(s):
            <bool>  status  True = successful execution
        """
        self.__ex_put_concat_elem_blk(
            elem_blk_ids,
            elem_type,
            num_blk_elems,
            num_elem_nodes,
            num_elem_attrs,
            defineMaps)
        return True

    # --------------------------------------------------------------------

    def get_elem_connectivity(self, id):
        """
        elem_conn, \\
        num_blk_elems, \\
        num_elem_nodes = exo.get_elem_connectivity(elem_blk_id)

          -> get the nodal connectivity, number of elements, and
            number of nodes per element for a single block

          input value(s):
            <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):

            if array_type == 'ctype':
              <list<int>>  elem_conn  ordered list of node *INDICES* that
                define the connectivity of each element
                in the block; the list cycles through
                all nodes of the first element, then
                all nodes of the second element, etc.
                (see get_node_id_map() for explanation
                of node *INDEX* versus node *ID*)

            if array_type == 'numpy':
              <np_array<int>>  elem_conn  (same description)

            <int>  num_blk_elems    number of elements in the block
            <int>  num_elem_nodes   number of nodes per element
        """
        (elem_block_connectivity, num_elem_this_blk,
         num_nodes_per_elem) = self.__ex_get_elem_conn(id)
        if self.use_numpy:
            elem_block_connectivity = ctype_to_numpy(
                self, elem_block_connectivity)
        return (
            elem_block_connectivity,
            num_elem_this_blk.value,
            num_nodes_per_elem.value)

    # --------------------------------------------------------------------

    def put_elem_connectivity(self, id, connectivity):
        """
        exo.put_elem_connectivity(elem_blk_id, elem_conn)

          -> store the nodal connectivity, number of elements, and
            number of nodes per element for a single block

          input value(s):
            <int>        elem_blk_id  element block *ID* (not *INDEX*)
            <list<int>>  elem_conn    ordered list of node *INDICES* that
              define the connectivity of each
              element in the block; the list cycles
              through all nodes of the first element,
              then all nodes of the second element,
              etc.
              (see get_node_id_map() for explanation
              of node *INDEX* versus node *ID*)
        """
        d1, numBlkElems, numNodesPerElem, d2 = self.elem_blk_info(id)
        assert len(connectivity) == (numBlkElems * numNodesPerElem)
        self.__ex_put_elem_conn(id, connectivity)

    # --------------------------------------------------------------------

    def get_elem_attr(self, elem_blk_id):
        """
        elem_attrs = exo.get_elem_attr(elem_blk_id)

          -> get all attributes for each element in a block

          input value(s):
            <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):
            if array_type == 'ctype':
            <list<float>>  elem_attrs  list of attribute values for all
              elements in the block; the list cycles
              through all attributes of the first
              element, then all attributes of the
              second element, etc. Attributes are
              ordered by the ordering of the names
              returned by
              exo.get_element_attribute_names()
            if array_type == 'numpy':
              <np_array<float>>  elem_attrs  array of attribute values for all
                                             elements in the block; the list cycles
                                             through all attributes of the first
                                             element, then all attributes of the
                                             second element, etc. Attributes are
                                             ordered by the ordering of the names
                                             returned by
                                             exo.get_element_attribute_names()
        """
        elem_attrs = self.__ex_get_elem_attr(elem_blk_id)
        if self.use_numpy:
            elem_attrs = ctype_to_numpy(self, elem_attrs)
        return elem_attrs

    # --------------------------------------------------------------------

    def get_elem_attr_values(self, elem_blk_id, elem_attr_name):
        """
        elem_attrs = exo.get_elem_attr(elem_blk_id)

          -> get an attribute for each element in a block

          input value(s):
            <int>    elem_blk_id     element block *ID* (not *INDEX*)
            <string> elem_attr_name  element attribute name

          return value(s):
            if array_type == 'ctype':
              <list<float>>  values      list of values for the requested
                                         attribute.  List has dimensions of
                                         1 x num_elem, where num_elem is the
                                         number of elements on the element block.
            if array_type == 'numpy':
              <np_array<float>>  values  array of values for the requested
                                         attribute.  Array has dimensions of
                                         1 x num_elem, where num_elem is the
                                         number of elements on the element block.
        """
        # The exo.get_elem_attr() method dumps all the element attributes in one
        # monolithic list.  This can be cumbersome for the user, and
        # prompted the following convenience function, which grabs a single set
        # of element attribute values from the proper location in the monolithic
        # list.
        elem_attr_names = self.get_element_attribute_names(elem_blk_id)
        a_ndx = elem_attr_names.index(elem_attr_name)
        num_attr = len(elem_attr_names)
        all_values = self.get_elem_attr(elem_blk_id)
        values = all_values[a_ndx::num_attr]
        if self.use_numpy:
            values = ctype_to_numpy(self, values)
        return values

    # --------------------------------------------------------------------

    def put_elem_attr(self, elem_blk_id, elem_attrs):
        """

        exo.put_elem_attr(elem_blk_id, elem_attrs)

          -> store all attributes for each element in a block

          input value(s):
            <int>          elem_blk_id  element block *ID* (not *INDEX*)
            <list<float>>  elem_attrs     list of all attribute values for all
              elements in the block; the list
              cycles through all attributes of
              the first element, then all attributes
              of the second element, etc. Attributes
              are ordered by the ordering of the
              names returned by
              exo.get_element_attribute_names()
        """
        self.__ex_put_elem_attr(elem_blk_id, elem_attrs)

    # --------------------------------------------------------------------

    def put_elem_attr_values(self, elem_blk_id, elem_attr_name, values):
        """

        exo.put_elem_attr_values(elem_blk_id, elem_attr_name, values)

          -> store an attribute for each element in a block

          input value(s):
            <int>          elem_blk_id    element block *ID* (not *INDEX*)
            <string>       elem_attr_name element attribute name
            <list<float>>  values         list of values for a single attribute
                                          on a element block.  List dimensions
                                          should be 1 x N_elem, where N_elem is
                                          the number of elements on the element
                                          block.
        """
        # The exo.put_elem_attr() method requires the user to specify all the
        # element attributes in one monolithic list, even if the user is only
        # specifying one element attribute.  This is cumbersome for the user, and
        # prompted the following convenience function, which inserts a single set
        # of element attribute values into the proper location in the monolithic
        # list and then puts them onto the database.
        elem_attr_names = self.get_element_attribute_names(elem_blk_id)
        a_ndx = elem_attr_names.index(elem_attr_name)
        num_attr = len(elem_attr_names)
        all_values = self.get_elem_attr(elem_blk_id)
        all_values[a_ndx::num_attr] = values
        self.put_elem_attr(elem_blk_id, all_values)

    # --------------------------------------------------------------------

    def elem_type(self, id):
        """
        elem_type = exo.elem_type(elem_blk_id)

          -> get the element type, e.g. "HEX8", for an element block

          input value(s):
            <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):
            <string>  elem_type
        """
        (elemType, numElem, nodesPerElem, numAttr) = self.__ex_get_elem_block(id)
        return elemType.value

    # --------------------------------------------------------------------

    def num_attr(self, id):
        """
        num_elem_attrs = exo.num_attr(elem_blk_id)

          -> get the number of attributes per element for an element block

          input value(s):
            <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):
            <int>  num_elem_attrs
        """
        (elemType, numElem, nodesPerElem, numAttr) = self.__ex_get_elem_block(id)
        return numAttr.value

    # --------------------------------------------------------------------

    def num_elems_in_blk(self, id):
        """
        num_blk_elems = exo.num_elems_in_blk(elem_blk_id)

          -> get the number of elements in an element block

          input value(s):
            <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):
            <int>  num_blk_elems
        """
        (elemType, numElem, nodesPerElem, numAttr) = self.__ex_get_elem_block(id)
        return numElem.value

    # --------------------------------------------------------------------

    def num_nodes_per_elem(self, id):
        """
        num_elem_nodes = exo.num_nodes_per_elem(elem_blk_id)

          -> get the number of nodes per element for an element block

          input value(s):
            <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):
            <int>  num_elem_nodes
        """
        (elemType, numElem, nodesPerElem, numAttr) = self.__ex_get_elem_block(id)
        return nodesPerElem.value

    # --------------------------------------------------------------------

    def get_element_variable_truth_table(self, blockId=None):
        """
        evar_truth_tab = \\
          exo.get_element_variable_truth_table(blockID=elem_blk_id)

          -> gets a truth table indicating which variables are defined for
            a block; if elem_blk_id is not passed, then a concatenated
            truth table for all blocks is returned with variable index
            cycling faster than block index

          input value(s):
            (optional) <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):
            <list<bool>>  evar_truth_tab  True for variable defined in block,
              False otherwise
        """
        truthTable = self.__ex_get_elem_var_tab()
        if blockId is not None:
            self.get_elem_blk_ids()
            assert blockId in list(self.elemBlkIds)
            indx = list(self.elemBlkIds).index(blockId)
            numVars = self.__ex_get_var_param("e").value
            start, stop = (indx * numVars, (indx + 1) * numVars)
            return truthTable[start:stop]
        return truthTable

    # --------------------------------------------------------------------

    def set_element_variable_truth_table(self, table):
        """
        status = \\
          exo.set_element_variable_truth_table(evar_truth_tab)

          -> stores a truth table indicating which variables are defined for
            all blocks and all element variables; variable index cycles
            faster than block index

          input value(s):
            <list<bool>>  evar_truth_tab  True for variable defined in block,
              False otherwise

          return value(s):
            <bool>  status  True = successful execution
        """
        self.get_elem_blk_ids()
        numBlks = len(self.elemBlkIds)
        numVars = int(self.__ex_get_var_param("e").value)
        assert len(table) == (numBlks * numVars)
        return self.__ex_put_elem_var_tab(table)

    # --------------------------------------------------------------------

    def get_element_variable_values(self, blockId, name, step):
        """
        evar_vals = \\
          exo.get_element_variable_values(elem_blk_id, \\
            evar_name, \\
            time_step)

          -> get list of element variable values for a specified element
            block, element variable name, and time step

          input value(s):
            <int>     elem_blk_id  element block *ID* (not *INDEX*)
            <string>  evar_name    name of element variable
            <int>     time_step    1-based index of time step

          return value(s):

            if array_type == 'ctype':
              <list<c_double>>  evar_vals

            if array_type == 'numpy':
              <np_array<double>>  evar_vals
        """
        names = self.get_element_variable_names()
        var_id = names.index(name) + 1
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        numVals = self.num_elems_in_blk(blockId)
        values = self.__ex_get_var(step, ebType, var_id, blockId, numVals)
        if self.use_numpy:
            values = ctype_to_numpy(self, values)
        return values

    # --------------------------------------------------------------------

    def put_element_variable_values(self, blockId, name, step, values):
        """
        status = \\
          exo.put_element_variable_values(elem_blk_id, \\
            evar_name, \\
            time_step, \\
            evar_vals)

          -> store a list of element variable values for a specified element
            block, element variable name, and time step

          input value(s):
            <int>          elem_blk_id  element block *ID* (not *INDEX*)
            <string>       evar_name    name of element variable
            <int>          time_step    1-based index of time step
            <list<float>>  evar_vals

          return value(s):
            <bool>  status  True = successful execution
        """
        names = self.get_element_variable_names()
        var_id = names.index(name) + 1
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        numVals = self.num_elems_in_blk(blockId)
        self.__ex_put_var(step, ebType, var_id, blockId, numVals, values)
        return True

    # --------------------------------------------------------------------

    def get_element_variable_number(self):
        """
        num_evars = exo.get_element_variable_number()

          -> get the number of element variables in the model

            return value(s):
              <int>  num_evars
        """
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        num = self.__ex_get_variable_param(ebType)
        return num.value

    # --------------------------------------------------------------------

    def set_element_variable_number(self, number):
        """
        status = exo.set_element_variable_number(num_evars)

          -> update the number of element variables in the model

            input value(s):
              <int>  num_evars

            return value(s):
              <bool>  status  True = successful execution
        """
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        self.__ex_put_variable_param(ebType, number)
        return True

    # --------------------------------------------------------------------

    def get_element_variable_names(self):
        """
        evar_names = exo.get_element_variable_names()

          -> get the list of element variable names in the model

            return value(s):
              <list<string>>  evar_names
        """
        if self.__ex_get_var_param("e").value == 0:
            return []
        return self.__ex_get_var_names("e")

    # --------------------------------------------------------------------

    def put_element_variable_name(self, name, index):
        """
        status = exo.put_element_variable_name(evar_name, evar_index)

          -> add the name and index of a new element variable to the model;
            element variable indexing goes from 1 to
            exo.get_element_variable_number()

          input value(s):
            <string>  evar_name   name of new element variable
            <int>     evar_index  1-based index of new element variable

          return value(s):
            <bool>  status  True = successful execution

          NOTE:
            this method is often called within the following sequence:
            >>> num_evars = exo.get_element_variable_number()
            >>> new_evar_index = num_evars + 1
            >>> num_evars += 1
            >>> exo.set_element_variable_number(num_evars)
            >>> exo.put_element_variable_name("new_evar", new_evar_index)
        """
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        EBvarNames = self.get_element_variable_names()
        if name in EBvarNames:
            print("WARNING: element variable \"", name, "\" already exists.")
        if index > len(EBvarNames):
            print("index", index, "len", len(EBvarNames))
            raise Exception("ERROR: variable index out of range.")
        self.__ex_put_variable_name(ebType, index, name)
        return True

    # --------------------------------------------------------------------

    def get_element_attribute_names(self, blkId):
        """
        attr_names = exo.get_element_attribute_names(elem_blk_id)

          -> get the list of element attribute names for a block

          input value(s):
            <int>  elem_blk_id  element block *ID* (not *INDEX*)

          return value(s):
            <list<string>>  attr_names
        """
        names = self.__ex_get_elem_attr_names(blkId)
        return list(names)

    # --------------------------------------------------------------------

    def put_element_attribute_names(self, blkId, names):
        """
        status = exo.put_element_attribute_names(elem_blk_id, attr_names)

          -> store the list of element attribute names for a block

          input value(s):
            <int>           elem_blk_id  element block *ID* (not *INDEX*)
            <list<string>>  attr_names

          return value(s):
            <bool>  status  True = successful execution
        """
        return self.__ex_put_elem_attr_names(blkId, names)

    # --------------------------------------------------------------------

    def get_element_property_names(self):
        """
        eprop_names = exo.get_element_property_names()

          -> get the list of element property names for all element blocks
            in the model

          return value(s):
            <list<string>>  eprop_names
        """
        names = []
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        inqType = "EX_INQ_EB_PROP"
        names = self.__ex_get_prop_names(ebType, inqType)
        return list(names)

    # --------------------------------------------------------------------

    def get_element_property_value(self, id, name):
        """
        eprop_val = exo.get_element_property_value(elem_blk_id, eprop_name)

          -> get element property value (an integer) for a specified element
            block and element property name

          input value(s):
            <int>     elem_blk_id  element block *ID* (not *INDEX*)
            <string>  eprop_name

          return value(s):
            <int>  eprop_val
        """
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        propVal = self.__ex_get_prop(ebType, id, name)
        return int(propVal)

    # --------------------------------------------------------------------

    def put_element_property_value(self, id, name, value):
        """
        status = exo.put_element_property_value(elem_blk_id, \\
          eprop_name, \\
          eprop_val)

          -> store an element property name and its integer value for an
            element block

          input value(s):
            <int>     elem_blk_id  element block *ID* (not *INDEX*)
            <string>  eprop_name
            <int>     eprop_val

          return value(s):
            <bool>  status  True = successful execution
        """
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        return self.__ex_put_prop(ebType, id, name, value)

    #
    # nodesets
    #
    # --------------------------------------------------------------------

    def num_node_sets(self):
        """
        num_node_sets = exo.num_node_sets()

          -> get the number of node sets in the model

          return value(s):
            <int>  num_node_sets
        """
        return self.numNodeSets.value

    # --------------------------------------------------------------------

    def get_node_set_ids(self):
        """
        node_set_ids = exo.get_node_set_ids()

          -> get mapping of exodus node set index to user- or application-
            defined node set id; node_set_ids is ordered
            by the *INDEX* ordering, a 1-based system going from
            1 to exo.num_node_sets(), used by exodus for storage
            and input/output of array data stored on the node sets; a
            user or application can optionally use a separate node set
            *ID* numbering system, so the node_set_ids array points to the
            node set *ID* for each node set *INDEX*

          return value(s):

            if array_type == 'ctype':
              <list<int>>  node_set_ids

            if array_type == 'numpy':
              <np_array<int>>  node_set_ids
        """
        self.__ex_get_node_set_ids()
        nodeSetIds = list(self.nodeSetIds)
        if self.use_numpy:
            nodeSetIds = self.np.array(nodeSetIds)
        return nodeSetIds

    # --------------------------------------------------------------------

    def get_node_set_name(self, id):
        """
        node_set_name = exo.get_node_set_name(node_set_id)

          -> get the name of a node set

          input value(s):
            <int>  node_set_id  node set *ID* (not *INDEX*)

          return value(s):
            <string>  node_set_name
        """
        objType = ex_entity_type("EX_NODE_SET")
        nodeSetName = self.__ex_get_name(objType, id)
        return nodeSetName

    # --------------------------------------------------------------------

    def put_node_set_name(self, id, name):
        """
        exo.put_node_set_name(node_set_id, node_set_name)

          -> store the name of a node set

          input value(s):
            <int>     node_set_id    node set *ID* (not *INDEX*)
            <string>  node_set_name
        """
        objType = ex_entity_type("EX_NODE_SET")
        self.__ex_put_name(objType, id, name)

    # --------------------------------------------------------------------

    def get_node_set_names(self):
        """
        node_set_names = exo.get_node_set_names()

          -> get a list of all node set names ordered by node set *INDEX*;
            (see description of get_node_set_ids() for explanation of the
            difference between node set *ID* and node set *INDEX*)

          return value(s):
            <list<string>>  node_set_names
        """
        objType = ex_entity_type("EX_NODE_SET")
        inqType = ex_inquiry("EX_INQ_NODE_SETS")
        nodeSetNames = self.__ex_get_names(objType, inqType)
        return nodeSetNames

    # --------------------------------------------------------------------

    def put_node_set_names(self, names):
        """
        exo.put_node_set_names(node_set_names)

          -> store a list of all node set names ordered by node set *INDEX*;
            (see description of get_node_set_ids() for explanation of the
            difference between node set *ID* and node set *INDEX*)

          input value(s):
            <list<string>>  node_set_names
        """
        objType = ex_entity_type("EX_NODE_SET")
        inqType = ex_inquiry("EX_INQ_NODE_SETS")
        self.__ex_put_names(objType, inqType, names)

    # --------------------------------------------------------------------

    def num_nodes_in_node_set(self, id):
        """
        num_ns_nodes = exo.num_nodes_in_node_set(node_set_id)

          -> get the number of nodes in a node set

          input value(s):
            <int>  node_set_id  node set *ID* (not *INDEX*)

          return value(s):
            <int>  num_ns_nodes
        """
        node_set_nodes = self.get_node_set_nodes(id)
        return len(node_set_nodes)

    # --------------------------------------------------------------------

    def get_node_set_nodes(self, id):
        """
        ns_nodes = exo.get_node_set_nodes(node_set_id)

          -> get the list of node *INDICES* in a node set
            (see exo.get_node_id_map() for explanation of node *INDEX*
            versus node *ID*)

          input value(s):
            <int>  node_set_id  node set *ID* (not *INDEX*)

          return value(s):

            if array_type == 'ctype':
              <list<int>>  ns_nodes

            if array_type == 'numpy':
              <np_array<int>>  ns_nodes
        """
        node_set_ids = self.get_node_set_ids()
        assert id in node_set_ids
        node_set_nodes = self.__ex_get_node_set(id)
        node_set_nodes = list(node_set_nodes)
        if self.use_numpy:
            node_set_nodes = self.np.array(node_set_nodes)
        return node_set_nodes

    # --------------------------------------------------------------------

    def put_node_set(self, id, nodeSetNodes):
        """
        exo.put_node_set(node_set_id, ns_nodes)

          -> store a node set by its id and the list of node *INDICES* in
            the node set (see exo.get_node_id_map() for explanation of node
            *INDEX* versus node *ID*)

          input value(s):
            <int>        node_set_id  node set *ID* (not *INDEX*)
            <list<int>>  ns_nodes
        """
        self.__ex_put_node_set(id, nodeSetNodes)

    # --------------------------------------------------------------------

    def get_node_set_dist_facts(self, id):
        """
        ns_dist_facts = exo.get_node_set_dist_facts(node_set_id)

          -> get the list of distribution factors for nodes in a node set

          input value(s):
            <int>        node_set_id  node set *ID* (not *INDEX*)

          return value(s):

            if array_type == 'ctype':
              <list<float>>  ns_dist_facts  a list of distribution factors,
                e.g. nodal 'weights'

            if array_type == 'numpy':
              <np_array<double>>  ns_dist_facts  a list of distribution
                factors, e.g. nodal
                'weights'
        """
        node_set_dfs = self.__ex_get_node_set_dist_fact(id)
        node_set_dfs = list(node_set_dfs)
        if self.use_numpy:
            node_set_dfs = self.np.array(node_set_dfs)
        return node_set_dfs

    # --------------------------------------------------------------------

    def put_node_set_dist_fact(self, id, nodeSetDistFact):
        """
        exo.put_node_set_dist_fact(node_set_id, ns_dist_facts)

          -> store the list of distribution factors for nodes in a node set

          input value(s):
            <int>          node_set_id    node set *ID* (not *INDEX*)
            <list<float>>  ns_dist_facts  a list of distribution factors,
              e.g. nodal 'weights'
        """
        self.__ex_put_node_set_dist_fact(id, nodeSetDistFact)

    # --------------------------------------------------------------------

    def get_node_set_variable_number(self):
        """
        num_nsvars = exo.get_node_set_variable_number()

          -> get the number of node set variables in the model

            return value(s):
              <int>  num_nsvars
        """
        nsType = ex_entity_type("EX_NODE_SET")
        num = self.__ex_get_variable_param(nsType)
        return num.value

    # --------------------------------------------------------------------

    def set_node_set_variable_number(self, number):
        """
        status = exo.set_node_set_variable_number(num_nsvars)

          -> update the number of node set variables in the model

            input value(s):
              <int>  num_nsvars

            return value(s):
              <bool>  status  True = successful execution
        """
        nsType = ex_entity_type("EX_NODE_SET")
        self.__ex_put_variable_param(nsType, number)
        return True

    # --------------------------------------------------------------------

    def get_node_set_variable_truth_table(self, nodeSetId=None):
        """
        nsvar_truth_tab = \\
          exo.get_node_set_variable_truth_table(nodeSetID=node_set_id)

          -> gets a truth table indicating which variables are defined for
            a node set; if node_set_id is not passed, then a concatenated
            truth table for all node sets is returned with variable index
            cycling faster than node set index

          input value(s):
            (optional) <int>  node_set_id  node set *ID* (not *INDEX*)

          return value(s):
            <list<bool>>  nsvar_truth_tab  True if variable is defined in
              a node set, False otherwise
        """
        truthTable = self.__ex_get_nset_var_tab()
        if nodeSetId is not None:
            self.get_node_set_ids()
            assert nodeSetId in list(self.nodeSetIds)
            indx = list(self.nodeSetIds).index(nodeSetId)
            numVars = self.__ex_get_var_param("m").value
            start, stop = (indx * numVars, (indx + 1) * numVars)
            return truthTable[start:stop]
        return truthTable

    # --------------------------------------------------------------------

    def set_node_set_variable_truth_table(self, table):
        """
        status = \\
          exo.set_node_set_variable_truth_table(nsvar_truth_tab)

          -> stores a truth table indicating which variables are defined for
            all node sets and all node set variables; variable index cycles
            faster than node set index

          input value(s):
            <list<bool>>  nsvar_truth_tab  True if variable is defined in
              a node set, False otherwise

          return value(s):
            <bool>  status  True = successful execution
        """
        self.get_node_set_ids()
        numBlks = len(self.nodeSetIds)
        numVars = int(self.__ex_get_var_param("m").value)
        assert len(table) == (numBlks * numVars)
        return self.__ex_put_nset_var_tab(table)

    # --------------------------------------------------------------------

    def get_node_set_variable_names(self):
        """
        nsvar_names = exo.get_node_set_variable_names()

          -> get the list of node set variable names in the model

            return value(s):
              <list<string>>  nsvar_names
        """
        names = []
        nsType = ex_entity_type("EX_NODE_SET")
        num_vars = self.__ex_get_variable_param(nsType)
        for varid in range(num_vars.value):
            varid += 1
            name = self.__ex_get_variable_name(nsType, varid)
            names.append(name.value)
        return names

    # --------------------------------------------------------------------

    def put_node_set_variable_name(self, name, index):
        """
        status = exo.put_node_set_variable_name(nsvar_name, nsvar_index)

          -> add the name and index of a new node set variable to the model;
            node set variable indexing goes from 1 to
            exo.get_node_set_variable_number()

          input value(s):
            <string>  nsvar_name   name of new node set variable
            <int>     nsvar_index  1-based index of new node set variable

          return value(s):
            <bool>  status  True = successful execution

          NOTE:
            this method is often called within the following sequence:
            >>> num_nsvars = exo.get_node_set_variable_number()
            >>> new_nsvar_index = num_nsvars + 1
            >>> num_nsvars += 1
            >>> exo.set_node_set_variable_number(num_nsvars)
            >>> exo.put_node_set_variable_name("new_nsvar", new_nsvar_index)
        """
        nsType = ex_entity_type("EX_NODE_SET")
        NSvarNames = self.get_node_set_variable_names()
        if name in NSvarNames:
            print("WARNING: Node set variable \"", name, "\" already exists.")
        if index > len(NSvarNames):
            raise Exception("ERROR: variable index out of range.")
        self.__ex_put_variable_name(nsType, index, name)
        return True

    # --------------------------------------------------------------------

    def get_node_set_variable_values(self, id, name, step):
        """
        nsvar_vals = \\
          exo.get_node_set_variable_values(node_set_id, \\
            nsvar_name, \\
            time_step)

          -> get list of node set variable values for a specified node
            set, node set variable name, and time step; the list has
            one variable value per node in the set

          input value(s):
            <int>     node_set_id  node set *ID* (not *INDEX*)
            <string>  nsvar_name   name of node set variable
            <int>     time_step    1-based index of time step

          return value(s):

            if array_type == 'ctype':
              <list<c_double>>  nsvar_vals

            if array_type == 'numpy':
              <np_array<double>>  nsvar_vals
        """
        names = self.get_node_set_variable_names()
        var_id = names.index(name) + 1
        values = self.__ex_get_nset_var(step, var_id, id)
        if self.use_numpy:
            values = ctype_to_numpy(self, values)
        return values

    # --------------------------------------------------------------------

    def put_node_set_variable_values(self, id, name, step, values):
        """
        status = \\
          exo.put_node_set_variable_values(node_set_id, \\
            nsvar_name, \\
            time_step, \\
            nsvar_vals)

          -> store a list of node set variable values for a specified node
            set, node set variable name, and time step; the list has one
            variable value per node in the set

          input value(s):
            <int>          node_set_id  node set *ID* (not *INDEX*)
            <string>       nsvar_name   name of node set variable
            <int>          time_step    1-based index of time step
            <list<float>>  nsvar_vals

          return value(s):
            <bool>  status  True = successful execution
        """
        names = self.get_node_set_variable_names()
        var_id = names.index(name) + 1
        self.__ex_put_nset_var(step, var_id, id, values)
        return True

    # --------------------------------------------------------------------

    def get_all_node_set_params(self):
        """
        tot_num_ns_nodes, \\
        tot_num_ns_dist_facts = exo.get_all_node_set_params()

          -> get total number of nodes and distribution factors (e.g. nodal
            'weights') combined among all node sets

          return value(s):
            <int>  tot_num_ns_nodes
            <int>  tot_num_ns_dist_facts
        """
        self.__ex_get_node_set_ids()
        totNumSetNodes, totNumSetDistFacts = 0, 0
        for nodeSetId in self.nodeSetIds:
            (numSetNodes, numSetDistFacts) = self.__ex_get_node_set_param(
                int(nodeSetId))
            totNumSetNodes += numSetNodes
            totNumSetDistFacts += numSetDistFacts
        return (totNumSetNodes, totNumSetDistFacts)

    # --------------------------------------------------------------------

    def get_node_set_params(self, id):
        """
        num_ns_nodes, num_ns_dist_facts = \\
          exo.get_node_set_params(node_set_id)

          -> get number of nodes and distribution factors (e.g. nodal
            'weights') in a node set

          input value(s):
            <int>  node_set_id  node set *ID* (not *INDEX*)

          return value(s):
            <int>  num_ns_nodes
            <int>  num_ns_dist_facts
        """
        (numSetNodes, numSetDistFacts) = self.__ex_get_node_set_param(int(id))
        return (numSetNodes, numSetDistFacts)

    # --------------------------------------------------------------------

    def put_node_set_params(self, id, numSetNodes, numSetDistFacts=None):
        """
        exo.put_node_set_params(node_set_id, \\
          num_ns_nodes, \\
          num_ns_dist_facts)

          -> initialize a new node set

          input value(s):
            <int>  node_set_id        node set *ID* (not *INDEX*)
            <int>  num_ns_nodes       number of nodes to be added to set
            <int>  num_ns_dist_facts  (optional) number of distribution
              factors (e.g. nodal 'weights') --
              must be equal to zero or
              num_ns_nodes
        """
        if numSetDistFacts is None:
            numSetDistFacts = numSetNodes
        assert numSetDistFacts == 0 or numSetDistFacts == numSetNodes
        self.__ex_put_node_set_param(id, numSetNodes, numSetDistFacts)

    # --------------------------------------------------------------------

    def get_node_set_property_names(self):
        """
        nsprop_names = exo.get_node_set_property_names()

          -> get the list of node set property names for all node sets in
            the model

          return value(s):
            <list<string>>  nsprop_names
        """
        names = []
        nsType = ex_entity_type("EX_NODE_SET")
        inqType = "EX_INQ_NS_PROP"
        names = self.__ex_get_prop_names(nsType, inqType)
        return list(names)

    # --------------------------------------------------------------------

    def get_node_set_property_value(self, id, name):
        """
        nsprop_val = \\
          exo.get_node_set_property_value(node_set_id, nsprop_name)

          -> get node set property value (an integer) for a specified node
            set and node set property name

          input value(s):
            <int>     node_set_id  node set *ID* (not *INDEX*)
            <string>  nsprop_name

          return value(s):
            <int>  nsprop_val
        """
        nsType = ex_entity_type("EX_NODE_SET")
        propVal = self.__ex_get_prop(nsType, id, name)
        return int(propVal)

    # --------------------------------------------------------------------

    def put_node_set_property_value(self, id, name, value):
        """
        status = exo.put_node_set_property_value(node_set_id, \\
          nsprop_name, \\
          nsprop_val)

          -> store a node set property name and its integer value for a
            node set

          input value(s):
            <int>     node_set_id  node set *ID* (not *INDEX*)
            <string>  nsprop_name
            <int>     nsprop_val

          return value(s):
            <bool>  status  True = successful execution
        """
        nsType = ex_entity_type("EX_NODE_SET")
        return self.__ex_put_prop(nsType, id, name, value)

    #
    # sidesets
    #
    # --------------------------------------------------------------------

    def num_side_sets(self):
        """
        num_side_sets = exo.num_side_sets()

          -> get the number of side sets in the model

          return value(s):
            <int>  num_side_sets
        """
        return self.numSideSets.value

    # --------------------------------------------------------------------

    def get_side_set_ids(self):
        """
        side_set_ids = exo.get_side_set_ids()

          -> get mapping of exodus side set index to user- or application-
            defined side set id; side_set_ids is ordered
            by the *INDEX* ordering, a 1-based system going from
            1 to exo.num_side_sets(), used by exodus for storage
            and input/output of array data stored on the side sets; a
            user or application can optionally use a separate side set
            *ID* numbering system, so the side_set_ids array points to the
            side set *ID* for each side set *INDEX*

          return value(s):

            if array_type == 'ctype':
              <list<int>>  side_set_ids

            if array_type == 'numpy':
              <np_array<int>>  side_set_ids
        """
        self.__ex_get_side_set_ids()
        sideSetIds = list(self.sideSetIds)
        if self.use_numpy:
            sideSetIds = self.np.array(sideSetIds)
        return sideSetIds

    # --------------------------------------------------------------------

    def get_side_set_name(self, id):
        """
        side_set_name = exo.get_side_set_name(side_set_id)

          -> get the name of a side set

          input value(s):
            <int>  side_set_id  side set *ID* (not *INDEX*)

          return value(s):
            <string>  side_set_name
        """
        objType = ex_entity_type("EX_SIDE_SET")
        sideSetName = self.__ex_get_name(objType, id)
        return sideSetName

    # --------------------------------------------------------------------

    def put_side_set_name(self, id, name):
        """
        exo.put_side_set_name(side_set_id, side_set_name)

          -> store the name of a side set

          input value(s):
            <int>     side_set_id    side set *ID* (not *INDEX*)
            <string>  side_set_name
        """
        objType = ex_entity_type("EX_SIDE_SET")
        self.__ex_put_name(objType, id, name)

    # --------------------------------------------------------------------

    def get_side_set_names(self):
        """
        side_set_names = exo.get_side_set_names()

          -> get a list of all side set names ordered by side set *INDEX*;
            (see description of get_side_set_ids() for explanation of the
            difference between side set *ID* and side set *INDEX*)

          return value(s):
            <list<string>>  side_set_names
        """
        objType = ex_entity_type("EX_SIDE_SET")
        inqType = ex_inquiry("EX_INQ_SIDE_SETS")
        sideSetNames = self.__ex_get_names(objType, inqType)
        return sideSetNames

    # --------------------------------------------------------------------

    def put_side_set_names(self, names):
        """
        exo.put_side_set_names(side_set_names)

          -> store a list of all side set names ordered by side set *INDEX*;
            (see description of get_side_set_ids() for explanation of the
            difference between side set *ID* and side set *INDEX*)

          input value(s):
            <list<string>>  side_set_names
        """
        objType = ex_entity_type("EX_SIDE_SET")
        inqType = ex_inquiry("EX_INQ_SIDE_SETS")
        self.__ex_put_names(objType, inqType, names)

    # --------------------------------------------------------------------

    def num_faces_in_side_set(self, id):
        """
        num_ss_faces = exo.num_faces_in_side_set(side_set_id)

          -> get the number of faces in a side set

          input value(s):
            <int>  side_set_id  side set *ID* (not *INDEX*)

          return value(s):
            <int>  num_ss_faces
        """
        ssids = self.get_side_set_ids()
        if id not in ssids:
            print("WARNING: queried side set ID does not exist in database")
            return 0
        (num_side_in_set, num_dist_fact_in_set) = self.__ex_get_side_set_param(id)
        return num_side_in_set

    # --------------------------------------------------------------------

    def get_all_side_set_params(self):
        """
        tot_num_ss_sides, \\
        tot_num_ss_nodes, \\
        tot_num_ss_dist_facts = exo.get_all_side_set_params()

          -> get total number of sides, nodes, and distribution factors
            (e.g. nodal 'weights') combined among all side sets

          return value(s):
            <int>  tot_num_ss_sides
            <int>  tot_num_ss_nodes
            <int>  tot_num_ss_dist_facts

          NOTE:
            The number of nodes (and distribution factors) in a side set is
            the sum of all face nodes.  A single node can be counted more
            than once, i.e. once for each face it belongs to in the side set.
        """
        self.__ex_get_side_set_ids()
        totNumSetSides, totNumSetDistFacts = 0, 0  # totNumSetDistFacts = totNumSetNodes
        for sideSetId in self.sideSetIds:
            (numSetSides, numSetDistFacts) = self.__ex_get_side_set_param(
                int(sideSetId))
            totNumSetSides += numSetSides
            totNumSetDistFacts += numSetDistFacts
        totNumSetNodes = totNumSetDistFacts
        return (totNumSetSides, totNumSetNodes, totNumSetDistFacts)

    # --------------------------------------------------------------------

    def get_side_set_params(self, id):
        """
        num_ss_sides, num_ss_dist_facts = \\
          exo.get_side_set_params(side_set_id)

          -> get number of sides and nodal distribution factors (e.g. nodal
            'weights') in a side set

          input value(s):
            <int>  side_set_id  side set *ID* (not *INDEX*)

          return value(s):
            <int>  num_ss_sides
            <int>  num_ss_dist_facts

          NOTE:
            The number of nodes (and distribution factors) in a side set is
            the sum of all face nodes.  A single node can be counted more
            than once, i.e. once for each face it belongs to in the side set.
        """
        (numSetSides, numSetDistFacts) = self.__ex_get_side_set_param(int(id))
        return (numSetSides, numSetDistFacts)

    # --------------------------------------------------------------------

    def put_side_set_params(self, id, numSetSides, numSetDistFacts):
        """
        exo.put_side_set_params(side_set_id, \\
          num_ss_sides, \\
          num_ss_dist_facts)

          -> initialize a new side set

          input value(s):
            <int>  side_set_id        side set *ID* (not *INDEX*)
            <int>  num_ss_sides       number of sides to be added to set
            <int>  num_ss_dist_facts  number of nodal distribution factors
              (e.g. nodal 'weights')

          NOTE:
            The number of nodes (and distribution factors) in a side set is
            the sum of all face nodes.  A single node can be counted more
            than once, i.e. once for each face it belongs to in the side set.
        """
        self.__ex_put_side_set_param(id, numSetSides, numSetDistFacts)

    # --------------------------------------------------------------------

    def get_side_set(self, id):
        """
        ss_elems, ss_sides = exo.get_side_set(side_set_id)

          -> get the lists of element and side indices in a side set; the
            two lists correspond: together, ss_elems[i] and ss_sides[i]
            define the face of an element

          input value(s):
            <int>  side_set_id  side set *ID* (not *INDEX*)

          return value(s):

            if array_type == 'ctype':
              <list<int>>  ss_elems
              <list<int>>  ss_sides

            if array_type == 'numpy':
              <np_array<int>>  ss_elems
              <np_array<int>>  ss_sides
        """
        (side_set_elem_list, side_set_side_list) = self.__ex_get_side_set(id)
        if self.use_numpy:
            side_set_elem_list = ctype_to_numpy(self, side_set_elem_list)
            side_set_side_list = ctype_to_numpy(self, side_set_side_list)
        return (side_set_elem_list, side_set_side_list)

    # --------------------------------------------------------------------

    def put_side_set(self, id, sideSetElements, sideSetSides):
        """
        exo.put_side_set(side_set_id, ss_elems, ss_sides)

          -> store a side set by its id and the lists of element and side
            indices in the side set; the two lists correspond: together,
            ss_elems[i] and ss_sides[i] define the face of an element

          input value(s):
            <int>        side_set_id  side set *ID* (not *INDEX*)
            <list<int>>  ss_elems
            <list<int>>  ss_sides
        """
        self.__ex_put_side_set(id, sideSetElements, sideSetSides)

    # --------------------------------------------------------------------

    def get_side_set_dist_fact(self, id):
        """
        ss_dist_facts = exo.get_side_set_dist_fact(side_set_id)

          -> get the list of distribution factors for nodes in a side set

          input value(s):
            <int>        side_set_id  side set *ID* (not *INDEX*)

          return value(s):

            if array_type == 'ctype':
              <list<float>>  ss_dist_facts  a list of distribution factors,
                e.g. nodal 'weights'

            if array_type == 'numpy':
              <np_array<double>>  ss_dist_facts  a list of distribution
                factors, e.g. nodal
                'weights'

          NOTE:
            The number of nodes (and distribution factors) in a side set is
            the sum of all face nodes.  A single node can be counted more
            than once, i.e. once for each face it belongs to in the side set.
        """
        side_set_dfs = list(self.__ex_get_side_set_dist_fact(id))
        if self.use_numpy:
            side_set_dfs = self.np.array(side_set_dfs)
        return side_set_dfs

    # --------------------------------------------------------------------

    def put_side_set_dist_fact(self, id, sideSetDistFact):
        """
        exo.put_side_set_dist_fact(side_set_id, ss_dist_facts)

          -> store the list of distribution factors for nodes in a side set

          input value(s):
            <int>          node_set_id    node set *ID* (not *INDEX*)
            <list<float>>  ns_dist_facts  a list of distribution factors,
              e.g. nodal 'weights'

          NOTE:
            The number of nodes (and distribution factors) in a side set is
            the sum of all face nodes.  A single node can be counted more
            than once, i.e. once for each face it belongs to in the side set.
        """
        self.__ex_put_side_set_dist_fact(id, sideSetDistFact)

    # --------------------------------------------------------------------

    def get_side_set_node_list(self, id):
        """
        ss_num_nodes_per_side, \\
        ss_nodes = exo.get_side_set_node_list(side_set_id)

          -> get two lists:
            1. number of nodes for each side in the set
            2. concatenation of the nodes for each side in the set

          input value(s):
            <int>        side_set_id  side set *ID* (not *INDEX*)

          return value(s):

            if array_type == 'ctype':
              <list<int>>  ss_num_side_nodes
              <list<int>>  ss_nodes

            if array_type == 'numpy':
              <np_array<int>>  ss_num_side_nodes
              <np_array<int>>  ss_nodes

          NOTE:
            The number of nodes (and distribution factors) in a side set is
            the sum of the entries in ss_num_nodes_per_side.  A single node
            can be counted more than once, i.e. once for each face it
            belongs to in the side set.
        """
        (side_set_node_cnt_list,
         side_set_node_list) = self.__ex_get_side_set_node_list(id)
        if self.use_numpy:
            side_set_node_cnt_list = ctype_to_numpy(
                self, side_set_node_cnt_list)
            side_set_node_list = ctype_to_numpy(self, side_set_node_list)
        return (side_set_node_cnt_list, side_set_node_list)

    # --------------------------------------------------------------------

    def get_side_set_variable_truth_table(self, sideSetId=None):
        """
        ssvar_truth_tab = \\
          exo.get_side_set_variable_truth_table(sideSetID=side_set_id)

          -> gets a truth table indicating which variables are defined for
            a side set; if side_set_id is not passed, then a concatenated
            truth table for all side sets is returned with variable index
            cycling faster than side set index

          input value(s):
            (optional) <int>  side_set_id  side set *ID* (not *INDEX*)

          return value(s):
            <list<bool>>  ssvar_truth_tab  True if variable is defined in
              a side set, False otherwise
        """
        truthTable = self.__ex_get_sset_var_tab()
        if sideSetId is not None:
            self.get_side_set_ids()
            assert sideSetId in list(self.sideSetIds)
            indx = list(self.sideSetIds).index(sideSetId)
            numVars = self.__ex_get_var_param("s").value
            start, stop = (indx * numVars, (indx + 1) * numVars)
            return truthTable[start:stop]
        return truthTable

    # --------------------------------------------------------------------

    def set_side_set_variable_truth_table(self, table):
        """
        status = \\
          exo.set_side_set_variable_truth_table(ssvar_truth_tab)

          -> stores a truth table indicating which variables are defined for
            all side sets and all side set variables; variable index cycles
            faster than side set index

          input value(s):
            <list<bool>>  ssvar_truth_tab  True if variable is defined in
              a side set, False otherwise

          return value(s):
            <bool>  status  True = successful execution
        """
        self.get_side_set_ids()
        numBlks = len(self.sideSetIds)
        numVars = int(self.__ex_get_var_param("s").value)
        assert len(table) == (numBlks * numVars)
        return self.__ex_put_sset_var_tab(table)

    # --------------------------------------------------------------------

    def get_side_set_variable_number(self):
        """
        num_ssvars = exo.get_side_set_variable_number()

          -> get the number of side set variables in the model

            return value(s):
              <int>  num_ssvars
        """
        ssType = ex_entity_type("EX_SIDE_SET")
        num = self.__ex_get_variable_param(ssType)
        return num.value

    # --------------------------------------------------------------------

    def set_side_set_variable_number(self, number):
        """
        status = exo.set_side_set_variable_number(num_ssvars)

          -> update the number of side set variables in the model

            input value(s):
              <int>  num_ssvars

            return value(s):
              <bool>  status  True = successful execution
        """
        ssType = ex_entity_type("EX_SIDE_SET")
        self.__ex_put_variable_param(ssType, number)
        return True

    # --------------------------------------------------------------------

    def get_side_set_variable_names(self):
        """
        ssvar_names = exo.get_side_set_variable_names()

          -> get the list of side set variable names in the model

            return value(s):
              <list<string>>  ssvar_names
        """
        names = []
        ssType = ex_entity_type("EX_SIDE_SET")
        num_vars = self.__ex_get_variable_param(ssType)
        for varid in range(num_vars.value):
            varid += 1
            name = self.__ex_get_variable_name(ssType, varid)
            names.append(name.value)
        return names

    # --------------------------------------------------------------------

    def put_side_set_variable_name(self, name, index):
        """
        status = exo.put_side_set_variable_name(ssvar_name, ssvar_index)

          -> add the name and index of a new side set variable to the model;
            side set variable indexing goes from 1 to
            exo.get_side_set_variable_number()

          input value(s):
            <string>  ssvar_name   name of new side set variable
            <int>     ssvar_index  1-based index of new side set variable

          return value(s):
            <bool>  status  True = successful execution

          NOTE:
            this method is often called within the following sequence:
            >>> num_ssvars = exo.get_side_set_variable_number()
            >>> new_ssvar_index = num_ssvars + 1
            >>> num_ssvars += 1
            >>> exo.set_side_set_variable_number(num_ssvars)
            >>> exo.put_side_set_variable_name("new_ssvar", new_ssvar_index)
        """
        ssType = ex_entity_type("EX_SIDE_SET")
        SSvarNames = self.get_side_set_variable_names()
        if name in SSvarNames:
            print("WARNING: Side set variable \"", name, "\" already exists.")
        if index > len(SSvarNames):
            raise Exception("ERROR: variable index out of range.")
        self.__ex_put_variable_name(ssType, index, name)
        return True

    # --------------------------------------------------------------------

    def get_side_set_variable_values(self, id, name, step):
        """
        ssvar_vals = \\
          exo.get_side_set_variable_values(side_set_id, \\
            ssvar_name, \\
            time_step)

          -> get list of side set variable values for a specified side
            set, side set variable name, and time step; the list has
            one variable value per side in the set

          input value(s):
            <int>     side_set_id  side set *ID* (not *INDEX*)
            <string>  ssvar_name   name of side set variable
            <int>     time_step    1-based index of time step

          return value(s):

            if array_type == 'ctype':
              <list<c_double>>  ssvar_vals

            if array_type == 'numpy':
              <np_array<double>>  ssvar_vals
        """
        names = self.get_side_set_variable_names()
        var_id = names.index(name) + 1
        values = self.__ex_get_sset_var(step, var_id, id)
        if self.use_numpy:
            values = ctype_to_numpy(self, values)
        return values

    # --------------------------------------------------------------------

    def put_side_set_variable_values(self, id, name, step, values):
        """
        status = \\
          exo.put_side_set_variable_values(side_set_id, \\
            ssvar_name, \\
            time_step, \\
            ssvar_vals)

          -> store a list of side set variable values for a specified side
            set, side set variable name, and time step; the list has one
            variable value per side in the set

          input value(s):
            <int>          side_set_id  side set *ID* (not *INDEX*)
            <string>       ssvar_name   name of side set variable
            <int>          time_step    1-based index of time step
            <list<float>>  ssvar_vals

          return value(s):
            <bool>  status  True = successful execution
        """
        names = self.get_side_set_variable_names()
        var_id = names.index(name) + 1
        self.__ex_put_sset_var(step, var_id, id, values)
        return True

    # --------------------------------------------------------------------

    def get_side_set_property_names(self):
        """
        ssprop_names = exo.get_side_set_property_names()

          -> get the list of side set property names for all side sets in
            the model

          return value(s):
            <list<string>>  ssprop_names
        """
        names = []
        ssType = ex_entity_type("EX_SIDE_SET")
        inqType = "EX_INQ_SS_PROP"
        names = self.__ex_get_prop_names(ssType, inqType)
        return list(names)

    # --------------------------------------------------------------------

    def get_side_set_property_value(self, id, name):
        """
        ssprop_val = \\
          exo.get_side_set_property_value(side_set_id, ssprop_name)

          -> get side set property value (an integer) for a specified side
            set and side set property name

          input value(s):
            <int>     side_set_id  side set *ID* (not *INDEX*)
            <string>  ssprop_name

          return value(s):
            <int>  ssprop_val
        """
        ssType = ex_entity_type("EX_SIDE_SET")
        propVal = self.__ex_get_prop(ssType, id, name)
        return int(propVal)

    # --------------------------------------------------------------------

    def put_side_set_property_value(self, id, name, value):
        """
        status = exo.put_side_set_property_value(side_set_id, \\
          ssprop_name, \\
          ssprop_val)

          -> store a side set property name and its integer value for a
            side set

          input value(s):
            <int>     side_set_id  side set *ID* (not *INDEX*)
            <string>  ssprop_name
            <int>     ssprop_val

          return value(s):
            <bool>  status  True = successful execution
        """
        ssType = ex_entity_type("EX_SIDE_SET")
        return self.__ex_put_prop(ssType, id, name, value)

    #
    # global variables
    #
    # --------------------------------------------------------------------

    def get_global_variable_number(self):
        """
        num_gvars = exo.get_global_variable_number()

          -> get the number of global variables in the model

            return value(s):
              <int>  num_gvars
        """
        gbType = ex_entity_type("EX_GLOBAL")
        num = self.__ex_get_variable_param(gbType)
        return num.value

    # --------------------------------------------------------------------

    def set_global_variable_number(self, number):
        """
        status = exo.set_global_variable_number(num_gvars)

          -> update the number of global variables in the model

            input value(s):
              <int>  num_gvars

            return value(s):
              <bool>  status  True = successful execution
        """
        gbType = ex_entity_type("EX_GLOBAL")
        self.__ex_put_variable_param(gbType, number)
        return True

    # --------------------------------------------------------------------

    def get_global_variable_names(self):
        """
        gvar_names = exo.get_global_variable_names()

          -> get the list of global variable names in the model

            return value(s):
              <list<string>>  gvar_names
        """
        if self.get_global_variable_number() == 0:
            return []
        return self.__ex_get_var_names("g")

    # --------------------------------------------------------------------

    def put_global_variable_name(self, name, index):
        """
        status = exo.put_global_variable_name(gvar_name, gvar_index)

          -> add the name and index of a new global variable to the model;
            global variable indexing goes from 1 to
            exo.get_global_variable_number()

          input value(s):
            <string>  gvar_name   name of new global variable
            <int>     gvar_index  1-based index of new global variable

          return value(s):
            <bool>  status  True = successful execution

          NOTE:
            this method is often called within the following sequence:
            >>> num_gvars = exo.get_global_variable_number()
            >>> new_gvar_index = num_gvars + 1
            >>> num_gvars += 1
            >>> exo.set_global_variable_number(num_gvars)
            >>> exo.put_global_variable_name("new_gvar", new_gvar_index)
        """
        gbType = ex_entity_type("EX_GLOBAL")
        GlobVarNames = self.get_global_variable_names()
        if name in GlobVarNames:
            print("WARNING: global variable \"", name, "\" already exists.")
        if index > len(GlobVarNames):
            print("index", index, "len", len(GlobVarNames))
            raise Exception("ERROR: variable index out of range.")
        self.__ex_put_variable_name(gbType, index, name)
        return True

    # --------------------------------------------------------------------

    def get_global_variable_value(self, name, step):
        """
        gvar_val = exo.get_global_variable_value(gvar_name, time_step)

          -> get a global variable value for a specified global variable
            name and time step

          input value(s):
            <string>  gvar_name  name of global variable
            <int>     time_step  1-based index of time step

          return value(s):
            <float>  gvar_val
        """
        names = self.get_global_variable_names()
        var_id = names.index(name)
        gbType = ex_entity_type("EX_GLOBAL")
        num = self.__ex_get_variable_param(gbType)
        gvalues = self.__ex_get_var(step, gbType, 0, 1, num.value)
        return gvalues[var_id]

    # --------------------------------------------------------------------

    def get_all_global_variable_values(self, step):
        """
        gvar_vals = exo.get_all_global_variable_values(time_step)

          -> get all global variable values (one for each global variable
            name, and in the order given by exo.get_global_variable_names())
            at a specified time step

          input value(s):
            <int>     time_step  1-based index of time step

          return value(s):

            if array_type == 'ctype':
              <list<float>>  gvar_vals

            if array_type == 'numpy':
              <np_array<double>>  gvar_vals
        """
        gbType = ex_entity_type("EX_GLOBAL")
        num = self.__ex_get_variable_param(gbType)
        gvalues = self.__ex_get_var(step, gbType, 0, 1, num.value)
        values = []
        for i in xrange(num.value):
            values.append(gvalues[i])
        if self.use_numpy:
            values = self.np.array(values)
        return values

    # --------------------------------------------------------------------

    def put_global_variable_value(self, name, step, value):
        """
        status = exo.put_global_variable_value(gvar_name, \\
          time_step, \\
          gvar_val)

          -> store a global variable value for a specified global variable
            name and time step

          input value(s):
            <string>  gvar_name  name of global variable
            <int>     time_step  1-based index of time step
            <float>   gvar_val

          return value(s):
            <bool>  status  True = successful execution
        """
        # we must write all values at once, not individually
        names = self.get_global_variable_names()
        # get all values
        numVals = self.get_global_variable_number()
        values = (c_double * numVals)()
        for i in xrange(numVals):
            values[i] = c_double(
                self.get_global_variable_value(
                    names[i], step))
        # adjust one of them
        values[names.index(name)] = c_double(value)
        # write them all
        EXODUS_LIB.ex_put_glob_vars(self.fileId,
                                    c_int(step),
                                    c_int(numVals),
                                    values)
        return True

    # --------------------------------------------------------------------

    def put_all_global_variable_values(self, step, values):
        """
        status = exo.put_all_global_variable_values(time_step, gvar_vals)

          -> store all global variable values (one for each global variable
            name, and in the order given by exo.get_global_variable_names())
            at a specified time step

          input value(s):
            <int>          time_step  1-based index of time step
            <list<float>>  gvar_vals

          return value(s):
            <bool>  status  True = successful execution
        """
        numVals = self.get_global_variable_number()
        gvalues = (c_double * numVals)()
        for i in xrange(numVals):
            gvalues[i] = c_double(values[i])
        EXODUS_LIB.ex_put_glob_vars(self.fileId,
                                    c_int(step),
                                    c_int(numVals),
                                    gvalues)
        return True

    # --------------------------------------------------------------------

    def get_global_variable_values(self, name):
        """
        gvar_vals = exo.get_global_variable_values(gvar_name)

          -> get global variable values over all time steps for one global
            variable name

          input value(s):
            <string>  gvar_name  name of global variable

          return value(s):

            if array_type == 'ctype':
              <list<float>>  gvar_vals

            if array_type == 'numpy':
              <np_array<double>>  gvar_vals
        """
        names = self.get_global_variable_names()
        var_id = names.index(name)
        gbType = ex_entity_type("EX_GLOBAL")
        num = self.__ex_get_variable_param(gbType)
        values = []
        for i in range(self.numTimes.value):
            gvalues = self.__ex_get_var(i + 1, gbType, 0, 1, num.value)
            values.append(gvalues[var_id])
        if self.use_numpy:
            values = self.np.array(values)
        return values

    # --------------------------------------------------------------------

    def put_polyhedra_elem_blk(self, blkID,
                               num_elems_this_blk,
                               num_faces,
                               num_attr_per_elem):
        """
        status = exo.put_polyhedra_elem_blk(blkID, num_elems_this_blk,
                                            num_faces, num_attr_per_elem)

          -> put in an element block with polyhedral elements

          input values:
            <int>     blkID               id of the block to be added
            <int>     num_elems_this_blk
            <int>     num_faces  total number of faces in this block
            <int>     num_attr_per_elem

          return value(s):
            <bool>  status  True = successful execution
        """

        ebType = ex_entity_type("EX_ELEM_BLOCK")

        EXODUS_LIB.ex_put_block(self.fileId, ebType, c_int(blkID),
                                create_string_buffer("NFACED"),
                                c_longlong(num_elems_this_blk),
                                c_longlong(0),
                                c_longlong(0),
                                c_longlong(num_faces),
                                c_longlong(num_attr_per_elem))
        return True

    # --------------------------------------------------------------------

    def put_polyhedra_face_blk(self, blkID,
                               num_faces_this_blk,
                               num_nodes,
                               num_attr_per_face):
        """
        status = exo.put_polyhedra_face_blk(blkID, num_faces_this_blk,
                                            num_nodes, num_attr_per_face)

          -> put in a block of faces

          input values:
            <int>     blkID               id of the block to be added
            <int>     num_faces_this_blk
            <int>     num_nodes           total number of nodes in this block
            <int>     num_attr_per_face

          return value(s):
            <bool>  status  True = successful execution
        """
        fbType = ex_entity_type("EX_FACE_BLOCK")

        EXODUS_LIB.ex_put_block(self.fileId, fbType, c_int(blkID),
                                create_string_buffer("NSIDED"),
                                c_longlong(num_faces_this_blk),
                                c_longlong(num_nodes),
                                c_longlong(0),
                                c_longlong(0),
                                c_longlong(num_attr_per_face))
        return True

    # --------------------------------------------------------------------

    def put_face_count_per_polyhedra(self, blkID, entityCounts):
        """
        status = exo.put_face_count_per_polyhedra(blkID, entityCounts)

          -> put in a count of faces in for each polyhedra in an elem block

          input values:
            <int>     blkID               id of the block to be added

            if array_type == 'ctype':
              <list<float>>  entityCounts

            if array_type == 'numpy':
              <np_array<double>>  entityCounts

          return value(s):
            <bool>  status  True = successful execution
        """
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        entity_counts = (c_int * len(entityCounts))()
        entity_counts[:] = entityCounts
        EXODUS_LIB.ex_put_entity_count_per_polyhedra(
            self.fileId, ebType, c_int(blkID), entity_counts)
        return True

    # --------------------------------------------------------------------

    def put_node_count_per_face(self, blkID, entityCounts):
        """
        status = exo.put_node_count_per_face(blkID, entityCounts)

          -> put in a count of nodes in for each face in a polygonal face block

          input values:
            <int>     blkID               id of the block to be added

            if array_type == 'ctype':
              <list<float>>  entityCounts

            if array_type == 'numpy':
              <np_array<double>>  entityCounts

          return value(s):
            <bool>  status  True = successful execution
        """
        ebType = ex_entity_type("EX_FACE_BLOCK")
        entity_counts = (c_int * len(entityCounts))()
        entity_counts[:] = entityCounts
        EXODUS_LIB.ex_put_entity_count_per_polyhedra(
            self.fileId, ebType, c_int(blkID), entity_counts)
        return True

    # --------------------------------------------------------------------

    def put_elem_face_conn(self, blkId, elemFaceConn):
        """
        status = exo.put_elem_face_conn(blkID, elemFaceConn)

          -> put in connectivity information from elems to faces

          input values:
            <int>     blkID               id of the elem block to be added

            if array_type == 'ctype':
              <list<float>>  elemFaceConn  (raveled/flat list)

            if array_type == 'numpy':
              <np_array<double>>  elemFaceConn  (raveled/flat array)

          return value(s):
            <bool>  status  True = successful execution
        """
        ebType = ex_entity_type("EX_ELEM_BLOCK")
        elem_face_conn = (c_int * len(elemFaceConn))()
        elem_face_conn[:] = elemFaceConn
        EXODUS_LIB.ex_put_conn(self.fileId, ebType, c_int(blkId),
                               None, None, elem_face_conn)
        return True

    # --------------------------------------------------------------------

    def put_face_node_conn(self, blkId, faceNodeConn):
        """
        status = exo.put_face_node_conn(blkID, faceNodeConn)

          -> put in connectivity information from faces to nodes

          input values:
            <int>     blkID               id of the face block to be added

            if array_type == 'ctype':
              <list<float>>  faceNodeConn  (raveled/flat list)

            if array_type == 'numpy':
              <np_array<double>>  faceNodeConn  (raveled/flat array)

          return value(s):
            <bool>  status  True = successful execution
        """
        ebType = ex_entity_type("EX_FACE_BLOCK")
        node_conn = (c_int * len(faceNodeConn))()
        node_conn[:] = faceNodeConn
        EXODUS_LIB.ex_put_conn(self.fileId, ebType, c_int(blkId),
                               node_conn, None, None)
        return True

    # --------------------------------------------------------------------

    def close(self):
        """
        exo.close()

          -> close the exodus file

          NOTE:
            Can only be called once for an exodus object, and once called
            all methods for that object become inoperable
        """
        print("Closing exodus file: " + self.fileName)
        errorInt = EXODUS_LIB.ex_close(self.fileId)
        if errorInt != 0:
            raise Exception(
                "ERROR: Closing file " +
                self.fileName +
                " had problems.")

    # --------------------------------------------------------------------
    #
    # Private Exodus API calls
    #
    # --------------------------------------------------------------------

    def __open(self, io_size=0):
        print("Opening exodus file: " + self.fileName)
        self.mode = EX_READ
        if self.modeChar.lower() == "a":
            self.mode = EX_WRITE
        if self.modeChar.lower() == "w+":
            self.mode = EX_CLOBBER

        if self.modeChar.lower() in [
                "a", "r"] and not os.path.isfile(self.fileName):
            raise Exception(
                "ERROR: Cannot open " +
                self.fileName +
                " for read. Does not exist.")
        elif self.modeChar.lower() == "w" and os.path.isfile(self.fileName):
            raise Exception("ERROR: Cowardly not opening " + self.fileName +
                            " for write. File already exists.")
        elif self.modeChar.lower() not in ["a", "r", "w", "w+"]:
            raise Exception(
                "ERROR: File open mode " +
                self.modeChar +
                " unrecognized.")

        self.comp_ws = c_int(8)
        self.io_ws = c_int(io_size)
        self.version = c_float(0.0)
        if self.modeChar.lower() in ["a", "r"]:  # open existing file
            self.fileId = EXODUS_LIB.ex_open_int(self.fileName, self.mode,
                                                 byref(self.comp_ws),
                                                 byref(self.io_ws),
                                                 byref(self.version),
                                                 EX_API_VERSION_NODOT)
        else:  # create file
            if io_size == 0:
                io_size = 8
                self.io_ws = c_int(io_size)
            self.__create()

    # --------------------------------------------------------------------

    def __create(self):
        self.fileId = EXODUS_LIB.ex_create_int(self.fileName, self.mode,
                                               byref(self.comp_ws),
                                               byref(self.io_ws),
                                               EX_API_VERSION_NODOT)

    # --------------------------------------------------------------------

    def __copy_file(self, fileId, include_transient=False):
        if include_transient:
            EXODUS_LIB.ex_copy(self.fileId, fileId)
            EXODUS_LIB.ex_copy_transient(self.fileId, fileId)
        else:
            EXODUS_LIB.ex_copy(self.fileId, fileId)

    # --------------------------------------------------------------------

    def __ex_get_info(self):
        self.Title = create_string_buffer(MAX_LINE_LENGTH + 1)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            self.numDim = c_longlong(0)
            self.numNodes = c_longlong(0)
            self.numElem = c_longlong(0)
            self.numElemBlk = c_longlong(0)
            self.numNodeSets = c_longlong(0)
            self.numSideSets = c_longlong(0)
        else:
            self.numDim = c_int(0)
            self.numNodes = c_int(0)
            self.numElem = c_int(0)
            self.numElemBlk = c_int(0)
            self.numNodeSets = c_int(0)
            self.numSideSets = c_int(0)
        EXODUS_LIB.ex_get_init(
            self.fileId, self.Title,
            byref(self.numDim),
            byref(self.numNodes),
            byref(self.numElem),
            byref(self.numElemBlk),
            byref(self.numNodeSets),
            byref(self.numSideSets))

    # --------------------------------------------------------------------

    def __ex_put_info(self, info):
        self.Title = create_string_buffer(info[0], MAX_LINE_LENGTH + 1)
        self.numDim = c_longlong(info[1])
        self.numNodes = c_longlong(info[2])
        self.numElem = c_longlong(info[3])
        self.numElemBlk = c_longlong(info[4])
        self.numNodeSets = c_longlong(info[5])
        self.numSideSets = c_longlong(info[6])
        EXODUS_LIB.ex_put_init(
            self.fileId,
            self.Title,
            self.numDim,
            self.numNodes,
            self.numElem,
            self.numElemBlk,
            self.numNodeSets,
            self.numSideSets)
        self.version = self.__ex_inquire_float(ex_inquiry("EX_INQ_DB_VERS"))

    # --------------------------------------------------------------------

    def __ex_put_concat_elem_blk(self, elemBlkIDs, elemType, numElemThisBlk,
                                 numNodesPerElem, numAttr, defineMaps):
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_IDS_INT64_API:
            elem_blk_ids = (c_longlong * len(elemBlkIDs))()
            elem_blk_ids[:] = elemBlkIDs
            num_elem_this_blk = (c_longlong * len(elemBlkIDs))()
            num_elem_this_blk[:] = numElemThisBlk
            num_nodes_per_elem = (c_longlong * len(elemBlkIDs))()
            num_nodes_per_elem[:] = numNodesPerElem
            num_attr = (c_longlong * len(elemBlkIDs))()
            num_attr[:] = numAttr
        else:
            elem_blk_ids = (c_int * len(elemBlkIDs))()
            elem_blk_ids[:] = elemBlkIDs
            num_elem_this_blk = (c_int * len(elemBlkIDs))()
            num_elem_this_blk[:] = numElemThisBlk
            num_nodes_per_elem = (c_int * len(elemBlkIDs))()
            num_nodes_per_elem[:] = numNodesPerElem
            num_attr = (c_int * len(elemBlkIDs))()
            num_attr[:] = numAttr
        elem_type = (c_char_p * len(elemBlkIDs))()
        elem_type[:] = elemType
        define_maps = c_int(defineMaps)
        EXODUS_LIB.ex_put_concat_elem_block(
            self.fileId,
            elem_blk_ids,
            elem_type,
            num_elem_this_blk,
            num_nodes_per_elem,
            num_attr,
            define_maps)

    # --------------------------------------------------------------------

    def __ex_get_qa(self):
        num_qa_recs = c_int(self.__ex_inquire_int(ex_inquiry("EX_INQ_QA")))
        qa_rec_ptrs = ((POINTER(c_char * (MAX_STR_LENGTH + 1)) * 4) * num_qa_recs.value)()
        for i in range(num_qa_recs.value):
            for j in range(4):
                qa_rec_ptrs[i][j] = pointer(
                    create_string_buffer(MAX_STR_LENGTH + 1))
        if num_qa_recs.value:
            EXODUS_LIB.ex_get_qa(self.fileId, byref(qa_rec_ptrs))
        qa_recs = []
        for qara in qa_rec_ptrs:
            qa_rec_list = []
            for ptr in qara:
                qa_rec_list.append(ptr.contents.value)
            qa_rec_tuple = tuple(qa_rec_list)
            assert len(qa_rec_tuple) == 4
            qa_recs.append(qa_rec_tuple)
        return qa_recs

    # --------------------------------------------------------------------

    def __ex_put_qa(self, qaRecs):
        num_qa_recs = c_int(len(qaRecs))
        qa_rec_ptrs = ((POINTER(c_char * (MAX_STR_LENGTH + 1)) * 4) * num_qa_recs.value)()
        for i in range(num_qa_recs.value):
            for j in range(4):
                qa_rec_ptrs[i][j] = pointer(create_string_buffer(
                    str(qaRecs[i][j]), MAX_STR_LENGTH + 1))
        EXODUS_LIB.ex_put_qa(self.fileId, num_qa_recs, byref(qa_rec_ptrs))
        return True

    # --------------------------------------------------------------------

    def _ex_get_info_recs_quietly(self):
        num_infos = c_int(self.__ex_inquire_int(ex_inquiry("EX_INQ_INFO")))
        info_ptrs = (POINTER(c_char * (MAX_LINE_LENGTH + 1)) * num_infos.value)()
        for i in range(num_infos.value):
            info_ptrs[i] = pointer(create_string_buffer(MAX_LINE_LENGTH + 1))
        if num_infos.value:
            EXODUS_LIB.ex_get_info(self.fileId, byref(info_ptrs))
        info_recs = []
        for irp in info_ptrs:
            info_recs.append(irp.contents.value)
        return info_recs

    # --------------------------------------------------------------------

    def __ex_get_info_recs(self):
        num_infos = c_int(self.__ex_inquire_int(ex_inquiry("EX_INQ_INFO")))
        info_ptrs = (POINTER(c_char * (MAX_LINE_LENGTH + 1)) * num_infos.value)()
        for i in range(num_infos.value):
            info_ptrs[i] = pointer(create_string_buffer(MAX_LINE_LENGTH + 1))
        EXODUS_LIB.ex_get_info(self.fileId, byref(info_ptrs))
        info_recs = []
        for irp in info_ptrs:
            info_recs.append(irp.contents.value)
        for rec in info_recs:
            if len(rec) > MAX_LINE_LENGTH:
                print("WARNING: max line length reached for one or more info records;")
                print("         info might be incomplete for these records")
                break
        return info_recs

    # --------------------------------------------------------------------

    def __ex_put_info_recs(self, infoRecs):
        num_infos = c_int(len(infoRecs))
        info_ptrs = (POINTER(c_char * (MAX_LINE_LENGTH + 1)) * num_infos.value)()
        for i in range(num_infos.value):
            info_ptrs[i] = pointer(create_string_buffer(
                str(infoRecs[i]), MAX_LINE_LENGTH + 1))
        EXODUS_LIB.ex_put_info(self.fileId, num_infos, byref(info_ptrs))
        return True

    # --------------------------------------------------------------------

    def __ex_inquire_float(self, id):
        dummy_char = create_string_buffer(MAX_LINE_LENGTH + 1)
        ret_float = c_float(0.0)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_INQ_INT64_API:
            dummy_int = c_longlong(0)
        else:
            dummy_int = c_int(0)
        val = EXODUS_LIB.ex_inquire(
            self.fileId,
            id,
            byref(dummy_int),
            byref(ret_float),
            dummy_char)
        if val < 0:
            raise Exception(
                "ERROR: ex_inquire(" +
                str(id) +
                ") failed on " +
                self.fileName)
        return ret_float

    # --------------------------------------------------------------------

    def __ex_inquire_int(self, id):
        val = EXODUS_LIB.ex_inquire_int(self.fileId, id)
        if val < 0:
            raise Exception(
                "ERROR: ex_inquire_int(" +
                str(id) +
                ") failed on " +
                self.fileName)
        return val

    # --------------------------------------------------------------------

    def __ex_get_coord_names(self):
        coord_name_ptrs = (
            POINTER(c_char * (MAX_NAME_LENGTH + 1)) * self.numDim.value)()
        for i in range(self.numDim.value):
            coord_name_ptrs[i] = pointer(
                create_string_buffer(
                    MAX_NAME_LENGTH + 1))
        EXODUS_LIB.ex_get_coord_names(self.fileId, byref(coord_name_ptrs))
        coord_names = []
        for cnp in coord_name_ptrs:
            coord_names.append(cnp.contents.value)
        return coord_names

    # --------------------------------------------------------------------

    def __ex_put_coord_names(self, names):
        coord_name_ptrs = (
            POINTER(c_char * (MAX_NAME_LENGTH + 1)) * self.numDim.value)()
        assert len(names) == self.numDim.value
        for i in range(self.numDim.value):
            coord_name_ptrs[i] = pointer(
                create_string_buffer(
                    names[i], MAX_NAME_LENGTH + 1))
        EXODUS_LIB.ex_put_coord_names(self.fileId, byref(coord_name_ptrs))

    # --------------------------------------------------------------------

    def __ex_get_all_times(self):
        self.times = (c_double * self.numTimes.value)()
        EXODUS_LIB.ex_get_all_times(self.fileId, byref(self.times))

    # --------------------------------------------------------------------

    def __ex_get_time(self, timeStep):
        time_step = c_int(timeStep)
        time_val = c_double(0.0)
        EXODUS_LIB.ex_get_time(self.fileId, time_step, byref(time_val))
        return time_val.value()

    # --------------------------------------------------------------------

    def __ex_put_time(self, timeStep, timeVal):
        time_step = c_int(timeStep)
        time_val = c_double(timeVal)
        EXODUS_LIB.ex_put_time(self.fileId, time_step, byref(time_val))
        return True

    # --------------------------------------------------------------------

    def __ex_get_name(self, objType, objId):
        obj_type = c_int(objType)
        obj_id = c_int(objId)
        obj_name = create_string_buffer(MAX_NAME_LENGTH + 1)
        EXODUS_LIB.ex_get_name(self.fileId, obj_type, obj_id, byref(obj_name))
        return obj_name.value

    # --------------------------------------------------------------------

    def __ex_put_name(self, objType, objId, objName):
        obj_type = c_int(objType)
        obj_id = c_int(objId)
        obj_name = create_string_buffer(objName, MAX_NAME_LENGTH + 1)
        EXODUS_LIB.ex_put_name(self.fileId, obj_type, obj_id, obj_name)

    # --------------------------------------------------------------------

    def __ex_get_names(self, objType, inqType):
        obj_type = c_int(objType)
        num_objs = c_int(self.__ex_inquire_int(inqType))
        numObjs = num_objs.value
        obj_name_ptrs = (POINTER(c_char * (MAX_NAME_LENGTH + 1)) * numObjs)()
        for i in range(numObjs):
            obj_name_ptrs[i] = pointer(
                create_string_buffer(
                    MAX_NAME_LENGTH + 1))
        EXODUS_LIB.ex_get_names(self.fileId, obj_type, byref(obj_name_ptrs))
        obj_names = []
        for onp in obj_name_ptrs:
            obj_names.append(onp.contents.value)
        return obj_names

    # --------------------------------------------------------------------

    def __ex_put_names(self, objType, inqType, objNames):
        num_objs = c_int(self.__ex_inquire_int(inqType))
        numObjs = num_objs.value
        assert numObjs == len(objNames)
        obj_name_ptrs = (POINTER(c_char * (MAX_NAME_LENGTH + 1)) * numObjs)()
        obj_type = c_int(objType)
        for i in range(numObjs):
            obj_name_ptrs[i] = pointer(
                create_string_buffer(
                    objNames[i], MAX_NAME_LENGTH + 1))
        EXODUS_LIB.ex_put_names(self.fileId, obj_type, byref(obj_name_ptrs))

    # --------------------------------------------------------------------

    def __ex_get_elem_blk_ids(self):
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_IDS_INT64_API:
            self.elemBlkIds = (c_longlong * self.numElemBlk.value)()
        else:
            self.elemBlkIds = (c_int * self.numElemBlk.value)()
        if self.numElemBlk.value > 0:
            EXODUS_LIB.ex_get_ids(
                self.fileId,
                ex_entity_type('EX_ELEM_BLOCK'),
                byref(self.elemBlkIds))

    # --------------------------------------------------------------------

    def __ex_get_side_set_ids(self):
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_IDS_INT64_API:
            self.sideSetIds = (c_longlong * self.numSideSets.value)()
        else:
            self.sideSetIds = (c_int * self.numSideSets.value)()
        if self.num_side_sets() > 0:
            EXODUS_LIB.ex_get_ids(
                self.fileId,
                ex_entity_type('EX_SIDE_SET'),
                byref(self.sideSetIds))

    # --------------------------------------------------------------------

    def __ex_get_node_set_ids(self):
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_IDS_INT64_API:
            self.nodeSetIds = (c_longlong * self.numNodeSets.value)()
        else:
            self.nodeSetIds = (c_int * self.numNodeSets.value)()
        if self.num_node_sets() > 0:
            EXODUS_LIB.ex_get_ids(
                self.fileId,
                ex_entity_type('EX_NODE_SET'),
                byref(self.nodeSetIds))

    # --------------------------------------------------------------------

    def __ex_get_node_set_param(self, nodeSetId):
        node_set_id = c_longlong(nodeSetId)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            num_set_nodes = c_longlong(0)
            num_set_dist_facts = c_longlong(0)
        else:
            num_set_nodes = c_int(0)
            num_set_dist_facts = c_int(0)
        EXODUS_LIB.ex_get_node_set_param(
            self.fileId,
            node_set_id,
            byref(num_set_nodes),
            byref(num_set_dist_facts))
        return (int(num_set_nodes.value), int(num_set_dist_facts.value))

    # --------------------------------------------------------------------

    def __ex_put_node_set_param(self, nodeSetId, numNodes, numDistFacts):
        node_set_id = c_longlong(nodeSetId)
        num_set_nodes = c_longlong(numNodes)
        num_set_dist_facts = c_longlong(numDistFacts)
        EXODUS_LIB.ex_put_node_set_param(
            self.fileId,
            node_set_id,
            num_set_nodes,
            num_set_dist_facts)

    # --------------------------------------------------------------------

    def __ex_get_node_set(self, nodeSetId):
        node_set_id = c_longlong(nodeSetId)
        num_node_set_nodes = self.__ex_get_node_set_param(nodeSetId)[0]
        if num_node_set_nodes == 0:
            return []
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            set_nodes = (c_longlong * num_node_set_nodes)()
        else:
            set_nodes = (c_int * num_node_set_nodes)()
        EXODUS_LIB.ex_get_node_set(self.fileId, node_set_id, byref(set_nodes))
        return set_nodes

    # --------------------------------------------------------------------

    def __ex_put_node_set(self, nodeSetId, nodeSetNodes):
        node_set_id = c_longlong(nodeSetId)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            node_set_nodes = (c_longlong * len(nodeSetNodes))()
            for i in range(len(nodeSetNodes)):
                node_set_nodes[i] = c_longlong(nodeSetNodes[i])
        else:
            node_set_nodes = (c_int * len(nodeSetNodes))()
            for i in range(len(nodeSetNodes)):
                node_set_nodes[i] = c_int(nodeSetNodes[i])
        EXODUS_LIB.ex_put_node_set(self.fileId, node_set_id, node_set_nodes)

    # --------------------------------------------------------------------

    def __ex_get_node_set_dist_fact(self, nodeSetId):
        node_set_id = c_longlong(nodeSetId)
        num_node_set_nodes = self.__ex_get_node_set_param(nodeSetId)[0]
        set_dfs = (c_double * num_node_set_nodes)()
        EXODUS_LIB.ex_get_node_set_dist_fact(
            self.fileId, node_set_id, byref(set_dfs))
        return set_dfs

    # --------------------------------------------------------------------

    def __ex_put_node_set_dist_fact(self, nodeSetId, nodeSetDistFact):
        node_set_id = c_longlong(nodeSetId)
        node_set_dist_fact = (c_double * len(nodeSetDistFact))()
        for i in range(len(nodeSetDistFact)):
            node_set_dist_fact[i] = c_double(nodeSetDistFact[i])
        EXODUS_LIB.ex_put_node_set_dist_fact(
            self.fileId, node_set_id, node_set_dist_fact)

    # --------------------------------------------------------------------

    def __ex_get_nset_var(self, timeStep, varId, id):
        step = c_int(timeStep)
        var_id = c_int(varId)
        node_set_id = c_longlong(id)
        (numNodeInSet, numDistFactInSet) = self.__ex_get_node_set_param(id)
        num_node_in_set = c_longlong(numNodeInSet)
        ns_var_vals = (c_double * numNodeInSet)()
        EXODUS_LIB.ex_get_nset_var(
            self.fileId,
            step,
            var_id,
            node_set_id,
            num_node_in_set,
            ns_var_vals)
        return list(ns_var_vals)

    # --------------------------------------------------------------------

    def __ex_get_nset_var_tab(self):
        self.__ex_get_node_set_ids()
        node_set_count = c_int(len(self.nodeSetIds))
        variable_count = self.__ex_get_var_param("m")
        truth_table = (c_int * (node_set_count.value * variable_count.value))()
        EXODUS_LIB.ex_get_nset_var_tab(self.fileId,
                                       node_set_count,
                                       variable_count,
                                       byref(truth_table))
        truthTab = []
        for val in truth_table:
            if val:
                truthTab.append(True)
            else:
                truthTab.append(False)
        return truthTab

    # --------------------------------------------------------------------

    def __ex_put_nset_var_tab(self, truthTab):
        self.__ex_get_node_set_ids()
        num_blks = c_int(len(self.nodeSetIds))
        num_vars = self.__ex_get_var_param("m")
        truth_tab = (c_int * (num_blks.value * num_vars.value))()
        for i in xrange(len(truthTab)):
            boolVal = truthTab[i]
            if boolVal:
                truth_tab[i] = c_int(1)
            else:
                truth_tab[i] = c_int(0)
        EXODUS_LIB.ex_put_nset_var_tab(
            self.fileId, num_blks, num_vars, truth_tab)
        return True

    # --------------------------------------------------------------------

    def __ex_put_nset_var(self, timeStep, varId, id, values):
        step = c_int(timeStep)
        var_id = c_int(varId)
        node_set_id = c_longlong(id)
        (numNodeInSet, numDistFactInSet) = self.__ex_get_node_set_param(id)
        num_node_in_set = c_longlong(numNodeInSet)
        ns_var_vals = (c_double * numNodeInSet)()
        for i in range(numNodeInSet):
            ns_var_vals[i] = float(values[i])
        EXODUS_LIB.ex_put_nset_var(
            self.fileId,
            step,
            var_id,
            node_set_id,
            num_node_in_set,
            ns_var_vals)
        return True

    # --------------------------------------------------------------------

    def __ex_get_coord(self):
        self.coordsX = (c_double * self.numNodes.value)()
        self.coordsY = (c_double * self.numNodes.value)()
        self.coordsZ = (c_double * self.numNodes.value)()
        EXODUS_LIB.ex_get_coord(
            self.fileId,
            byref(self.coordsX),
            byref(self.coordsY),
            byref(self.coordsZ))

    # --------------------------------------------------------------------

    def __ex_put_coord(self, xCoords, yCoords, zCoords):
        self.coordsX = (c_double * self.numNodes.value)()
        self.coordsY = (c_double * self.numNodes.value)()
        self.coordsZ = (c_double * self.numNodes.value)()
        for i in range(self.numNodes.value):
            self.coordsX[i] = float(xCoords[i])
            self.coordsY[i] = float(yCoords[i])
            self.coordsZ[i] = float(zCoords[i])
        EXODUS_LIB.ex_put_coord(
            self.fileId,
            byref(self.coordsX),
            byref(self.coordsY),
            byref(self.coordsZ))

    # --------------------------------------------------------------------

    def __ex_get_n_coord(self, startNodeId, numNodes):
        start_node_num = c_longlong(startNodeId)
        num_nodes = c_longlong(numNodes)
        coordsX = (c_double * numNodes)()
        coordsY = (c_double * numNodes)()
        coordsZ = (c_double * numNodes)()
        EXODUS_LIB.ex_get_n_coord(
            self.fileId,
            start_node_num,
            num_nodes,
            byref(coordsX),
            byref(coordsY),
            byref(coordsZ))
        return list(coordsX), list(coordsY), list(coordsZ)

    # --------------------------------------------------------------------

    def __ex_get_id_map(self, objType, inqType):
        obj_type = c_int(objType)
        num_objs = c_int(self.__ex_inquire_int(inqType))
        numObjs = num_objs.value
        id_map = []
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_IDS_INT64_API:
            id_map = (c_longlong * numObjs)()
        else:
            id_map = (c_int * numObjs)()
        EXODUS_LIB.ex_get_id_map(self.fileId, obj_type, byref(id_map))
        idMap = []
        for i in xrange(numObjs):
            idMap.append(id_map[i])
        return idMap

    # --------------------------------------------------------------------

    def __ex_put_id_map(self, objType, inqType, map):
        obj_type = c_int(objType)
        num_objs = c_int(self.__ex_inquire_int(inqType))
        numObjs = num_objs.value
        assert numObjs == len(map)
        id_map = []
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_IDS_INT64_API:
            id_map = (c_longlong * numObjs)()
            for i in xrange(numObjs):
                id_map[i] = c_longlong(map[i])
        else:
            id_map = (c_int * numObjs)()
            for i in xrange(numObjs):
                id_map[i] = c_int(map[i])
        EXODUS_LIB.ex_put_id_map(self.fileId, obj_type, byref(id_map))
        return True

    # --------------------------------------------------------------------

    def __ex_get_elem_num_map(self):
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_MAPS_INT64_API:
            elemNumMap = (c_longlong * self.numElem.value)()
        else:
            elemNumMap = (c_int * self.numElem.value)()
        EXODUS_LIB.ex_get_elem_num_map(self.fileId, byref(elemNumMap))
        return elemNumMap

    # --------------------------------------------------------------------

    def __ex_get_node_num_map(self):
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_MAPS_INT64_API:
            nodeNumMap = (c_longlong * self.numNodes.value)()
        else:
            nodeNumMap = (c_int * self.numNodes.value)()
        EXODUS_LIB.ex_get_node_num_map(self.fileId, byref(nodeNumMap))
        return nodeNumMap

    # --------------------------------------------------------------------

    def __ex_get_elem_order_map(self):
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_MAPS_INT64_API:
            elemOrderMap = (c_longlong * self.numElem.value)()
        else:
            elemOrderMap = (c_int * self.numElem.value)()
        EXODUS_LIB.ex_get_map(self.fileId, byref(elemOrderMap))
        return elemOrderMap

    # --------------------------------------------------------------------

    def __ex_get_elem_block(self, id):
        elem_block_id = c_longlong(id)
        elem_type = create_string_buffer(MAX_STR_LENGTH + 1)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            num_elem_this_blk = c_longlong(0)
            num_nodes_per_elem = c_longlong(0)
            num_edges_per_elem = c_longlong(0)
            num_faces_per_elem = c_longlong(0)
            num_attr = c_longlong(0)
        else:
            num_elem_this_blk = c_int(0)
            num_nodes_per_elem = c_int(0)
            num_edges_per_elem = c_int(0)
            num_faces_per_elem = c_int(0)
            num_attr = c_int(0)
        EXODUS_LIB.ex_get_block(
            self.fileId,
            ex_entity_type('EX_ELEM_BLOCK'),
            elem_block_id,
            elem_type,
            byref(num_elem_this_blk),
            byref(num_nodes_per_elem),
            byref(num_edges_per_elem),
            byref(num_faces_per_elem),
            byref(num_attr))
        return elem_type, num_elem_this_blk, num_nodes_per_elem, num_attr

    # --------------------------------------------------------------------

    def __ex_put_elem_block(
            self,
            id,
            eType,
            numElems,
            numNodesPerElem,
            numAttrsPerElem):
        elem_block_id = c_longlong(id)
        elem_type = create_string_buffer(eType.upper(), MAX_NAME_LENGTH + 1)
        num_elem_this_blk = c_longlong(numElems)
        num_nodes_per_elem = c_longlong(numNodesPerElem)
        num_attr = c_longlong(numAttrsPerElem)
        EXODUS_LIB.ex_put_elem_block(self.fileId, elem_block_id, elem_type,
                                     num_elem_this_blk, num_nodes_per_elem,
                                     num_attr)

    # --------------------------------------------------------------------

    def __ex_get_elem_conn(self, id):
        (elem_type, num_elem_this_blk, num_nodes_per_elem,
         num_attr) = self.__ex_get_elem_block(id)
        elem_block_id = c_longlong(id)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            elem_block_connectivity = (
                c_longlong * (num_elem_this_blk.value * num_nodes_per_elem.value))()
        else:
            elem_block_connectivity = (
                c_int * (num_elem_this_blk.value * num_nodes_per_elem.value))()
        EXODUS_LIB.ex_get_elem_conn(
            self.fileId,
            elem_block_id,
            byref(elem_block_connectivity))
        return (elem_block_connectivity, num_elem_this_blk, num_nodes_per_elem)

    # --------------------------------------------------------------------

    def __ex_put_elem_conn(self, id, connectivity):
        (elem_type, num_elem_this_blk, num_nodes_per_elem,
         num_attr) = self.__ex_get_elem_block(id)
        elem_block_id = c_longlong(id)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            elem_block_connectivity = (
                c_longlong * (num_elem_this_blk.value * num_nodes_per_elem.value))()
            for i in range(num_elem_this_blk.value * num_nodes_per_elem.value):
                elem_block_connectivity[i] = c_longlong(connectivity[i])
        else:
            elem_block_connectivity = (
                c_int * (num_elem_this_blk.value * num_nodes_per_elem.value))()
            for i in range(num_elem_this_blk.value * num_nodes_per_elem.value):
                elem_block_connectivity[i] = c_int(connectivity[i])
        EXODUS_LIB.ex_put_elem_conn(
            self.fileId,
            elem_block_id,
            elem_block_connectivity)

    # --------------------------------------------------------------------

    def __ex_put_elem_attr(self, elemBlkID, Attr):
        elem_blk_id = c_longlong(elemBlkID)
        attrib = (c_double * len(Attr))()
        for i in range(len(Attr)):
            attrib[i] = c_double(Attr[i])
        EXODUS_LIB.ex_put_attr(
            self.fileId,
            ex_entity_type('EX_ELEM_BLOCK'),
            elem_blk_id,
            attrib)

    # --------------------------------------------------------------------

    def __ex_get_elem_attr(self, elemBlkID):
        elem_blk_id = c_longlong(elemBlkID)
        numAttrThisBlk = self.num_attr(elemBlkID)
        numElemsThisBlk = self.num_elems_in_blk(elemBlkID)
        totalAttr = numAttrThisBlk * numElemsThisBlk
        attrib = (c_double * totalAttr)()
        EXODUS_LIB.ex_get_attr(
            self.fileId,
            ex_entity_type('EX_ELEM_BLOCK'),
            elem_blk_id,
            byref(attrib))
        return attrib

    # --------------------------------------------------------------------

    def __ex_get_var_param(self, varChar):
        assert varChar.lower() in 'ngems'
        var_char = c_char(varChar)
        num_vars = c_int()
        EXODUS_LIB.ex_get_var_param(
            self.fileId, byref(var_char), byref(num_vars))
        return num_vars

    # --------------------------------------------------------------------

    def __ex_get_var_names(self, varChar):
        assert varChar.lower() in 'ngems'
        var_char = c_char(varChar)
        num_vars = self.__ex_get_var_param(varChar)
        var_name_ptrs = (
            POINTER(c_char * (MAX_NAME_LENGTH + 1)) * num_vars.value)()
        for i in range(num_vars.value):
            var_name_ptrs[i] = pointer(
                create_string_buffer(
                    MAX_NAME_LENGTH + 1))
        EXODUS_LIB.ex_get_var_names(
            self.fileId,
            byref(var_char),
            num_vars,
            byref(var_name_ptrs))
        var_names = []
        for vnp in var_name_ptrs:
            var_names.append(vnp.contents.value)
        return var_names

    # --------------------------------------------------------------------

    def __ex_get_elem_var_tab(self):
        self.__ex_get_elem_blk_ids()
        num_blks = c_int(len(self.elemBlkIds))
        num_vars = self.__ex_get_var_param("e")
        truth_tab = (c_int * (num_blks.value * num_vars.value))()
        EXODUS_LIB.ex_get_elem_var_tab(
            self.fileId, num_blks, num_vars, byref(truth_tab))
        truthTab = []
        for val in truth_tab:
            if val:
                truthTab.append(True)
            else:
                truthTab.append(False)
        return truthTab

    # --------------------------------------------------------------------

    def __ex_put_elem_var_tab(self, truthTab):
        self.__ex_get_elem_blk_ids()
        num_blks = c_int(len(self.elemBlkIds))
        num_vars = self.__ex_get_var_param("e")
        truth_tab = (c_int * (num_blks.value * num_vars.value))()
        for i in xrange(len(truthTab)):
            boolVal = truthTab[i]
            if boolVal:
                truth_tab[i] = c_int(1)
            else:
                truth_tab[i] = c_int(0)
        EXODUS_LIB.ex_put_elem_var_tab(
            self.fileId, num_blks, num_vars, truth_tab)
        return True

    # --------------------------------------------------------------------

    def __ex_get_var(self, timeStep, varType, varId, blkId, numValues):
        step = c_int(timeStep)
        var_type = c_int(varType)
        var_id = c_int(varId)
        block_id = c_longlong(blkId)
        num_values = c_longlong(numValues)
        var_vals = (c_double * num_values.value)()
        EXODUS_LIB.ex_get_var(
            self.fileId,
            step,
            var_type,
            var_id,
            block_id,
            num_values,
            var_vals)
        return var_vals

    # --------------------------------------------------------------------

    def __ex_put_var(self, timeStep, varType, varId, blkId, numValues, values):
        step = c_int(timeStep)
        var_type = c_int(varType)
        var_id = c_int(varId)
        block_id = c_longlong(blkId)
        num_values = c_longlong(numValues)
        var_vals = (c_double * num_values.value)()
        for i in range(num_values.value):
            var_vals[i] = float(values[i])
        EXODUS_LIB.ex_put_var(
            self.fileId,
            step,
            var_type,
            var_id,
            block_id,
            num_values,
            var_vals)
        return True

    # --------------------------------------------------------------------

    def __ex_get_side_set_node_list_len(self, id):
        side_set_id = c_longlong(id)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            side_set_node_list_len = c_longlong(0)
        else:
            side_set_node_list_len = c_int(0)
        EXODUS_LIB.ex_get_side_set_node_list_len(
            self.fileId, side_set_id, byref(side_set_node_list_len))
        return side_set_node_list_len

    # --------------------------------------------------------------------

    def __ex_get_side_set_param(self, id):
        side_set_id = c_longlong(id)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            num_side_in_set = c_longlong(0)
            num_dist_fact_in_set = c_longlong(0)
        else:
            num_side_in_set = c_int(0)
            num_dist_fact_in_set = c_int(0)
        EXODUS_LIB.ex_get_side_set_param(
            self.fileId,
            side_set_id,
            byref(num_side_in_set),
            byref(num_dist_fact_in_set))
        return (int(num_side_in_set.value), int(num_dist_fact_in_set.value))

    # --------------------------------------------------------------------

    def __ex_put_side_set_param(self, id, numSides, numDistFacts):
        side_set_id = c_longlong(id)
        num_side_in_set = c_longlong(numSides)
        num_dist_fact_in_set = c_longlong(numDistFacts)
        EXODUS_LIB.ex_put_side_set_param(
            self.fileId,
            side_set_id,
            num_side_in_set,
            num_dist_fact_in_set)
        return True

    # --------------------------------------------------------------------

    def __ex_get_side_set(self, sideSetId):
        side_set_id = c_longlong(sideSetId)
        (num_side_in_set, num_dist_fact_in_set) = self.__ex_get_side_set_param(sideSetId)
        if num_side_in_set == 0:
            return ([], [])
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            side_set_elem_list = (c_longlong * num_side_in_set)()
            side_set_side_list = (c_longlong * num_side_in_set)()
        else:
            side_set_elem_list = (c_int * num_side_in_set)()
            side_set_side_list = (c_int * num_side_in_set)()
        EXODUS_LIB.ex_get_side_set(self.fileId, side_set_id,
                                   byref(side_set_elem_list),
                                   byref(side_set_side_list))
        return (side_set_elem_list, side_set_side_list)

    # --------------------------------------------------------------------

    def __ex_put_side_set(self, id, sideSetElements, sideSetSides):
        side_set_id = c_longlong(id)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            side_set_elem_list = (c_longlong * len(sideSetElements))()
            side_set_side_list = (c_longlong * len(sideSetSides))()
            for i in range(len(sideSetElements)):
                side_set_elem_list[i] = c_longlong(sideSetElements[i])
                side_set_side_list[i] = c_longlong(sideSetSides[i])
        else:
            side_set_elem_list = (c_int * len(sideSetElements))()
            side_set_side_list = (c_int * len(sideSetSides))()
            for i in range(len(sideSetElements)):
                side_set_elem_list[i] = c_int(sideSetElements[i])
                side_set_side_list[i] = c_int(sideSetSides[i])
        EXODUS_LIB.ex_put_side_set(
            self.fileId,
            side_set_id,
            side_set_elem_list,
            side_set_side_list)
        return True

    # --------------------------------------------------------------------

    def __ex_get_sset_var_tab(self):
        self.__ex_get_side_set_ids()
        side_set_count = c_int(len(self.sideSetIds))
        variable_count = self.__ex_get_var_param("s")
        truth_table = (c_int * (side_set_count.value * variable_count.value))()
        EXODUS_LIB.ex_get_sset_var_tab(self.fileId,
                                       side_set_count,
                                       variable_count,
                                       byref(truth_table))
        truthTab = []
        for val in truth_table:
            if val:
                truthTab.append(True)
            else:
                truthTab.append(False)
        return truthTab

    # --------------------------------------------------------------------

    def __ex_put_sset_var_tab(self, truthTab):
        self.__ex_get_side_set_ids()
        num_blks = c_int(len(self.sideSetIds))
        num_vars = self.__ex_get_var_param("s")
        truth_tab = (c_int * (num_blks.value * num_vars.value))()
        for i in xrange(len(truthTab)):
            boolVal = truthTab[i]
            if boolVal:
                truth_tab[i] = c_int(1)
            else:
                truth_tab[i] = c_int(0)
        EXODUS_LIB.ex_put_sset_var_tab(
            self.fileId, num_blks, num_vars, truth_tab)
        return True

    # --------------------------------------------------------------------

    def __ex_get_side_set_dist_fact(self, sideSetId):
        side_set_id = c_longlong(sideSetId)
        side_set_node_list_len = self.__ex_get_side_set_node_list_len(
            sideSetId)
        set_dfs = (c_double * side_set_node_list_len.value)()
        EXODUS_LIB.ex_get_side_set_dist_fact(
            self.fileId, side_set_id, byref(set_dfs))
        return set_dfs

    # --------------------------------------------------------------------

    def __ex_put_side_set_dist_fact(self, sideSetId, sideSetDistFact):
        side_set_id = c_longlong(sideSetId)
        side_set_dist_fact = (c_double * len(sideSetDistFact))()
        for i in range(len(sideSetDistFact)):
            side_set_dist_fact[i] = c_double(sideSetDistFact[i])
        EXODUS_LIB.ex_put_side_set_dist_fact(
            self.fileId, side_set_id, side_set_dist_fact)

    # --------------------------------------------------------------------

    def __ex_get_side_set_node_list(self, id):
        side_set_id = c_longlong(id)
        side_set_node_list_len = self.__ex_get_side_set_node_list_len(id)
        (num_side_in_set, num_dist_fact_in_set) = self.__ex_get_side_set_param(id)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_BULK_INT64_API:
            side_set_node_cnt_list = (c_longlong * num_side_in_set)()
            side_set_node_list = (c_longlong * side_set_node_list_len.value)()
        else:
            side_set_node_cnt_list = (c_int * num_side_in_set)()
            side_set_node_list = (c_int * side_set_node_list_len.value)()
        EXODUS_LIB.ex_get_side_set_node_list(self.fileId, side_set_id,
                                             byref(side_set_node_cnt_list),
                                             byref(side_set_node_list))
        return (side_set_node_cnt_list, side_set_node_list)

    # --------------------------------------------------------------------

    def __ex_get_sset_var(self, timeStep, varId, id):
        step = c_int(timeStep)
        var_id = c_int(varId)
        side_set_id = c_longlong(id)
        (numSideInSet, numDistFactInSet) = self.__ex_get_side_set_param(id)
        ss_var_vals = (c_double * numSideInSet)()
        num_side_in_set = c_longlong(numSideInSet)
        EXODUS_LIB.ex_get_sset_var(
            self.fileId,
            step,
            var_id,
            side_set_id,
            num_side_in_set,
            ss_var_vals)
        return ss_var_vals

    # --------------------------------------------------------------------

    def __ex_put_sset_var(self, timeStep, varId, id, values):
        step = c_int(timeStep)
        var_id = c_int(varId)
        side_set_id = c_longlong(id)
        (numSideInSet, numDistFactInSet) = self.__ex_get_side_set_param(id)
        num_side_in_set = c_longlong(numSideInSet)
        ss_var_vals = (c_double * numSideInSet)()
        for i in range(numSideInSet):
            ss_var_vals[i] = float(values[i])
        EXODUS_LIB.ex_put_sset_var(
            self.fileId,
            step,
            var_id,
            side_set_id,
            num_side_in_set,
            ss_var_vals)
        return True

    # --------------------------------------------------------------------

    def __ex_get_variable_param(self, varType):
        var_type = c_int(varType)
        num_vars = c_int(0)
        EXODUS_LIB.ex_get_variable_param(
            self.fileId, var_type, byref(num_vars))
        return num_vars

    # --------------------------------------------------------------------

    def __ex_put_variable_param(self, varType, numVars):
        var_type = c_int(varType)
        num_vars = c_int(numVars)
        current_num = self.__ex_get_variable_param(varType)
        if current_num.value == num_vars.value:
            # print "value already set"
            return True
        errorInt = EXODUS_LIB.ex_put_variable_param(
            self.fileId, var_type, num_vars)
        if errorInt != 0:
            print("ERROR code =", errorInt)
            raise Exception(
                "ERROR: ex_put_variable_param had problems."
                " This can only be called once per varType.")
        return True

    # --------------------------------------------------------------------

    def __ex_get_variable_name(self, varType, varId):
        var_type = c_int(varType)
        var_id = c_int(varId)
        name = create_string_buffer(MAX_NAME_LENGTH + 1)
        EXODUS_LIB.ex_get_variable_name(self.fileId, var_type, var_id, name)
        return name

    # --------------------------------------------------------------------

    def __ex_put_variable_name(self, varType, varId, varName):
        var_type = c_int(varType)
        var_id = c_int(varId)
        name = create_string_buffer(varName, MAX_NAME_LENGTH + 1)
        EXODUS_LIB.ex_put_variable_name(self.fileId, var_type, var_id, name)
        return True

    # --------------------------------------------------------------------

    def __ex_get_elem_attr_names(self, blkId):
        object_id = c_int(blkId)
        num_attr = c_int(self.num_attr(blkId))
        len_name = self.__ex_inquire_int(ex_inquiry("EX_INQ_MAX_READ_NAME_LENGTH"))
        attr_name_ptrs = (POINTER(c_char * (len_name + 1)) * num_attr.value)()
        for i in range(num_attr.value):
            attr_name_ptrs[i] = pointer(create_string_buffer(len_name + 1))
        EXODUS_LIB.ex_get_elem_attr_names(
            self.fileId, object_id, byref(attr_name_ptrs))
        attr_names = []
        for cnp in attr_name_ptrs:
            attr_names.append(cnp.contents.value)
        return attr_names

    # --------------------------------------------------------------------

    def __ex_put_elem_attr_names(self, blkId, varNames):
        object_id = c_int(blkId)
        num_attr = c_int(self.num_attr(blkId))
        len_name = self.__ex_inquire_int(ex_inquiry("EX_INQ_MAX_READ_NAME_LENGTH"))
        attr_name_ptrs = (POINTER(c_char * (len_name + 1)) * num_attr.value)()
        assert len(varNames) == num_attr.value
        for i in range(num_attr.value):
            attr_name_ptrs[i] = pointer(
                create_string_buffer(
                    varNames[i], len_name + 1))
        EXODUS_LIB.ex_put_elem_attr_names(
            self.fileId, object_id, byref(attr_name_ptrs))
        return True

    # --------------------------------------------------------------------

    def __ex_get_prop_names(self, varType, inqType):
        var_type = c_int(varType)
        num_props = c_int(self.__ex_inquire_int(ex_inquiry(inqType)))
        prop_name_ptrs = (
            POINTER(c_char * (MAX_STR_LENGTH + 1)) * num_props.value)()
        for i in range(num_props.value):
            prop_name_ptrs[i] = pointer(
                create_string_buffer(
                    MAX_STR_LENGTH + 1))
        EXODUS_LIB.ex_get_prop_names(
            self.fileId, var_type, byref(prop_name_ptrs))
        prop_names = []
        for cnp in prop_name_ptrs:
            prop_names.append(cnp.contents.value)
        return prop_names

    # --------------------------------------------------------------------

    def __ex_get_prop(self, objType, objId, propName):
        obj_type = c_int(objType)
        obj_id = c_longlong(objId)
        prop_name = create_string_buffer(propName, MAX_STR_LENGTH + 1)
        if EXODUS_LIB.ex_int64_status(self.fileId) & EX_IDS_INT64_API:
            prop_val = c_longlong(0)
        else:
            prop_val = c_int(0)
        EXODUS_LIB.ex_get_prop(
            self.fileId,
            obj_type,
            obj_id,
            byref(prop_name),
            byref(prop_val))
        return prop_val.value

    # --------------------------------------------------------------------

    def __ex_put_prop(self, objType, objId, propName, propVal):
        obj_type = c_int(objType)
        obj_id = c_longlong(objId)
        prop_name = create_string_buffer(propName, MAX_STR_LENGTH + 1)
        prop_val = c_longlong(propVal)
        EXODUS_LIB.ex_put_prop(
            self.fileId,
            obj_type,
            obj_id,
            byref(prop_name),
            prop_val)
        return True

    # --------------------------------------------------------------------

    def __ex_update(self):
        EXODUS_LIB.ex_update(self.fileId)
        return True

    # --------------------------------------------------------------------
# Utility Functions
# --------------------------------------------------------------------


def collectElemConnectivity(exodusHandle, connectivity):
    """
      This function generates a list of lists that represent the element connectivity.

      Usage:

      exodusHandle = exodus("file.g", "r")
      connectivity = []
      collectElemConnectivity(exodusHandle, connectivity)

      exodusHandle.close()
    """

    if not isinstance(connectivity, list):
        raise Exception(
            "ERROR: connectivity is not a list in call to collectElemConnectivity().")
    if connectivity:
        raise Exception(
            "ERROR: connectivity is not empty in call to collectElemConnectivity().")

    blockIds = exodusHandle.get_elem_blk_ids()
    for blId in blockIds:
        (elem_block_conn, num_elem, num_nodes) = exodusHandle.get_elem_connectivity(blId)
        for k in range(num_elem):
            i = k * num_nodes
            j = i + num_nodes
            local_elem_conn = elem_block_conn[i:j]
            connectivity.append(local_elem_conn)

# --------------------------------------------------------------------


def collectLocalNodeToLocalElems(
        exodusHandle,
        connectivity,
        localNodeToLocalElems):
    """
      This function generates a list of lists to go from local node id
      to local elem id.

      Usage:

      exodusHandle = exodus("file.g", "r")
      connectivity = [] ## If this is not empty it will assume it is already filled.
      localNodeToLocalElems = []
      collectLocalNodeToLocalElems(exodusHandle, connectivity, localNodeToLocalElems)

      exodusHandle.close()
    """

    if not isinstance(connectivity, list):
        raise Exception(
            "ERROR: connectivity is not a list in call to collectLocalNodeToLocalElems().")
    if not isinstance(localNodeToLocalElems, list):
        raise Exception(
            "ERROR: localNodeToLocalElems is not a list in call to collectLocalNodeToLocalElems().")
    if localNodeToLocalElems:
        raise Exception(
            "ERROR: localNodeToLocalElems is not empty in call to collectLocalNodeToLocalElems().")

    if not connectivity:
        collectElemConnectivity(exodusHandle, connectivity)

    numNodes = exodusHandle.num_nodes()
    for i in range(numNodes + 1):
        localNodeToLocalElems.append([])
    localElemId = 0
    for local_elem_conn in connectivity:
        for n in local_elem_conn:
            localNodeToLocalElems[n].append(localElemId)
        localElemId = localElemId + 1

# --------------------------------------------------------------------


def collectLocalElemToLocalElems(
        exodusHandle,
        connectivity,
        localNodeToLocalElems,
        localElemToLocalElems):
    """
      This function generates a list of lists to go from local elem id
      to connected local elem ids.

      Usage:

      exodusHandle = exodus("file.g", "r")
      connectivity = [] ## If this is not empty it will assume it is already filled.
      localNodeToLocalElems = [] ## If this is not empty it will assume it is already filled.
      localElemToLocalElems = []
      collectLocalElemToLocalElems(exodusHandle, connectivity, localNodeToLocalElems,
                                   localElemToLocalElems)

      exodusHandle.close()
    """

    if not isinstance(connectivity, list):
        raise Exception(
            "ERROR: connectivity is not a list in call to collectLocalElemToLocalElems().")
    if not isinstance(localNodeToLocalElems, list):
        raise Exception(
            "ERROR: localNodeToLocalElems is not a list in call to collectLocalElemToLocalElems().")
    if not isinstance(localElemToLocalElems, list):
        raise Exception(
            "ERROR: localElemToLocalElems is not a list in call to collectLocalElemToLocalElems().")
    if localElemToLocalElems:
        raise Exception(
            "ERROR: localElemToLocalElems is not empty in call to collectLocalElemToLocalElems().")

    if not connectivity:
        collectElemConnectivity(exodusHandle, connectivity)
    if not localNodeToLocalElems:
        collectLocalNodeToLocalElems(
            exodusHandle, connectivity, localNodeToLocalElems)

    numElems = exodusHandle.num_elems()
    for i in range(numElems):
        localElemToLocalElems.append([])
    for localElemId in range(numElems):
        nodeList = list(connectivity[localElemId])
        newConnectedElems = []
        for n in nodeList:
            for elem in localNodeToLocalElems[n]:
                newConnectedElems.append(elem)
        localElemToLocalElems[localElemId] = list(set(newConnectedElems))

# --------------------------------------------------------------------


def copy_mesh(fromFileName, toFileName, exoFromObj=None,
              additionalElementAttributes=[], array_type='ctype'):
    """
    Copies the mesh data from an existing exodus database to a new exodus
    database.

    Parameters
    ----------
    fromFileName : string
        File name of the exodus mesh to be copied
    toFileName : string
        File name of the new exodus mesh
    exoFromObj : exodus object, optional
        Exodus object to be copied from.  If an exodus object is supplied, the
        fromFileName string will be ignored.
    additionalElementAttributes : list
        list of element attribute names to add to all blocks or tuples
        ( name, blkIds ) where name is the element attribute to add and blkIds is
        a list of blkIds to add it to.
    array_type : 'ctype' | 'numpy'
        Specifies whether arrays will be imported and copied as ctype or numpy
        arrays.  (This option should make no difference to the user, but it can
        be used by developers to test whether the commands within this function
        handle both array types correctly.)

    Returns
    -------
    exo_to : exodus object
        New exodus mesh

    Notes
    -----
    This function also allows one to add new element attributes during the copy
    process.  The number of element attributes is permanently set when the
    block is created, meaning new element attributes can only be added to an
    existing mesh by copying it to a new mesh.  The values of the element
    attributes are set to their defaults so that the user can populate them
    later.
    """
    debugPrint = False

    # If the user did not supply a exodus object to copy from, attempt to read an
    # exodus database with the name "fromFileName"
    if exoFromObj is None:
        exoFrom = exodus(fromFileName, "r", array_type=array_type)
    else:
        exoFrom = exoFromObj

    if os.path.isfile(toFileName):
        raise Exception(
            "ERROR: ",
            toFileName,
            " file already exists cowardly exiting instead of overwriting in call to copy_mesh().")

    title = exoFrom.title()
    ex_pars = ex_init_params(num_dim=exoFrom.num_dimensions(),
                             num_nodes=exoFrom.num_nodes(),
                             num_elem=exoFrom.num_elems(),
                             num_elem_blk=exoFrom.num_blks(),
                             num_node_sets=exoFrom.num_node_sets(),
                             num_side_sets=exoFrom.num_side_sets())

    exo_to = exodus(toFileName, mode="w", array_type=array_type,
                    title=title, init_params=ex_pars)

    if debugPrint:
        print("Transfer QA records")
    qaRecords = exoFrom.get_qa_records()
    exo_to.put_qa_records(qaRecords)

    if debugPrint:
        print("Transfer Nodal Coordinates and Names")
    exo_to.put_coord_names(exoFrom.get_coord_names())
    (xCoords, yCoords, zCoords) = exoFrom.get_coords()
    exo_to.put_coords(xCoords, yCoords, zCoords)

    if debugPrint:
        print("Transfer Node Id Map")
    nodeIdMap = exoFrom.get_node_id_map()
    exo_to.put_node_id_map(nodeIdMap)

    if debugPrint:
        print("Construct mapping from block ID to element attribute data")
    # The exodus library does not provide a way to add only new element
    # attributes, so we must collect both the new and the old element
    # attributes
    e_attr_names = dict()
    e_attr_vals = dict()
    # Collect the old element attribute names and the number of elements in each
    # block
    blk_ids = exoFrom.get_elem_blk_ids()
    blk_num_elem = dict()
    for blk_id in blk_ids:
        (elemType, numElem, nodesPerElem, numAttr) = exoFrom.elem_blk_info(blk_id)
        e_attr_names[blk_id] = []
        e_attr_vals[blk_id] = []
        if numAttr > 0:
            e_attr_names[blk_id].extend(
                exoFrom.get_element_attribute_names(blk_id))
            e_attr_vals[blk_id].extend(exoFrom.get_elem_attr(blk_id))
        blk_num_elem[blk_id] = numElem
    # Collect the new element attribute names
    # (The new names are mapped from "attribute name" to "list of block IDs that
    # contain that attribute".  We need to have them be mapped as "block ID" to
    # "list of attribute names contained in that block".)
    for item in additionalElementAttributes:
        if isinstance(item, tuple):
            e_attr_name = item[0]
            e_attr_blk_ids = item[1]
        elif isinstance(item, str):
            e_attr_name = item
            e_attr_blk_ids = blk_ids
        else:
            print(
                "Warning additional element attribute item " +
                item +
                " is not right type to add.")
            print("should be a string or tuple, skipping")
        for blk_id in e_attr_blk_ids:
            if blk_id in blk_ids:
                e_attr_names[blk_id].append(e_attr_name)
                # Concatenate all element attribute values into a single big list,
                # because that is format required by exo.put_elem_attr().
                e_attr_vals[blk_id].extend([0.0] * blk_num_elem[blk_id])

    if debugPrint:
        print("Transfer Element Data")
    blkIds = exoFrom.get_elem_blk_ids()
    for blkId in blkIds:
        (elemType, numElem, nodesPerElem, oldnumAttr) = exoFrom.elem_blk_info(blkId)
        numAttr = len(e_attr_names[blkId])
        exo_to.put_elem_blk_info(
            blkId,
            elemType,
            numElem,
            nodesPerElem,
            numAttr)
        (connectivity, numElem, nodesPerElem) = exoFrom.get_elem_connectivity(blkId)
        exo_to.put_elem_connectivity(blkId, connectivity)
        if numAttr > 0:
            exo_to.put_element_attribute_names(blkId, e_attr_names[blkId])
            exo_to.put_elem_attr(blkId, e_attr_vals[blkId])
        elemProps = exoFrom.get_element_property_names()
        for elemProp in elemProps:
            propVal = exoFrom.get_element_property_value(blkId, elemProp)
            if elemProp == "ID" and propVal == blkId:
                continue
            else:
                exo_to.put_element_property_value(blkId, elemProp, propVal)
        blockName = exoFrom.get_elem_blk_name(blkId)
        exo_to.put_elem_blk_name(blkId, blockName)

    if debugPrint:
        print("Transfer Element Id Map")
    elemIdMap = exoFrom.get_elem_id_map()
    exo_to.put_elem_id_map(elemIdMap)

    if debugPrint:
        print("Transfer Node Sets")
    if exoFrom.num_node_sets() > 0:
        nodeSetProps = exoFrom.get_node_set_property_names()
        nodeSetIds = exoFrom.get_node_set_ids()
        for nsId in nodeSetIds:
            (numSetNodes, numSetDistFacts) = exoFrom.get_node_set_params(nsId)
            exo_to.put_node_set_params(nsId, numSetNodes, numSetDistFacts)
            nsNodes = exoFrom.get_node_set_nodes(nsId)
            exo_to.put_node_set(nsId, nsNodes)
            if numSetDistFacts > 0:
                nsDF = exoFrom.get_node_set_dist_facts(nsId)
                exo_to.put_node_set_dist_fact(nsId, nsDF)
            nodeSetName = exoFrom.get_node_set_name(nsId)
            exo_to.put_node_set_name(nsId, nodeSetName)
            for nodeSetProp in nodeSetProps:
                propVal = exoFrom.get_node_set_property_value(
                    nsId, nodeSetProp)
                if nodeSetProp == "ID" and propVal == nsId:
                    continue
                else:
                    exo_to.put_node_set_property_value(
                        nsId, nodeSetProp, propVal)

    if debugPrint:
        print("Transfer Side Sets")
    if exoFrom.num_side_sets() > 0:
        sideSetProps = exoFrom.get_side_set_property_names()
        sideSetIds = exoFrom.get_side_set_ids()
        for ssId in sideSetIds:
            (numSetSides, numSetDistFacts) = exoFrom.get_side_set_params(ssId)
            exo_to.put_side_set_params(ssId, numSetSides, numSetDistFacts)
            (elemList, sideList) = exoFrom.get_side_set(ssId)
            exo_to.put_side_set(ssId, elemList, sideList)
            if numSetDistFacts > 0:
                ssDF = exoFrom.get_side_set_dist_fact(ssId)
                exo_to.put_side_set_dist_fact(ssId, ssDF)
            sideSetName = exoFrom.get_side_set_name(ssId)
            exo_to.put_side_set_name(ssId, sideSetName)
            for sideSetProp in sideSetProps:
                propVal = exoFrom.get_side_set_property_value(
                    ssId, sideSetProp)
                if sideSetProp == "ID" and propVal == ssId:
                    continue
                else:
                    exo_to.put_side_set_property_value(
                        ssId, sideSetProp, propVal)

    # If the user did not supply an exodus object to copy from, then close the
    # database.
    if exoFromObj is None:
        exoFrom.close()

    return exo_to


def transfer_variables(
        exoFrom,
        exo_to,
        array_type='ctype',
        additionalGlobalVariables=[],
        additionalNodalVariables=[],
        additionalElementVariables=[]):
    """
      This function transfers variables from exoFrom to exo_to and allows
      additional variables to be added with additionalGlobalVariables,
      additionalNodalVariables, and additionalElementVariables.  Additional
      variables values are set to their defaults so that the user can populate
      them later.

      exoFrom: exodus object to transfer from

      exo_to: exodus object to transfer to

      additionalGlobalVariables: list of global variable names to add.

      additionalNodalVaraibles: list of nodal variable names to add.

      additionalElementVariables: should be a list of element variable names to add to all blocks or
        tuples (name, blkIds) where name is the element variable to add
        and blkIds is a list of blkIds to add it to.
    """
    # IDEA: It may make sense to make transfer_variables() strictly transfer
    # variables, and use add_variables() to add new variables.  Alternatively,
    # add_variables() could be called within transfer_variables() to add
    # new variables to the exo_to database.  Either way, we should minimize
    # duplicate code if possible.

    debugPrint = False

    if not isinstance(additionalGlobalVariables, list):
        raise Exception("ERROR: additionalGlobalVariables is not a list.")
    if not isinstance(additionalNodalVariables, list):
        raise Exception("ERROR: additionalNodalVariables is not a list.")
    if not isinstance(additionalElementVariables, list):
        raise Exception("ERROR: additionalElementVariables is not a list.")

    if debugPrint:
        print("Transfer Info records")
    numInfoRecs = exoFrom.num_info_records()
    if numInfoRecs > 0:
        infoRecs = exoFrom.get_info_records()
        exo_to.put_info_records(infoRecs)
    if debugPrint:
        print("Transfer time values")

    nSteps = exoFrom.num_times()
    if nSteps == 0:
        return exo_to

    timeVals = exoFrom.get_times()
    for step in xrange(nSteps):
        exo_to.put_time(step + 1, timeVals[step])

    if debugPrint:
        print("Add Global Variables")
    nNewGlobalVars = len(additionalGlobalVariables)
    nGlobalVars = exoFrom.get_global_variable_number() + nNewGlobalVars
    defaultNewVarVals = []
    for i in xrange(nNewGlobalVars):
        defaultNewVarVals.append(0.0)
    if nGlobalVars > 0:
        exo_to.set_global_variable_number(nGlobalVars)
        gVarNames = exoFrom.get_global_variable_names()
        gVarNames.extend(additionalGlobalVariables)
        for nameIndex in xrange(nGlobalVars):
            globalVarName = gVarNames[nameIndex]
            exo_to.put_global_variable_name(globalVarName, nameIndex + 1)
        for step in xrange(nSteps):
            gValues = exoFrom.get_all_global_variable_values(step + 1)
            if array_type == 'numpy':
                gValues = exo_to.np.append(gValues, defaultNewVarVals)
            else:
                gValues.extend(defaultNewVarVals)
            exo_to.put_all_global_variable_values(step + 1, gValues)

    if debugPrint:
        print("Add Nodal Variables")
    nNewNodalVars = len(additionalNodalVariables)
    nOrigNodalVars = exoFrom.get_node_variable_number()
    nNodalVars = nOrigNodalVars + nNewNodalVars
    if nNodalVars > 0:
        exo_to.set_node_variable_number(nNodalVars)
        nVarNames = exoFrom.get_node_variable_names()
        nVarNames.extend(additionalNodalVariables)
        for nameIndex in xrange(nNodalVars):
            nodalVarName = nVarNames[nameIndex]
            exo_to.put_node_variable_name(nodalVarName, nameIndex + 1)
            if nameIndex < nOrigNodalVars:
                for step in xrange(nSteps):
                    nValues = exoFrom.get_node_variable_values(
                        nodalVarName, step + 1)
                    exo_to.put_node_variable_values(
                        nodalVarName, step + 1, nValues)

    if debugPrint:
        print("Construct Truth Table for additionalElementVariables")
    blkIds = exoFrom.get_elem_blk_ids()
    numBlks = exoFrom.num_blks()
    newElemVariableNames = []
    newElemVariableBlocks = []
    for item in additionalElementVariables:
        if isinstance(item, tuple):
            newElemVariableNames.append(item[0])
            inBlks = []
            for blkId in item[1]:
                if blkId in blkIds:
                    inBlks.append(blkId)
            newElemVariableBlocks.append(inBlks)
        elif isinstance(item, str):
            newElemVariableNames.append(item)
            newElemVariableBlocks.append(blkIds)
        else:
            print("Warning additionalElementVariable item ",
                  item, " is not right type to add.")
            print("should be a string or tuple, skipping")

    if debugPrint:
        print("Add Element Variables")
    nNewElemVars = len(newElemVariableNames)
    nOrigElemVars = exoFrom.get_element_variable_number()
    nElemVars = nOrigElemVars + nNewElemVars
    if nElemVars > 0:
        exo_to.set_element_variable_number(nElemVars)
        origElemVarNames = exoFrom.get_element_variable_names()
        eVarNames = exoFrom.get_element_variable_names()
        eVarNames.extend(newElemVariableNames)
        truthTable = []
        if nOrigElemVars > 0:
            truthTable = exoFrom.get_element_variable_truth_table()
        if nNewElemVars > 0:
            newTruth = []
            for j in xrange(numBlks):
                for k in xrange(nOrigElemVars):
                    index = j * nOrigElemVars + k
                    newTruth.append(truthTable[index])
                for m in xrange(nNewElemVars):
                    if blkIds[j] in newElemVariableBlocks[m]:
                        newTruth.append(True)
                    else:
                        newTruth.append(False)
            truthTable = newTruth
        exo_to.set_element_variable_truth_table(truthTable)
        for nameIndex in xrange(nElemVars):
            elemVarName = eVarNames[nameIndex]
            exo_to.put_element_variable_name(elemVarName, nameIndex + 1)
        truthIndex = 0
        for blkId in blkIds:
            for eVarName in origElemVarNames:
                if truthTable[truthIndex]:
                    for step in xrange(nSteps):
                        eValues = exoFrom.get_element_variable_values(
                            blkId, eVarName, step + 1)
                        exo_to.put_element_variable_values(
                            blkId, eVarName, step + 1, eValues)
                truthIndex = truthIndex + 1
            truthIndex = truthIndex + nNewElemVars

    # TODO: Transfer Nodeset Variables

    # TODO: Transfer Sideset Variables

    return exo_to


def add_variables(exo, global_vars=[], nodal_vars=[], element_vars=[]):
    """
    This function adds variables to the exodus object.  The values of the
    variables are set to their defaults so that the user can populate them later.

    Parameters
    ----------
      exo: exodus database object
        Exodus database that variables will be added to.
    global_vars : list
        global variable names to add.
    nodal_vars : list
        nodal variable names to add.
    element_vars : list
        list of element variable names to add to all blocks or tuples
        ( name, blkIds ) where name is the element variable to add and blkIds is
        a list of blkIds to add it to.

    Returns
    -------
    exo : exodus database object
        Exodus database with variables added to it.  (The values of the variables
        are set to their defaults so that the user can populate them later.)

    See Also
    --------
    This function does not allow one to add element attributes to an exodus
    database.  See the copy_mesh() function for that capability.
    """
    debugPrint = False

    if not isinstance(global_vars, list):
        raise Exception("ERROR: global_vars is not a list.")
    if not isinstance(nodal_vars, list):
        raise Exception("ERROR: nodal_vars is not a list.")
    if not isinstance(element_vars, list):
        raise Exception("ERROR: element_vars is not a list.")

    if exo.modeChar is 'r':
        raise Exception(
            "ERROR: variables cannot be added to an exodus object in read only mode")

    if debugPrint:
        print("Add Global Variables")
    n_new_vars = len(global_vars)
    n_old_vars = exo.get_global_variable_number()
    n_vars = n_old_vars + n_new_vars
    default_vals = [0.0] * n_new_vars
    if n_new_vars > 0:
        exo.set_global_variable_number(n_vars)
        for i, var_name in enumerate(global_vars):
            exo.put_global_variable_name(var_name, n_old_vars + i + 1)
        # One might wish to put all the values for a given global variable in the
        # database at once, but exo.put_global_variable_value() ends up loading
        # all the global variables for a given step and then putting them all back
        # in, so we might as well just use
        # exo.put_all_global_variable_values().
        nSteps = exo.num_times()
        for step in xrange(nSteps):
            gValues = exo.get_all_global_variable_values(step + 1)
            if exo.use_numpy:
                gValues = exo.np.append(gValues, default_vals)
            else:
                gValues.extend(default_vals)
            exo.put_all_global_variable_values(step + 1, gValues)

    if debugPrint:
        print("Add Nodal Variables")
    n_new_vars = len(nodal_vars)
    n_old_vars = exo.get_node_variable_number()
    n_vars = n_old_vars + n_new_vars
    if n_new_vars > 0:
        exo.set_node_variable_number(n_vars)
        for i, var_name in enumerate(nodal_vars):
            exo.put_node_variable_name(var_name, i + n_old_vars + 1)

    if debugPrint:
        print("Construct Truth Table for additionalElementVariables")
    new_e_var_names = []
    new_e_var_blks = []
    blk_ids = exo.get_elem_blk_ids()
    for item in element_vars:
        if isinstance(item, tuple):
            new_e_var_names.append(item[0])
            in_blks = []
            for blk_id in item[1]:
                if blk_id in blk_ids:
                    in_blks.append(blk_id)
            new_e_var_blks.append(in_blks)
        elif isinstance(item, str):
            new_e_var_names.append(item)
            new_e_var_blks.append(blk_ids)
        else:
            print("Warning additionalElementVariable item " +
                  item + " is not right type to add.")
            print("should be a string or tuple, skipping")

    if debugPrint:
        print("Add Element Variables")
    n_new_vars = len(new_e_var_names)
    n_old_vars = exo.get_element_variable_number()
    n_vars = n_old_vars + n_new_vars
    if n_new_vars > 0:
        exo.set_element_variable_number(n_vars)
        old_truth_table = []
        if n_old_vars > 0:
            old_truth_table = exo.get_element_variable_truth_table()
        truth_table = []
        n_blks = exo.num_blks()
        for j in xrange(n_blks):
            for k in xrange(n_old_vars):
                ndx = j * n_old_vars + k
                truth_table.append(old_truth_table[ndx])
            for m in xrange(n_new_vars):
                if blk_ids[j] in new_e_var_blks[m]:
                    truth_table.append(True)
                else:
                    truth_table.append(False)
        exo.set_element_variable_truth_table(truth_table)
        for i, var_name in enumerate(new_e_var_names):
            exo.put_element_variable_name(var_name, n_old_vars + i + 1)

    # TODO: Add Nodeset Variables

    # TODO: Add Sideset Variables

    return exo

# --------------------------------------------------------------------


def copyTransfer(
        fromFileName,
        toFileName,
        array_type='ctype',
        additionalGlobalVariables=[],
        additionalNodalVariables=[],
        additionalElementVariables=[],
        additionalElementAttributes=[]):
    """
      This function creates an exodus file toFileName and copies
      everything from exodus file fromFileName returning a file handle
      to toFileName.

      Additional space is allocated for additionalGlobalVariables,
      additionalNodalVariables and additionalElementVariables if
      specified.

      additionalGlobalVariables: list of global variable names to add.

      additionalNodalVaraibles: list of nodal variable names to add.

      additionalElementVariables: should be a list of element variable
      names to add to all blocks or tuples (name, blkIds) where name is
      the element variable to add and blkIds is a list of blkIds to add
      it to.

      additionalElementAttributes: list of element attribute names to
      add to all blocks or tuples ( name, blkIds ) where name is the
      element attribute to add and blkIds is a list of blkIds to add it
      to.  Usage:

      fromFileName = "input.e"
      toFileName = "output.e"
      ## Do not add any new global variables
      addGlobalVariables = []
      ## Add node_dummy1 and node_dummy2 as new node variables
      addNodeVariables = ["node_dummy1", "node_dummy2"]
      ## Add elem_dummy1 on blkIds 1, 2, 3 and elem_dummy2 on all blocks
      addElementVariables = [ ("elem_dummy1", [1, 2, 3]), "elem_dummy2" ]
      ## Add elem_attr_dummy1 on blkIds 1,2,3 and elem_attr_dummy2 on all blocks
      addElementAttributes = [ ("elem_attr_dummy1",[1,2,3]), "elem_attr_dummy2" ]

      toFileHandle = copyTranfer(fromFileName,toFileName,addGlobalVariables,addNodeVariables,
                                 addElementVariables,addElementAttributes)

      ## Fill in new variables

      toFileHandle.close()

    """

    exoFrom = exodus(fromFileName, "r", array_type=array_type)

    exo_to = copy_mesh(fromFileName, toFileName, exoFromObj=exoFrom,
                       additionalElementAttributes=additionalElementAttributes,
                       array_type=array_type)

    exo_to = transfer_variables(
        exoFrom,
        exo_to,
        additionalGlobalVariables=additionalGlobalVariables,
        additionalNodalVariables=additionalNodalVariables,
        additionalElementVariables=additionalElementVariables,
        array_type=array_type)

    exoFrom.close()
    return exo_to


def ctype_to_numpy(exo, c_array):
    """
    Converts a c-type array into a numpy array

      Parameters
      ----------
      exo : exodus object
          exodus database object initialized with the option array_type = 'numpy'
      c_array : c-type array
          c-type array to be converted into a numpy array

      Returns
      -------
      np_array : numpy array
          Numpy array converted from c-type array
    """
    # ctypes currently produce invalid PEP 3118 type codes, which causes numpy
    # to issue a warning.  This is a bug and can be ignored.
    # http://stackoverflow.com/questions/4964101/pep-3118-warning-when-using-ctypes-array-as-numpy-array
    if len(c_array) == 0:
        return exo.np.array([])

    with exo.warnings.catch_warnings():
        exo.warnings.simplefilter('ignore')
        np_array = exo.np.ctypeslib.as_array(c_array)
    return np_array
