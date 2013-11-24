# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2013-07-25 13:10
# modified : 2013-09-10 16:26
"""
Module provides basic functions for the reading of text files in QLC format.
"""

__author__="Johann-Mattis List"
__date__="2013-09-10"


from .csv import csv2list
from .phylip import read_dst,read_scorer
from ..thirdparty import cogent as cg
import json
import codecs
import os


def _list2msa(
        msa_lines,
        ids=False,
        header=True,
        **keywords
        ):
    """
    Function retrieves a dictionary from a list of MSA strings.

    """
    defaults = dict(
            seq_id = '-',
            dataset = '-',
            input_file = 'dummy'
            )
    for key in defaults:
        if key not in keywords:
            keywords[key] = defaults[key]

    # create the dictionary
    d = dict(
            ID = [],
            taxa = [],
            alignment = [],
            seqs = [],
            infile = keywords['input_file']
            )
    
    if header:
        start = 2
        d['dataset'] = msa_lines[0]
        d['seq_id'] = msa_lines[1]
    else:
        start = 0
        d['dataset'] = keywords['dataset']
        d['seq_id'] = keywords['seq_id']

    for i,line in enumerate(msa_lines[start:]):
        if ids:
            idx = 1
        else:
            idx = 0
        
        # check for specific id
        if line[0] in  ['0', 'LOCAL', 'SWAPS', 'MERGE']:
            if line[idx] == 'LOCAL':
                d['local'] = []
                for j,x in enumerate(line[idx+1:]):
                    if x == '*':
                        d['local'] += [j]
            elif line[idx] == 'SWAPS':
                d['swaps'] = []
                swapline = [x for x in line[idx+1:]]
                j=0
                while swapline:
                    x = swapline.pop(0)
                    if x == '+':
                        d['swaps'] += [(j,j+1,j+2)]
                        swapline.pop(0)
                        swapline.pop(0)
                        j += 2
                    else:
                        pass
                    j += 1
            elif line[idx] == 'MERGE':
                d['merge'] = {}
                mergeline = [x for x in line[idx+1:]]
                k = 1
                merge = False
                for j,m in enumerate(mergeline):
                    if not merge:
                        k += 1

                    if m == '<':
                        merge = True
                    if m == '>':
                        merge = False

                    d['merge'][j] = k

        elif line[0] not in ['LOCAL','SWAPS','MERGE','0']:
            if ids:
                try:
                    d['ID'] += [int(line[0])]
                except:
                    d['ID'] += [line[0]]
            else:
                d["ID"] += [i]
            d["taxa"] += [line[idx].rstrip('.')]
            d["seqs"] += [' '.join([l for l in line[idx+1:] if l != '-'])]
            d["alignment"] += [line[idx+1:]]

    return d

def read_msa(
        infile,
        comment = "#",
        ids = False,
        header = True,
        **keywords
        ):
    """
    Simple function to load an MSA object.

    Parameters
    ----------
    infile : str
        The name of the input file.
    comment : str (default="#")
        The comment character. If a line starts with this character, it will be
        ignored.
    ids : bool (default=False)
        Indicate whether the MSA file contains unique IDs for all sequences or
        not.

    Returns
    -------
    d : dict
        A dictionary in which keys correspond to specific parts of a multiple
        alignment. This dictionary can be directly passed to alignment
        functions, such as :py:class:`lingpy.sca.MSA`.
    """
    if 'input_file' not in keywords:
        keywords['input_file'] = infile

    f = codecs.open(infile,'r','utf-8')
    msa_lines = []
    for line in f:
        if line.strip() and not line.startswith(comment):
            newlines = [t.strip().rstrip('.') for t in line.split('\t')]
            if len(newlines) == 1:
                msa_lines += newlines
            else:
                msa_lines += [newlines]
    
    d = _list2msa(msa_lines, header=header, ids=ids, **keywords)

    return d
    

def read_qlc(
        infile,
        comment = '#'
        ):
    """
    Simple function that loads qlc-format into a dictionary.

    Parameters
    ----------
    infile : str
        The name of the input file.
    comment : str (default="#")
        The comment character. If a line starts with this character, it will be
        ignored.

    Returns
    -------
    d : dict
        A dictionary with integer keys corresponding to the order of the lines
        of the input file. The header is given 0 as a specific key.
    """
    # check whether path exists
    if not os.path.isfile(infile):
        raise NameError(
                "[!] File {0} could not be found.".format(infile)
                )

    inf = codecs.open(infile,'r','utf-8')
    
    # create data array
    data = []
    meta = {}

    # read lines from infile
    lines = inf.readlines()

    inf.close()

    # set dtype to false
    dtype = False

    # start the loop
    while lines:
        line = lines.pop(0)

        # line is empty or starts with hash
        if line.startswith(comment) or not line.strip():
            pass
        
        # line starts with key-value @
        elif line.startswith('@'):
            key = line[1:line.index(':')]
            value = line[line.index(':')+1:].strip()
            if key not in ['tree']:
                if key not in meta:
                    meta[key] = value
                else:
                    if type(meta[key]) == list:
                        meta[key] += [value]
                    else:
                        print("[WARNING] Key '{0}' in input file is not unique! Use JSON-format for these datatypes!".format(key))
                        meta[key] = [meta[key]]
                        meta[key] += [value]
                        
            else:
                if key == 'tree':
                    meta["tree"] = cg.LoadTree(treestring=value)
        
        # line starts with complex stuff
        elif line.startswith('<'):
            tmp = line[1:line.index('>')]
            # check for specific keywords
            if ' ' in tmp:
                dtype = tmp.split(' ')[0]
                keys = dict([(k,v[1:-1]) for k,v in [key.split('=') for key in
                    tmp.split(' ')[1:]]])
            else:
                dtype = tmp.strip()
                keys = {}

            tmp = []

            # iterate
            while True:
                line = lines.pop(0)

                if line.startswith('</'+dtype+'>'):
                    break
                else:
                    tmp += [line.strip()]

            tmp = '\n'.join(tmp)

            # check for data stuff
            # json
            if dtype == "json":
                tmp = json.loads(tmp)
                if not keys:
                    for key in tmp:
                        meta[key] = tmp[key]
                elif keys:
                    meta[keys["id"]] = {}
                    for k in tmp:
                        meta[keys["id"]][k] = tmp[k]
            
            # tree
            elif dtype in ['tre','nwk']:
                
                # check for "tree" in meta
                if "trees" not in meta:
                    meta["trees"] = {}
                
                # add the data
                if not keys:
                    keys["id"] = "1"

                meta['trees'][keys["id"]] = cg.LoadTree(treestring=tmp)

            # csv
            elif dtype in ['csv']:

                meta[keys["id"]] = {}

                # check for columns
                if "ncol" in keys:
                    ncol = int(keys["ncol"])
                else:
                    ncol = 2

                # check for dtype
                if "dtype" in keys:
                    transf = eval(keys["dtype"])
                else:
                    transf = str

                # split tmp into lines
                tmp = tmp.split('\n')
                for l in tmp:
                    if ncol == 2:
                        a,b = l.split('\t')
                        b = transf(b)
                    else:
                        l = l.split('\t')
                        a = l[0]
                        b = [transf(b) for b in l[1:]]
                    meta[keys["id"]][a] = b

            elif dtype == 'msa':
                
                # check for dtype
                tmp = tmp.split('\n')
                if 'msa' not in meta:
                    meta['msa'] = {}

                # check for additional reference attribute
                if 'ref' in keys:
                    ref = keys['ref']
                else:
                    ref = 'cogid' # XXX check this later for flexibility

                # check for msa.ref:
                if ref not in meta['msa']:
                    meta['msa'][ref] = {}

                tmp_msa = {}
                try:
                    tmp_msa['dataset'] =  meta['dataset']
                except:
                    tmp_msa['dataset'] = infile.replace('.csv','')

                tmp_msa['seq_id'] = keys['id']

                # add consensus string to msa, if it appears in the keys
                if "consensus" in keys:
                    tmp_msa['consensus'] = keys['consensus']
                
                msad = []
                for l in tmp:
                    if not l.startswith(comment):
                        
                        line = [x.strip().rstrip('.') for x in
                                l.split('\t')]
                        msad += [line]
                tmp_msa = _list2msa(msad,header=False,ids=True,**tmp_msa)

                try:
                    meta['msa'][ref][int(keys['id'])] = tmp_msa   
                except:
                    meta['msa'][ref][keys['id']] = tmp_msa
            
            elif dtype == 'dst':
                taxa,matrix = read_dst(tmp)
                new_taxa = sorted(taxa)
                distances = [[0.0 for line in matrix] for line in matrix]
                for i,line in enumerate(matrix):
                    for j,cell in enumerate(line):
                        if i < j:
                            idxA = new_taxa.index(taxa[i])
                            idxB = new_taxa.index(taxa[j])
                            distances[i][j] = cell
                            distances[j][i] = cell
                meta['distances'] = distances
            elif dtype == 'scorer':
                scorer = read_scorer(tmp)
                if not 'scorer' in meta:
                    meta['scorer'] = {}
                if 'id' not in keys:
                    keys['id'] = 'basic'
                meta['scorer'][keys['id']] = scorer

            elif dtype == 'taxa':
                meta['taxa'] = [t.strip() for t in tmp.split('\n')]          
        else:
            data += [[l.strip() for l in line.split('\t')]]
    
    # create the dictionary in which the data will be stored
    d = {}

    # check for first line, if a local ID is given in the header (or simply
    # "ID"), take this line as the ID, otherwise create it
    if data[0][0].lower() in ['id','local_id','localid']:
        local_id = True
    else:
        local_id = False

    # iterate over data and fill the dictionary (a bit inefficient, but enough
    # for the moment)
    try:
        i = 1
        for line in data[1:]:
            if local_id:
                d[int(line[0])] = line[1:]
            else:
                d[i] = line
                i += 1
    except:
        raise Exception("Error processing line:\n" + line)

    # assign the header to d[0]
    if local_id:
        d[0] = [x.lower() for x in data[0][1:]]
    else:
        d[0] = [x.lower() for x in data[0]]
    
    for m in meta:
        d[m] = meta[m]
    
    # check for tree-attributes
    if 'trees' in d and not 'tree' in d:
        d['tree'] = sorted(
                d['trees'].items(),
                key = lambda x: x[0],
                )[0][1]
                

    return d

def qlc2dict(infile):

    return read_qlc(infile)
