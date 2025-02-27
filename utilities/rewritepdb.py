import os 
import sys
from pymd.structure.structure_file import StructureFile
from pymd.utilities.library import residues as _residues

def addChainID(filename, newfilename, nterm, cterm):
    
    # initialize variables
    contents = [] # hold contents of .pdb file
    new_contents = [] # hold contents of new .pdb file
    next_resnum = None # hold the next residue in the .pdb file
    switch = False # tells when next atom should switch chain id
    chain_id = 'A' # hold current chain ID
    i = 0 # iterator
    
    f = open(filename, 'r') # open .pdb file
    for line in f:
        contents.append(line) # append contents of .pdb file to a list
    f.close()
    
    for line in contents:
        if ('ATOM' in line) and ('SOL' not in line): # check for ATOM line
            line_parts = line.split()
            res_num = line_parts[4] # current residue number
            res_name = line_parts[3]
            res_id = res_name + res_num
            # if int(res_num) % cterm == 0: # check if the residue number is the last in the chain
            if res_id == cterm:
                try:
                    parts = contents[i+1].split() # check next atom info
                except:
                    parts = ['TER']
                if 'TER' not in parts: # check that next line is an atom
                    next_name = parts[3]
                    next_num = parts[4]
                    next_id = next_name + next_num
                    if next_id == nterm:
                        switch = True # increment chain ID if next res name is nterm
                    # format the new line with chain ID, append to newcontents

                if len(line_parts[2]) < 4: 
                    line_format = '{:<4s}{:>7s}  {:<3} {:>3s} ' + chain_id + '{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                    formatted_list = line_format.format(*line_parts)
                    new_contents.append(formatted_list)
                if len(line_parts[2]) == 4:
                    line_format = '{:<4s}{:>7s} {:<4} {:>3s} ' + chain_id + '{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                    formatted_list = line_format.format(*line_parts)
                    new_contents.append(formatted_list)
                if switch is True: # check if the next atom is on the next chain
                    chain_id = chr(ord(chain_id) + 1) # increment chain ID
                    switch = False
            else:
                # format the new line with chain ID, append to new_contents
                if len(line_parts[2]) < 4:
                    line_format = '{:<4s}{:>7s}  {:<3} {:>3s} ' + chain_id + '{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                    formatted_list = line_format.format(*line_parts)
                    new_contents.append(formatted_list)
                if len(line_parts[2]) == 4:
                    line_format = '{:<4s}{:>7s} {:<4} {:>3s} ' + chain_id + '{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                    formatted_list = line_format.format(*line_parts)
                    new_contents.append(formatted_list)
        else:
            # append remark/comment lines to new_contents
            new_contents.append(line)
        i += 1 # incrementor

    # write new .pdb file
    f = open(newfilename, 'w') 
    for item in new_contents:
        f.write(item)
        f.write('          \n') 
    f.close()

    # return list of edited contents
    return newfilename


def addChainID_CHARMM(inp, out):
    newcontents = []
    f = open(inp, 'r')
    contents = f.readlines()
    f.close()
    for line in contents:
        if not line.startswith(('ATOM', 'HETATM',)):
            newcontents.append(line.split())
            continue
        parts = line.split()
        segid = parts[-2]
        if segid.startswith('PRO'):
            chain_id = segid[3:]
            _parts = parts[:]
            parts = _parts[0:4] + [chain_id] + _parts[4:]
        newcontents.append(parts)
        if parts[3] == 'CER1':
            print(parts)

    writePDB(newcontents, out)

def renumberPDB(filename, newfilename, nterm, cterm):
    # initialize variables
    contents = [] # hold .pdb file contents
    new_contents = [] # hold edited contents
    num = 1 # hold current residue number
    i = 0 # iterator
    
    # open .pdb, append contents to contents list
    f = open(filename, 'r')
    contents = f.readlines()
    f.close()


    for line in contents:
        if 'ATOM' in line: # check for atom line
            line_parts = line.split() # hold line contents
            res_num = line_parts[5] # hold current residue number
            if int(res_num) % cterm == 0: # check if current residue is the last in the chain
                parts = contents[i+1].split() # check next atom 
                if 'TER' not in parts: # check if next atom is atom
                    next_resnum = int(parts[5]) # hold next residue number
                # format the new line with appropriate residue number, append to newcontents
                if len(line_parts[2]) < 4:
                    line_parts[5] = str(num)
                    line_format = '{:<4s}{:>7s}  {:<3} {:>3s} {:1s}{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                    formatted_list = line_format.format(*line_parts)
                    new_contents.append(formatted_list)
                if len(line_parts[2]) == 4:
                    line_parts[5] = str(num)
                    line_format = '{:<4s}{:>7s} {:<4} {:>3s} {:1s}{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                    formatted_list = line_format.format(*line_parts)
                    new_contents.append(formatted_list)
                # check if next atom is on a new peptide
                if int(next_resnum) != int(res_num):
                    num = nterm
            else:
                parts = contents[i+1].split() # check next atom
                if parts[0].startswith('ATOM'): # check if next atom is atom
                    next_resnum = parts[5] # hold next residue number
                # format the new line with appropriate residue number, append to newcontents
                if len(line_parts[2]) < 4: 
                    line_parts[5] = str(num)
                    line_format = '{:<4s}{:>7s}  {:<3} {:>3s} {:1s}{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                    formatted_list = line_format.format(*line_parts)
                    new_contents.append(formatted_list)
                if len(line_parts[2]) == 4:
                    line_parts[5] = str(num)
                    line_format = '{:<4s}{:>7s} {:<4} {:>3s} {:1s}{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                    formatted_list = line_format.format(*line_parts)
                    new_contents.append(formatted_list)
                if int(next_resnum) != int(res_num):
                    num += 1
        else:
            # append comment lines to new_contents
            new_contents.append(line)
        i += 1 # iterator

    # write new .pdb file
    f = open(newfilename, 'w') 
    for line in new_contents:
        f.write(line)
        f.write('      \n')
    f.close()

    # return list of edited contents
    return newfilename

def renumberByChain(filename, newfilename, start=1):
    struct = StructureFile(filename)
    new_contents = ['REMARK    RE-NUMBERED BY pymd.utilities.rewritepdb.renumberByChain\n']
    res_counter = start
    atom_counter = 1
    last_chain_index = None
    last_res_id = None
    for i, ld in enumerate(struct.pdb()):
        # write non-atom strings
        if isinstance(ld, str):
            new_contents.append(ld)
            continue
        
        # get res id
        res_id = ld.residue_name + str(ld.residue_number)

        #check for residue change
        if last_res_id is not None:
            if last_res_id != res_id:
                res_counter += 1

        # check if residue counter > 9999
        if res_counter > 9999:
            res_counter = 0

        # check if atom_counter > 99999
        if atom_counter > 99999:
            atom_counter = 0

        # check chain index
        if ld.chain_index != last_chain_index:
            res_counter = start

        # format and save line for writing
        line_parts = ['ATOM', str(atom_counter), ld.atom_name, ld.residue_name, ld.chain, str(res_counter), 
              ld.x, ld.y, ld.z, ld.occ, ld.temp, ld.segid, ld.elem, ld.charge]
        if len(ld.atom_name) > 3:
            line = '{:<4s}{:>7s} {:<4s} {:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)
        else:
            line = '{:<4s}{:>7s}  {:<4s}{:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)
        new_contents.append(line)

        # update last data
        last_chain_index = ld.chain_index
        last_res_id = res_id
        atom_counter += 1

    # write file
    f = open(newfilename, 'w')
    for line in new_contents:
        f.write(line)
    f.close()

def editchainID_v2(filename, output=None, start=1, atom_start=1,renumber_chain=True):
    struct = StructureFile(filename)
    new_contents = ['REMARK    CHAIN ID EDITED BY BY pymd.utilities.rewritepdb.editchainID_v2\n']
    res_counter = start
    atom_counter = atom_start
    last_chain_index = None
    last_res_id = None
    last_res_num = None
    chain_id = 'A'
    _real_chain_id = 'A'
    for i, ld in enumerate(struct.pdb()):
        # write non-atom strings
        if isinstance(ld, str):
            new_contents.append(ld)
            continue
        
        # get res id
        res_id = ld.residue_name + str(ld.residue_number)
        if ld.residue_name not in _residues():
            new_contents.append(ld.line)
            continue

        #check for residue change
        if last_res_id is not None:
            if last_res_id != res_id:
                res_counter += 1

        if last_res_num is not None:
            if (ld.residue_number != last_res_num + 1) and (ld.residue_number != last_res_num):
                if chain_id != '':
                    chain_id = chr(ord(chain_id) + 1)
                    _real_chain_id = chr(ord(_real_chain_id) + 1)
                    if renumber_chain:
                        res_counter = start
                else:
                    _real_chain_id = chr(ord(_real_chain_id) + 1)
            elif (ld.residue_id != last_res_id) and (ld.residue_name not in _residues()):
                if chain_id != '':
                    chain_id = chr(ord(chain_id) + 1)
                    _real_chain_id = chr(ord(_real_chain_id) + 1)
                    if renumber_chain:
                        res_counter = start
                else:
                    _real_chain_id = chr(ord(_real_chain_id) + 1)

        # check if residue counter > 9999
        if res_counter > 9999:
            res_counter = 0

        # check if atom_counter > 99999
        if atom_counter > 99999:
            atom_counter = 0

        # check chain index
        if ld.chain_index != last_chain_index:
            res_counter = start

        if ld.residue_name not in _residues():
            chain_id = ''
        # format and save line for writing
        line_parts = ['ATOM', str(atom_counter), ld.atom_name, ld.residue_name, chain_id, str(res_counter), 
              ld.x, ld.y, ld.z, ld.occ, ld.temp, ld.segid, ld.elem, ld.charge]
        if len(ld.residue_name) <= 3:
            if len(ld.atom_name) > 3:
                line = '{:<4s}{:>7s} {:<4s} {:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)
            else:
                line = '{:<4s}{:>7s}  {:<4s}{:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)
        else:
            if len(ld.atom_name) > 3:
                line = '{:<4s}{:>7s} {:<4s} {:>3s}{:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)
            else:
                line = '{:<4s}{:>7s}  {:<4s}{:>3s}{:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)

        new_contents.append(line)

        # update last data
        last_chain_index = ld.chain_index
        last_res_id = res_id
        last_res_num = ld.residue_number
        atom_counter += 1

    # write file
    if output is None:
        output = filename
    f = open(output, 'w')
    for line in new_contents:
        f.write(line)
    f.close() 

def add_segid(filename, output=None, renumber_chain=True, start=1):
    struct = StructureFile(filename)
    new_contents = ['REMARK    CHAIN ID EDITED BY BY pymd.utilities.rewritepdb.editchainID_v2\n']
    res_counter = start
    atom_counter = 1
    last_chain_index = None
    last_res_id = None
    last_res_num = None
    last_res_name = None
    chain_id = 'A'
    _real_chain_id = 'A'
    real_res_counter = 1
    sol = ['SOL', 'TIP3', 'NA', 'CL', 'K', 'CLA', 'POT', 'SOD']
    for i, ld in enumerate(struct.pdb()):
        # write non-atom strings
        if isinstance(ld, str):
            new_contents.append(ld)
            continue
        
        # get res id
        res_id = ld.residue_name + str(ld.residue_number)

        #check for residue change
        if last_res_id is not None:
            if last_res_id != res_id:
                res_counter += 1
                real_res_counter += 1
                
        if last_res_num is not None:
            if (ld.residue_number != last_res_num + 1) and (ld.residue_number != last_res_num):
                if not ld.residue_name in ['SOL', 'TIP3', 'NA', 'CL', 'K', 'CLA', 'POT', 'SOD']:
                    chain_id = chr(ord(chain_id) + 1)
                    _real_chain_id = chr(ord(_real_chain_id) + 1)
                    if renumber_chain:
                        res_counter = start
                else:
                    if (last_res_name not in sol) and (ld.residue_name in sol):
                        chain_id = ''
            # else:
            #     if (last_res_name not in sol) and (ld.residue_name in sol):
            #         chain_id = chr(ord(chain_id) + 1)
            #         _real_chain_id = chr(ord(_real_chain_id) + 1)
            #     elif (ld.residue_name in sol):
            #         if last_res_name != ld.residue_name:
            #             chain_id = chr(ord(chain_id) + 1)


        # check if residue counter > 9999
        if res_counter > 9999:
            res_counter = 0

        # check if atom_counter > 99999
        if atom_counter > 99999:
            atom_counter = 0

        # check chain index
        if ld.chain_index != last_chain_index:
            res_counter = start

        if ld.residue_name in ['SOL', 'TIP3']:
            segid = 'SOLV'
        elif ld.residue_name in ['NA', 'CL', 'K', 'CLA', 'POT', 'SOD']:
            segid = 'SOLV'
        else:
            segid = 'PRO{}'.format(chain_id)
        # format and save line for writing
        line_parts = ['ATOM', str(atom_counter), ld.atom_name, ld.residue_name, chain_id, str(res_counter), 
              ld.x, ld.y, ld.z, ld.occ, ld.temp, segid, ld.elem, ld.charge]
        if len(ld.atom_name) > 3:
            line = '{:<4s}{:>7s} {:<4s} {:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)
        else:
            line = '{:<4s}{:>7s}  {:<4s}{:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)
        new_contents.append(line)

        # update last data
        last_chain_index = ld.chain_index
        last_res_id = res_id
        last_res_num = ld.residue_number
        last_res_name = ld.residue_name
        atom_counter += 1

    # write file
    if output is None:
        output = filename
    f = open(output, 'w')
    for line in new_contents:
        f.write(line)
    f.close() 

def solv2CHARMM(filename, output=None, renumber_chain=True, start=1):
    struct = StructureFile(filename)
    new_contents = ['REMARK    CHAIN ID EDITED BY BY pymd.utilities.rewritepdb.editchainID_v2\n']
    res_counter = start
    atom_counter = 1
    last_chain_index = None
    last_res_id = None
    last_res_num = None
    last_res_name = None
    chain_id = 'A'
    _real_chain_id = 'A'
    real_res_counter = 1
    sol = ['SOL', 'TIP3', 'NA', 'CL', 'K', 'CLA', 'POT', 'SOD']
    for i, ld in enumerate(struct.pdb()):
        # write non-atom strings
        if isinstance(ld, str):
            new_contents.append(ld)
            continue
        
        # get res id
        res_id = ld.residue_name + str(ld.residue_number)

        # #check for residue change
        # if last_res_id is not None:
        #     if last_res_id != res_id:
        #         res_counter += 1
        #         real_res_counter += 1
                
        # if last_res_num is not None:
        #     if (ld.residue_number != last_res_num + 1) and (ld.residue_number != last_res_num):
        #         if not ld.residue_name in ['SOL', 'TIP3', 'NA', 'CL', 'K', 'CLA', 'POT', 'SOD']:
        #             chain_id = chr(ord(chain_id) + 1)
        #             _real_chain_id = chr(ord(_real_chain_id) + 1)
        #             if renumber_chain:
        #                 res_counter = start
        #         else:
        #             chain_id = ''


        # # check if residue counter > 9999
        # if res_counter > 9999:
        #     res_counter = 0

        # # check if atom_counter > 99999
        # if atom_counter > 99999:
        #     atom_counter = 0

        # # check chain index
        # if ld.chain_index != last_chain_index:
        #     res_counter = start

        if ld.residue_name in ['SOL', 'TIP3']:
            segid = 'SOLV'
            res_name = 'TIP3'
            if ld.elem == 'OW':
                atom_name = 'OH2'
            elif ld.atom_name == 'HW1':
                atom_name = 'H1'
            elif ld.atom_name == 'HW2':
                atom_name = 'H2'
            
        elif ld.residue_name in ['NA', 'CL', 'K', 'CLA', 'POT', 'SOD']:
            segid = 'IONS'
            if (ld.residue_name == 'NA') or (ld.residue_name == 'SOD'):
                res_name = 'SOD'
                atom_name = 'SOD'
                ld.elem = 'Na'
            if (ld.residue_name == 'K') or (ld.residue_name == 'POT'):
                res_name = 'POT'
                atom_name = 'POT'
                ld.elem ='K'
            if (ld.residue_name == 'CL') or (ld.residue_name == 'CLA'):
                res_name = 'CLA'
                atom_name = 'CLA'
                ld.elem='Cl'
        else:
            segid = 'PRO{}'.format(chain_id)
            res_name = ld.residue_name
            atom_name = ld.atom_name
        # format and save line for writing
        line_parts = ['ATOM', str(atom_counter), atom_name, res_name, chain_id, str(res_counter), 
              ld.x, ld.y, ld.z, ld.occ, ld.temp, segid, ld.elem, ld.charge]
        if len(ld.atom_name) > 3:
            line = '{:<4s}{:>7s} {:<4s} {:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)
        else:
            line = '{:<4s}{:>7s}  {:<4s}{:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>1.2f}  {:>1.2f}{:>10s} {}{}\n'.format(*line_parts)
        new_contents.append(line)

        # # update last data
        # last_chain_index = ld.chain_index
        # last_res_id = res_id
        # last_res_num = ld.residue_number
        # last_res_name = ld.residue_name
        # atom_counter += 1

    # write file
    if output is None:
        output = filename
    f = open(output, 'w')
    for line in new_contents:
        f.write(line)
    f.close() 

def editChainID(filename, *args, output=None, renumber_chains=False, chain_id='A'):
    '''
    edits chain id by given residue ranges (tuples)
    usage:
    editchainID(filename, (resnum1ChainA, resnum2ChainB), (resnum1ChainB, resnum2ChainB)..., output=optional)
    '''
    # check inputs
    if args is not None:
        for arg in args:
            if not isinstance(arg, tuple):
                raise ValueError('The first positional argument must be a filename; any subsequent positional arguments must be a tuple of length 2. To specify an output filename, use a keyword argument.')
            if not len(arg) == 2:
                raise ValueError('Positional arguments specifying residue ranges for chains must have only two entries (n-terminal residue number, c-terminal residue number). Residue range {} does not have a length of 2.'.format(arg))
            try:
                arg = tuple(map(int, arg))
            except:
                raise ValueError('Positional arguments specifying residue ranges must be integers. Residue range {} has a value that cannot be interpereted as an integer.'.format(arg))
    else:
        reassignChainID(filename, chain_id, output, renumber_chains)
        return 0
    try:
        assert isinstance(filename, str)
    except:
        raise ValueError('Filename {} (first positional argument) must be a string.'.format(filename))
    try:
        assert filename.endswith('pdb')
    except:
        raise ValueError('Input file must be a .pdb')


    # open file
    f = open(filename, 'r')
    contents = f.readlines()
    f.close()
    newcontents = []

    # initialize incrementers
    chain_id = 'A'
    i = 0
    chain_counter = 0
    current_chain = args[chain_counter]
    resnr = 0
    last_res = None
    last_chain = current_chain
    reset = False
    for line in contents:
        if line.startswith('ATOM'):
            line_parts = line.split()
            # cleaning
            # check if last field is segid
            if isFloat(line_parts[-1].strip()):
                segid = line_parts[2][0]
                line_parts.append(segid)
            # check for occupancy line
            if line_parts[10] != '0.00':
                line_parts[10] = '0.00'
            # check if chain ID exists
            if not hasChainID(line):
                first_four_fields = line_parts[:4]
                first_four_fields.append("X")
                line_parts = first_four_fields + line_parts[4:]
            # give proper chain id if in current range
            res_num = int(line_parts[5])
            if res_num in range(current_chain[0], current_chain[1]):
                line_parts[4] = chain_id
            else: 
                # give proper chain id if cterm of current chain
                if (res_num == current_chain[1]):
                    line_parts[4] = chain_id 
                # check for increment
                if (line != contents[-1]) and (contents[i + 1].startswith('ATOM')):
                    if hasChainID(contents[i+1]):
                        next_res_num = int(contents[i+1].split()[5])
                    else:
                        next_res_num = int(contents[i + 1].split()[4])
                    # if next line's res num is the start of a new range, increment chain id
                    if (chain_counter+1 != len(args)) and (next_res_num == args[chain_counter+1][0]):
                        chain_id = chr(ord(chain_id)+1)
                        chain_counter += 1
                        reset = True
                        current_chain = args[chain_counter]
            # renumbering chains
            if renumber_chains:
                current_res = line_parts[5]
                # increment res number if the last res number was different
                if (current_res != last_res):
                    resnr += 1
                last_res = line_parts[5]
                line_parts[5] = str(resnr)
                # reset for new chain
                if reset is True:
                    resnr = 0
                    reset = False
            newcontents.append(formatString(line_parts))
        elif line.startswith('CONECT'):
            continue
        else:
            newcontents.append(line)
        i += 1

    
    if output is None:
        filepath = os.path.join(os.sep.join(filename.split(os.sep)[:-1]))
        if filepath == '':
            if sys.platform == 'win32':
                try:
                    filepath = os.path.join(os.sep.join(filename.split('/')[:-1]))
                    assert filepath != ''
                    filename = filename.split('/')[-1][:-4] + '_chainid.pdb'
                except:
                    filepath = os.getcwd()
                    filename = output[:-4] + '_chainid.pdb'
            else:
                filepath = os.getcwd() 
                filename = output[:-4] + '_chainid.pdb'
        else:
            filename = filename.split(os.sep)[-1][:-4] + '_chainid.pdb'
        output = os.path.join(filepath, filename)

    f = open(output, 'w')
    for line in newcontents:
        f.write(line)
    f.close()

def reassignChainID(filename, chain_id, output=None, renumber_chains=False):
    f = open(filename, 'r')
    contents = f.readlines()
    f.close()
    newcontents = []
    last_res = None
    if type(renumber_chains) is int:
        resnr = renumber_chains
        renumber_chains = True
    else:
        resnr = 1
    for line in contents:
        if line.startswith('ATOM'):
            line_parts = line.split()
            # cleaning
            # check if last field is segid
            if isFloat(line_parts[-1].strip()):
                segid = line_parts[2][0]
                line_parts.append(segid)
            # check for occupancy line
            if line_parts[10] != '0.00':
                line_parts[10] = '0.00'
            # check if chain ID exists
            if not hasChainID(line):
                first_four_fields = line_parts[:4]
                first_four_fields.append("X")
                line_parts = first_four_fields + line_parts[4:]
            # give proper chain id 
            line_parts[4] = chain_id
            # renumbering chains
            if renumber_chains:
                current_res = line_parts[5]
                if last_res is None:
                    last_res = current_res
                # increment res number if the last res number was different
                if (current_res != last_res):
                    resnr += 1
                last_res = line_parts[5]
                line_parts[5] = str(resnr)
            newcontents.append(formatString(line_parts))   
        elif line.startswith('CONECT'):
            continue
        else:
            newcontents.append(line)  

    if output is None:
        filepath = os.path.join(os.sep.join(filename.split(os.sep)[:-1]))
        if filepath == '':
            if sys.platform == 'win32':
                try:
                    filepath = os.path.join(os.sep.join(filename.split('/')[:-1]))
                    assert filepath != ''
                    filename = filename.split('/')[-1][:-4] + '_chainid.pdb'
                except:
                    filepath = os.getcwd()
                    filename = output[:-4] + '_chainid.pdb'
            else:
                filepath = os.getcwd() 
                filename = output[:-4] + '_chainid.pdb'
        else:
            filename = filename.split(os.sep)[-1][:-4] + '_chainid.pdb'
        output = os.path.join(filepath, filename)   
    f = open(output, 'w')
    for line in newcontents:
        f.write(line)
    f.close()
            
def formatString(line_parts, chain_id=None):
        atom_name = line_parts[2]
        if chain_id is not None:
            line_parts[4] = chain_id
        coords = None
        if line_parts[4].isalpha():
            try:
                coords = list(map(float, line_parts[6:9]))
            except:
                coords = fixBadCoordinates(line_parts[6:9])
                line_parts = line_parts[:6] + list(map(str, coords)) + line_parts[8:]
        else:
            try:
                coords = list(map(float, line_parts[5:8]))
            except:
                coords = fixBadCoordinates(line_parts[5:8])
                line_parts = line_parts[:5] + list(map(str, coords)) + line_parts[7:]
        if len(atom_name) > 3:
            string = '{:<4s}{:>7s} {:<4s} {:>3s} {:1s}{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}{:>12s}\n'.format(*line_parts)
        else:
            string = '{:<4s}{:>7s}  {:<4s}{:>3s} {:1s}{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}{:>12s}\n'.format(*line_parts)
        return string

def fixBadCoordinates(line_parts):
    '''
    Fixes bad coordinates with no spaces between them
    Arguments:
    * line_parts (list): list of bad coordinates
    Returns: (list) fixed x,y,z coordinates for atom
    '''
    coords = []
    chunk = ''.join(line_parts)
    string = ''
    i = 0
    for char in chunk:
        if (char != '.') and (i == 0):
            string = string + char
        if (char != '.') and (i != 0):
            string = string + char
            i += 1
            if i == 4:
                coords.append(float(string))
                if len(coords) == 3:
                    return coords
                i = 0
                string = ''
        if char == '.':
            string = string + char
            i += 1
def isFloat(val):
    try:
      float(val)
      return True
    except:
        return False  

def hasChainID(line):
    if line.split()[4].isnumeric():
        return False
    else:
        return True

def editChainIDResidue(filename, newfilename, nterm, cterm, sm=None):
    '''
    updates chain id by giving residue names nterm and cterm. for peptides. 
    '''
    f = open(filename, 'r')
    contents = f.readlines()
    f.close()

    newcontents = []
    nterm = str(nterm)
    cterm = str(cterm)
    chain_id = 'A'
    i = 0
    sol = False
    residues = ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLU', 'GLN', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL', 'HSD']
    for line in contents:
        if line.startswith('ENDMDL'):
            chain_id = 'A'
        if line.startswith('ATOM'):
            line_parts = line.split()
            # check if chain ID exists
            if not hasChainID(line):
                first_four_fields = line_parts[:4]
                first_four_fields.append(chain_id)
                line_parts = first_four_fields + line_parts[4:]
            else:
                first_four_fields = line_parts[:4]
                first_four_fields.append(chain_id)
                line_parts = first_four_fields + line_parts[5:]
            if line_parts[3] not in residues:
                newcontents.append(line)
                continue
            # check if last field is segid
            if isFloat(line_parts[-1]):
                segid = [char for char in line_parts[2] if char.isalpha()][0]
                line_parts.append(segid)
            # increment chain ID 
            if (line != contents[-1]) and (contents[i + 1].startswith('ATOM')):
                res_name = line_parts[3]
                res_num  = line_parts[5]
                res_id = res_name + res_num
                next_res_name = contents[i+1].split()[3]
                next_res_num = contents[i+1].split()[4]
                next_res_id = next_res_name + next_res_num
                # increment bc going to new nterm
                if (res_id == cterm) and (next_res_id == nterm):
                    print(res_id, next_res_id)
                    chain_id = chr(ord(chain_id) + 1)
                # increment bc going to new sm from cterm
                if (res_id == cterm) and (next_res_name == sm):
                    chain_id = chr(ord(chain_id) + 1)
                # increment bc going to new sm from another sm
                if (res_name == sm):
                    res_num = line_parts[5]
                    # check if next line has chain id
                    if hasChainID(contents[i+1]):
                        next_res_num = contents[i+1].split()[5]
                    else:
                        next_res_num = contents[i+1].split()[4]
                    # increment
                    if next_res_num != res_num:
                        chain_id = chr(ord(chain_id) + 1)
            newcontents.append(formatString(line_parts))
        else:
            newcontents.append(line)
        i += 1

    f = open(newfilename, 'w')
    for line in newcontents:
        f.write(line)
    f.close()


def writePDB(data, newfilename):
    # print(newfilename)
    f = open(newfilename, 'w')
    ter = False
    for line in data:
        if line == []:
            continue
        if ('TER' in line):
            # if ([data][-1] == ['TER']) or ([data][-1] == 'TER'):
            #     ter = True
            #     string = '{}'.format(*line)
            #     f.write(string)
            #     break
            ter = True
            string = '{}\n'.format(line[0])
            f.write(string)
            # break
        elif (line[0] == 'ATOM') or (line[0] == 'HETATM'):
            if not line[1].isnumeric():
                continue
            atom_name = line[2]
            atom_symbol = line[2][0]
            res_name = line[3]
            if line[-1] != atom_symbol:
                line.append(atom_symbol)
            if line[4].isalpha():
                if ('SOL' not in line) and ('NA' not in line) and ('CL' not in line):
                    if isinstance(line[6], str):
                        xyz = list(map(float, line[6:9]))
                        line[6] = xyz[0]
                        line[7] = xyz[1]
                        line[8] = xyz[2]
                else:
                    if isinstance(line[5], str):
                        xyz = list(map(float, line[5:8]))
                        line[5] = xyz[0]
                        line[6] = xyz[1]
                        line[7] = xyz[2]
                if line[0].startswith('ATOM'):
                    if len(atom_name) > 3:
                        if len(line[-1]) == 1:
                            string = '{:<4s}{:>7s} {:<4s} {:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s} {}\n'.format(*line)
                        else:
                            string = '{:<4s}{:>7s} {:<4s} {:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s}\n'.format(*line)
                    else:
                        if len(line[-1]) == 1:
                            string = '{:<4s}{:>7s}  {:<4s}{:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s} {}\n'.format(*line)
                        else:
                            string = '{:<4s}{:>7s}  {:<4s}{:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s}\n'.format(*line)
                #### HETATM
                else:
                    if len(atom_name) > 3:
                        if len(line[-1]) == 1:
                            string = '{:<4s}{:>5s} {:<4s} {:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s} {}\n'.format(*line)
                        else:
                            string = '{:<4s}{:>5s} {:<4s} {:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s}\n'.format(*line)
                    else:
                        if len(line[-1]) == 1:
                            string = '{:<4s}{:>5s}  {:<4s}{:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s} {}\n'.format(*line)
                        else:
                            string = '{:<4s}{:>5s}  {:<4s}{:>3s} {:1s}{:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s}\n'.format(*line)
            else:
                if isinstance(line[5], str):
                    xyz = list(map(float, line[5:8]))
                    line[5] = xyz[0]
                    line[6] = xyz[1]
                    line[7] = xyz[2]
                if len(atom_name) > 3:
                    string = '{:<4s}{:>7s} {:^4s} {:>3s} {:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s} {}\n'.format(*line)
                else:
                    string = '{:<4s}{:>7s}  {:<4s}{:>3s} {:>4s}    {:>8.3f}{:>8.3f}{:>8.3f}  {:>3s}  {:>3s}{:>10s} {}\n'.format(*line)
            f.write(string)
        else:
            string = '{}'.format(line)
            f.write(string)
    f.close()
    return newfilename

def renumberProtein(filename, newfilename, start):
    # initialize variables
    contents = [] # hold .pdb file contents
    new_contents = [] # hold edited contents
    i = 0 # iterator
    num = start # hold updated residue number
    

    # open .pdb, append contents to contents list
    f = open(filename, 'r')
    contents = f.readlines()
    f.close()


    for line in contents:
        if 'ATOM' in line: # check for atom line
            line_parts = line.split() # hold line contents
            if line_parts[4].isalpha():
                actual_resnum = int(line_parts[5])
            else:
                actual_resnum = int(line_parts[4])
            # format the new line with appropriate residue number, append to newcontents
            if len(line_parts[2]) < 4:
                line_parts[5] = str(num)
                line_format = '{:<4s}{:>7s}  {:<3} {:>3s} {:1s}{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                formatted_list = line_format.format(*line_parts)
                new_contents.append(formatted_list)
            if len(line_parts[2]) == 4:
                line_parts[5] = str(num)
                line_format = '{:<4s}{:>7s} {:<4} {:>3s} {:1s}{:>4s}    {:>8s}{:>8s}{:>8s}  {:>3s}  {:>3s}'
                formatted_list = line_format.format(*line_parts)
                new_contents.append(formatted_list)
            if num < 100:
                print(num)
            #check if next line is a new residue; if so, increment
            if line != contents[-1]:
                next_parts = contents[i+1].split() # check next atom 
                if next_parts[0].startswith('ATOM'): # check if next atom is atom
                    if line_parts[4].isalpha():
                        next_resnum = int(next_parts[5])
                    else:
                        next_resnum = int(next_parts[4])
                    if next_resnum > actual_resnum:
                        num += 1
                        print('**')
            i += 1
        else:
            # append comment lines to new_contents
            new_contents.append(line)
            i += 1
        

    # write new .pdb file
    f = open(newfilename, 'w') 
    for line in new_contents:
        f.write(line)
        f.write('      \n')
    f.close()

    # return list of edited contents
    return newfilename

'''
editChainIDResidue(filename, newfilename, nterm, cterm)
filename: the file you want to edit the chain ID for
newfilename: the output file path
nterm: the name of the nterm (example: 'ACE')
cterm: the name of the cterm (example: 'NME')
'''
# filename = 'something.pdb'
# newfilename = 'something_chainid.pdb'
# editChainIDResidue(filename, newfilename, 'ACE', 'NME')

def formatLine(line, chain_id):
    line_parts = line.split()
    if isFloat(line_parts[-1].strip()):
        segid = line_parts[2][0]
        line_parts.append(segid)
    # check if chain ID exists
    if not hasChainID(line):
        first_four_fields = line_parts[:4]
        first_four_fields.append(chain_id)
        line_parts = first_four_fields + line_parts[4:]
    if line_parts[10] != '0.00':
        line_parts[10] = '0.00'
    string = formatString(line_parts, chain_id=chain_id)
    return string

def addChainIDLipid(filename, protein_chains=((1, -1),), lipids=['POPC', 'CHL1', 'SDPE', 'POPE', 'PSM', 'SOPS', 'POPE', 'POPS', 'SM', 'CHOL', 'DLPG', 'DDPC'], output=None, chain_id='A'):
    # open file
    f = open(filename, 'r')
    contents = f.readlines()
    f.close()
    chain_char = 'A'
    newcontents = []
    residues = ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLU', 'GLN', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL', 'HSD']
    # initialize incrementers
    i = 0
    chain_counter = 0
    current_chain = protein_chains[chain_counter]
    resnr = 0
    k = 0
    last_res = None
    newcontents = []
    atom_types = ('ATOM', 'HETATM')
    model_end = ('TER', 'ENDMDL')
    for line in contents:
        if (line.startswith(atom_types)):
            line_parts = line.split()
            res_name = line_parts[3]
            res_num = line_parts[4]
            res_id = res_name + res_num
            if res_name in residues:
                newline = formatLine(line, chain_id)
                newcontents.append(newline)
                if line != contents[-1]:
                    if contents[i+1].startswith(atom_types):
                        next_res_num = contents[i+1].split()[4]
                        # if next line's res num is the start of a new range, increment chain id
                        if (chain_counter+1 != len(protein_chains)) and (next_res_num == protein_chains[chain_counter+1][0]):
                            chain_id = chr(ord(chain_id)+1)
                            chain_char = chr(ord(chain_char)+1)
                            chain_counter += 1
                            reset = True
                            current_chain = protein_chains[chain_counter]
                    elif contents[i+1].startswith(model_end):
                        chain_id = chr(ord(chain_id)+1)
                        chain_counter += 1
                    else:
                        print(formatLine(line, chain_id))  
            if res_name in lipids:
                k += 1
                newline = formatLine(line, chain_id)
                newcontents.append(newline)
                if line != contents[-1]:
                    if contents[i+1].startswith(atom_types):
                        next_res_num = contents[i+1].split()[4]
                        if next_res_num != res_num:
                            if not chain_id.endswith('Z'):
                                chain_id = chr(ord(chain_id)+1)
                            else:
                                chain_id = 'A'
        else:
            newcontents.append(line)
        i += 1
    if output is None:
        filepath = os.path.join(os.sep.join(filename.split(os.sep)[:-1]))
        if filepath == '':
            if sys.platform == 'win32':
                try:
                    filepath = os.path.join(os.sep.join(filename.split('/')[:-1]))
                    assert filepath != ''
                    filename = filename.split('/')[-1][:-4] + '_chainid.pdb'
                except:
                    filepath = os.getcwd()
                    filename = filepath[:-4] + '_chainid.pdb'
            else:
                filepath = os.getcwd() 
                filename = output[:-4] + '_chainid.pdb'
        else:
            filename = filename.split(os.sep)[-1][:-4] + '_chainid.pdb'
        output = os.path.join(filepath, filename)
    f = open(output, 'w')
    for line in newcontents:
        f.write(line)
    f.close()
        

if __name__ == '__main__':
    editchainID_v2('top.nowat.pdb', 'top.nowat.chain.pdb', renumber_chain=False)