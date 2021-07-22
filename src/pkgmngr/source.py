from abc import ABC, abstractmethod
from apparatus import Apparatus as apt
import logging as log
from entity import Entity


class Source(ABC):
    def __init__(self, fpath):
        self._file_path = apt.fs(fpath)
        pass
    
    @abstractmethod
    def decipher(self):
        pass
    pass


class Vhdl(Source):

    def decipher(self, availLibs, design_book, cur_lib):
        log.info("Deciphering VHDL file...")
        lib_headers = list()
        pre_files = []
        entity_bank = dict()
        with open(self._file_path, 'r') as file:
            in_entity = in_arch = in_true_arch = in_pkg = False
            entity_name = arch_name = pkg_name =  None
            extern_libs = list()
            port_txt = ''
            ent = None
            #read through the VHDL file
            for line in file.readlines():
                #parse line into a list of its words
                words = line.split()
                if(len(words) == 0): #skip if its a blank line
                    continue
                #find when entering an entity, architecture, or package
                if(words[0].lower() == "entity"):
                    in_entity = True
                    entity_name = words[1].lower()
                    #stash all "uses" from above
                    ent = Entity(self._file_path, cur_lib+'.'+entity_name, lib_headers, pre_files)
                    ent.setExterns(extern_libs)
                    extern_libs = list()
                    pre_files = []
                    lib_headers = list()
                if(words[0].lower() == "package"):
                    in_pkg = True
                    pkg_name = words[1].lower()
                    #stash all "uses" from above
                    lib_headers = list()
                if(words[0].lower() == "architecture"):
                    in_arch = True
                    arch_name = words[1]
                #find "use" declarations
                if(words[0].lower() == "use" and not in_entity and not in_arch and not in_pkg):
                    impt = words[1].split('.')
                    #do not add if the library is not work or library is not in list of available custom libs
                    if(impt[0].lower() == 'work' or impt[0].lower() in availLibs):
                        package_name = impt[1].replace(";",'').lower()
                        if(impt[0].lower() == 'work'):
                            package_name = cur_lib+'.'+package_name
                        elif(impt[0].lower() in availLibs):
                            package_name = impt[0].lower()+'.'+package_name

                        if(impt[0].lower() in availLibs):
                            extern_libs.append((package_name,design_book[package_name]))
                            pre_files.append(design_book[package_name])
                        else:
                            #print("file needed for entity as use:",design_book[package_name])
                            pre_files.append(design_book[package_name])
                        #lib_headers.append(words[1][:len(words[1])-1])
                        comps = self.grabComponents(design_book[package_name], impt[0])
                        
                        #3 parts to word -> library.package.entity; or library.package.all;
                        if(len(impt) == 3):
                            suffix = impt[2].lower().replace(";",'')
                            if(suffix == 'all'): # add all found entities from pkg as dependencies of design
                                lib_headers = lib_headers + comps
                            else: #it is a specific component
                                lib_headers.append(impt[0]+'.'+suffix)
                        else: # a third piece was not given, check instantiations with this pkg.entity format in architecture
                            pass
                #determine if it can be a disqualified testbench entity
                if(in_entity):
                    keywords = line.lower().split()
                    if("in" in keywords or "out" in keywords or "inout" in keywords):
                        ent.setTb(False)
                    port_txt = port_txt + line

                #find component declarations
                if(words[0].lower() == "component" and in_arch):
                    ent.addDependency(cur_lib+'.'+words[1].lower())
                if(words[0].lower() == "component" and in_pkg):
                    pass

                if(in_arch):
                    if(words[0].lower() == 'begin'):
                        in_true_arch = True
                #find instantiations by library.package.entity
                if(len(words) > 2 and words[1] == ':' and in_arch and in_true_arch):
                    inst = words[2]
                    inst_parts = inst.split('.')
                    
                    e_name = inst_parts[len(inst_parts)-1].lower()
                    p_name = inst_parts[len(inst_parts)-2].lower()
                    l_name = inst_parts[0].lower()
                    pre_header = l_name+'.'+p_name
                    
                    if(len(inst_parts) > 2):
                        #add to external references if it is not from work
                        if(inst_parts[0].lower() != 'work'):
                            ent.addExtern((l_name+'.'+p_name,design_book[l_name+'.'+p_name]))
                            ent.addPreFile(design_book[l_name+'.'+p_name])
                        else:
                            l_name = cur_lib.split('.')[0]
                            ent.addPreFile(design_book[l_name+'.'+p_name])
                            #print("file needed for entity as use:",design_book[l_name+'.'+p_name])

                    if(l_name+'.'+p_name in design_book.keys()):
                        ent.addDependency(l_name+'.'+e_name)
                        #ent.appendFiles(design_book[p_name])
                        #print("file needed for entity:",ent.getName(),design_book[p_name])

                #detect when outside of entity, architecture, or package
                if(words[0].lower() == "end"):
                    if(in_entity and (entity_name+";" in words or words[1].lower().count("entity"))):
                        in_entity = False
                        ent.setPorts(port_txt)
                        port_txt = ''
                    if(in_arch and (arch_name+";" in words or words[1].lower().count("architecture"))):
                        entity_bank[cur_lib+'.'+ent.getName()] = ent
                        in_arch = in_true_arch = False
                    if(in_pkg and (pkg_name+";" in words or words[1].lower().count("package"))):
                        in_pkg = False
                pass
            file.close()
            pass
        return entity_bank
        pass

    def grabComponents(self, filepath, pre_header):
            comp_list = list()
            with open(filepath, 'r') as file:
                for line in file.readlines():
                    words = line.split()
                    if(len(words) == 0): #skip if its a blank line
                        continue
                    if(words[0].lower() == "component"):
                        comp_list.append(pre_header+'.'+words[1].lower())
                file.close()
            #print("Components:",comp_list)
            return comp_list

    pass