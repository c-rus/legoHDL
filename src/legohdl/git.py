# Project: legohdl
# Script: git.py
# Author: Chase Ruskin
# Description:
#   The Git class. A git object has handy commands availabel for Git 
#   repositories.

import os
from .apparatus import Apparatus as apt

class Git:

    def __init__(self, path):
        self._path = apt.fs(path)
        pass
    
    def getPath(self):
        return self._path

    def commit(self, msg):
        #first identify if has commits available
        keyword = 'Changes to be committed:'
        
        txt = apt.execute('git','-C',self.getPath(),'commit','-m','\"'+msg+'\"','-q', returnoutput=True)
        print(txt)


    def add(self, files):
        '''


        Parameters:
            files (list): list of files to add
        '''
        apt.execute('git','-C')

    @classmethod
    def isValid(cls, path):
        '''
        Checks if a path has a .git/ folder at the root

        Parameters:
            None
        Returns:
            (bool): true if .git/ folder exists at path
        '''
        return os.path.isdir(apt.fs(path)+'.git/')

    def __str__(self):
        return f'''
        {self.__hash__}
        {self._path}
        '''

    pass