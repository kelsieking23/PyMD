import os
import json
import pandas as pd
from datetime import datetime
import mdtraj
from pymd.mdanalysis.postprocess import PostProcess
import multiprocessing as mp
from pymd.utilities.rewritepdb import writePDB
from collections.abc import Iterable

class Analysis:

    def __init__(self, inp, top, parent=None, **kwargs):
        '''
        For now, takes a dict of parameters from run.py call
        '''
        self.parent = parent
        self._inp = inp
        self._topfile = top
        self.traj = None
        self._traj = None
        self._output = None
        self.job_name = 'analysis'
        self.job_params = {}
        self.load_state = False
        self.__dict__.update(kwargs)

    
    @property
    def inp(self):
        if self.parent is not None:
            return os.path.join(self.parent.root, self._inp)  # type: ignore
        return self._inp

    @property
    def topfile(self):
        if self.parent is not None:
            return os.path.join(self.parent.root, self._topfile)  # type: ignore
        return self._topfile

    @property
    def top(self):
        return mdtraj.load(self.topfile).topology

    def save(self):
        params = {}
        manual_keys = ['parent', 'df', 'matrix', 'traj', '_traj', 'top', 'frames']
        to_dump = {}
        for key, value in self.__dict__.items():
            try:
                json.dumps(value)
                to_dump[key] = value
            except:
                continue
        filename = os.path.join(self.root, 'job_params.json')
        with open(filename, 'w') as f:
            params_dict = json.dumps(to_dump)
            f.write(params_dict)
        self.job_params = params_dict

    @classmethod
    def from_json(cls, path, inp=None, top=None, parent=None, load_traj=False):
        with open(os.path.join(path, 'job_params.json'), 'r') as f:
            params = json.load(f)
        dic = {}
        manual_keys = ['inp', 'top', 'parent', 'df', 'matrix']
        for key, value in params.items():
            if key not in manual_keys:
                dic[key] = value
        for filename in os.listdir(path):
            if filename == params['_output']:
                if filename.endswith('csv'):
                    dic['df'] = pd.read_csv(os.path.join(path, filename), index_col=0)
                if filename.endswith('xvg'):
                    post = PostProcess()
                    dic['df'] = post.getDataFrame(os.path.join(path, filename))
        if parent is not None:
            inp = parent.inp
            top = parent.topfile
        else:
            inp = params['_inp']
            top = params['_topfile']
        if load_traj:
            stride = dic['stride']
            selection = dic['selection']
            b = dic['b']
            e = dic['e']
            if stride != 0:
                traj = mdtraj.load(inp, top=top, stride=stride)
            else:
                traj = mdtraj.load(inp, top=top)
            _traj = traj
            traj = traj.superpose(traj)

            if selection != 'all':
                sele = traj.top.select(selection)
                traj = traj.atom_slice(sele)
            if (e == -1):
                traj = traj.center_coordinates()[b:]
                # self.traj = traj[b:]
            else:
                traj = traj.center_coordinates()[b:e]
            dic['traj'] = traj
            dic['_traj'] = _traj
            dic['frames'] = traj._xyz
        return cls(inp, top, parent, **dic)

    
    @property
    def output(self):
        if self._output is not None:
            return os.path.join(self.root, self._output) # type: ignore
        return None
        # if self.parent is not None:
        #     if not os.path.isdir(os.path.join(self.parent.root, self.job_name)): # type: ignore
        #         os.mkdir(os.path.join(self.parent.root, self.job_name)) # type: ignore
        #     return os.path.join(self.parent.root, self.job_name, self._output) # type: ignore
        # return self._output
    
    @property
    def root(self):
        if self.parent is not None:
            root = os.path.join(self.parent.root, self.job_name)
        else:
            if os.path.dirname(self.inp) == '':
                root =  os.path.join(os.getcwd(), self.job_name)
            else:
                root = os.path.join(os.path.dirname(self.inp), self.job_name)
        if not os.path.isdir(root):
            os.mkdir(root)
        return root

    def loadTrajectory(self, stride=100, selection='backbone', b=0, e=-1):
        if stride != 0:
            traj = mdtraj.load(self.inp, top=self.topfile, stride=stride)
        else:
            traj = mdtraj.load(self.inp, top=self.topfile)
        traj = traj.superpose(traj)
        self._traj = traj.center_coordinates()

        if selection != 'all':
            if isinstance(selection, str):
                sele = self._traj.top.select(selection)
                traj = self._traj.atom_slice(sele)
            if isinstance(selection, Iterable):
                traj = self._traj.atom_slice(selection)
        self.traj = traj
        if (e == -1):
            self.traj = self.traj[b:]
            # self.traj = traj[b:]
        else:
            self.traj = traj[b:e]
            # self.traj = traj[b:e]
        self.stride = stride
        self.selection=selection
        self.b = b
        self.e = e
        self.frames = self.traj._xyz
        # self.top = self.traj.topology
        return self

    @staticmethod
    def now():
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


    def getPartitions(self, nprocs='auto'):
        if nprocs == 'auto':
            nprocs = int(mp.cpu_count() // 2)
        else:
            nprocs = nprocs
        if self.traj is None:
            self.loadTrajectory()
        nframes, _, _ = self.traj._xyz.shape # type: ignore
        interval = int(nframes // nprocs)
        partitions = []
        procid=1
        for i in range(0, nframes, interval):
            data = {
                'b':i,
                'e':i+interval,
                'procid':procid,
            }
            partitions.append(data)
            procid+=1
            if ((i + interval + interval) > nframes) and (i+interval != nframes):
                data = {
                    'b':i+interval,
                    'e':nframes,
                    'procid':procid
                }
                partitions.append(data)
                break
        return partitions, nprocs

    def toPDB(self, index, output, remark=None):
        frame = self._traj._xyz[index]
        chain_index = 0
        chain_id = 'A'
        contents = []
        if remark is not None:
            contents.append('{}\n'.format(remark))
        for z in range(0, len(frame)):
            atom = self._traj.topology._atoms[z]
            if atom.residue.chain.index > chain_index:
                chain_index = atom.residue.chain.index
                chain_id = chr(ord(chain_id) + 1)
            x, y, z = map(self.fixCoordinates, frame[z])
            line = ['ATOM', str(atom.index), atom.name, atom.residue.name, chain_id, str(atom.residue.resSeq), x, y, z, '1.00', '0.00', atom.element.symbol]
            contents.append(line)
        writePDB(contents, output)
        print('Wrote {}'.format(output))

    def fixCoordinates(self, xyz):
        return xyz*10
    
    @staticmethod
    def chain_conversions():
        keys = [i for i in range(0,26)]
        values = list(map(chr, range(ord('A'), ord('Z')+1)))
        return {k:v for (k,v) in zip(keys, values)}