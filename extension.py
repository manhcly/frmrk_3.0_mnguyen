#! /usr/bin/python
from __future__ import print_function
import filecmp
import os.path
import sys

from common import *

class dircmp(filecmp.dircmp):
    """
    Compare the content of dir1 and dir2. In contrast with filecmp.dircmp, this
    subclass compares the content of files with the same path.
    """
    def phase3(self):
        """
        Find out differences between common files.
        Ensure we are using content comparison with shallow=False.
        """
        fcomp = filecmp.cmpfiles(self.left, self.right, self.common_files,shallow=False)
        self.same_files, self.diff_files, self.funny_files = fcomp

class extension:
    def __init__(self,val_root=None,val_parse=None,sw_root=None,sw_ref=None,sw_build=None,type=None,ext_files_path=None):

        if type: self.type= type
        else: self.type='atf'

        if self.type == 'atf':
            self.sw_type = 'apm-atf'
            #self.EXTENSION_FILE = ATF_VAL_EXTENSION_FILE
            self.VAL_EXTENSION_IGNORE = ATF_VAL_EXTENSION_IGNORE
            self.subdir = 'osprey'
        elif self.type == 'aptio':
            self.sw_type = 'apm-ami-aptiov'
            #self.EXTENSION_FILE = APTIO_VAL_EXTENSION_FILE
            self.VAL_EXTENSION_IGNORE = APTIO_VAL_EXTENSION_IGNORE
            self.subdir = 'osprey'

        elif self.type == 'linux':
            self.sw_type = 'linux'
            #self.EXTENSION_FILE = LINUX_VAL_EXTENSION_FILE
            self.VAL_EXTENSION_IGNORE = LINUX_VAL_EXTENSION_IGNORE
            self.subdir = 'centOS'

        #########################################################################################################
        # SW release folder
        if sw_root: sw_default_root = sw_root
        else: sw_default_root = '/projects/hcm/skylark/users/nhnguyen/frmwrk/sw_release'

        #########################################################################################################
        # SW reference release to get the VAL Extensions
        sw_default_ref = '4.04.25-beta'
        if sw_ref == None:
            self.sw_root = os.path.join(sw_default_root,sw_default_ref,self.subdir)
            self.sw_ref = sw_default_ref
        else:
            path = os.path.join(sw_default_root,sw_ref,self.subdir)
            if os.path.isdir(path) :
                self.sw_root = path
                self.sw_ref = sw_ref
            else:
                self.sw_root = os.path.join(sw_default_root,sw_default_ref,self.subdir)
                self.sw_ref = sw_default_ref
        self.sw_root = os.path.join(self.sw_root,self.sw_type)



        #########################################################################################################
        # VAL reference source to compare with SW reference source to build the VAL Extensions
        if val_root: self.val_root   = val_root
        else: self.val_root = '/projects/hcm/skylark/users/nhnguyen/frmwrk/GIT/xval_skylark'
        if self.type == 'linux':
            self.val_root = os.path.join(self.val_root,'linux_frw',self.type)
        else:
            self.val_root = os.path.join(self.val_root,self.type)

        #########################################################################################################
        # VAL Extensions folders
        if val_parse : self.val_parse = val_parse
        else: self.val_parse = '/projects/hcm/skylark/users/nhnguyen/frmwrk/VAL_parse'

        self.diff_root = os.path.join(self.val_parse,'diff_DB',self.sw_ref)
        self.ext_root = os.path.join(self.diff_root,'Extensions')
        self.sw_ref   = os.path.join(self.diff_root,'.ref/SW')
        self.val_ref  = os.path.join(self.diff_root,'.ref/VAL')


        #########################################################################################################
        # SW release from what we will add the VAL extensions to have an 'updated' VAL source
        sw_default_build = '4.04.27-beta'
        if sw_build == None:
            self.sw_release = os.path.join(sw_default_root,sw_default_build,self.subdir)
            self.sw_build = sw_default_build
        else:
            path = os.path.join(sw_default_root,sw_build,self.subdir)
            if os.path.isdir(path) :
                self.sw_release = path
                self.sw_build = sw_build
            else:
                raise Exception("Path '%s' doesn't exist"%path)
                self.sw_release = os.path.join(sw_default_root,sw_default_build,self.subdir)
                self.sw_build = sw_default_build
        self.sw_release = os.path.join(self.sw_release,self.sw_type)
        #print(self.sw_release)
        #########################################################################################################
        # VAL Updated source folders
        self.val_src = os.path.join(self.val_parse,'val_extended_src',self.sw_build)



        #########################################################################################################
        # Text file to list all the VAL files contain extensions
        self.EXTENSION_FILE = []
        if ext_files_path == None:
           ext_files_path  = 'val_ext_files'
        if not os.path.isabs(ext_files_path):
            path = os.popen('pwd').read().strip('\n')
            abs_path = os.path.join(path,ext_files_path)
        else:
            abs_path = ext_files_path

        with open(abs_path) as f:
            lines = f.readlines()
        #print(self.EXTENSION_FILE)
        for l in lines:
            #if l.isspace(): continue
            if l.find("#") != -1 : continue
            if l.find(self.type) == -1 : continue
            if l.strip('\n') not in self.EXTENSION_FILE:
                self.EXTENSION_FILE.append(l.strip('\n'))
        #print(self.EXTENSION_FILE)
        self.DEBUG    = False
        #self.DEBUG    = True


    def __del__(self):
        del self.val_root
        del self.sw_root
        del self.ext_root
        del self.diff_root
        del self.val_ref
        del self.sw_ref
        del self.sw_release
        del self.sw_build
        del self.type
        del self.sw_type
        del self.val_parse


    #==============================
    # Private functions
    #==============================
    def __debugPrint(self,str):
        if self.DEBUG:
            print (str)

    def __createPath(self,path):
        if not os.path.isdir(path):
            os.makedirs(path)



    def __diff_file_2(self,src_path,dst_path):
        i           = dst_path.rfind('/'+self.type+'/')
        diff_path   = dst_path[i+1:]
        i           = diff_path.rfind('/')
        path        = os.path.join(self.ext_root,diff_path[:i])
        fname       = diff_path[i:].strip('/')
        self.__createPath(path)
        out = os.path.join(path,fname)

        '''
        Read SW and VAL files, strip down the blanc lines and restore as reference
        '''
        buffer      = []
        sw_lines    = []
        val_lines   = []
        #if src_path.find('xhci.c') == -1 : return #DEBUG
        sw_file     = open(src_path)
        for line in sw_file:
            sw_lines.append(line)
        sw_file.close()

        val_file = open(dst_path)
        for line in val_file:
            val_lines.append(line)
        val_file.close()


        sw_len      = len(sw_lines)     # Number of line in SW file
        val_len     = len(val_lines)    # Number of line in VAL file
        idx_diff    = 0                 # Difference between no of line between SW and VAL
        replace_idxs=[]                 # Index of lines to replace in SW file



        # Go through all lines in SW file
        for sw_idx in range(sw_len):
            diff    = False # Flag of difference between SW and VAL
            add     = False # Flag to add lines from VAL to SW file

            # Don't treat if this line is marked "replaced"
            if sw_idx in replace_idxs : continue

            # If there is a difference between SW and VAL
            if sw_lines[sw_idx] != val_lines[sw_idx+idx_diff]:
                self.__debugPrint("--------------------------------------------------------------------------------")
                self.__debugPrint("missmatch found in line: sw_idx=%d - val_idx=%d"%(sw_idx, sw_idx+idx_diff))
                self.__debugPrint("sw_len = %d -- val_len = %d"%(sw_len,val_len))
                self.__debugPrint("sw_idx = %d -- idx_diff = %d" %(sw_idx,idx_diff))
                self.__debugPrint("SW[%d]: '%s'"%(sw_idx,sw_lines[sw_idx].strip('\n')))
                self.__debugPrint("VAL[%d]:'%s'"%(sw_idx+idx_diff,val_lines[sw_idx+idx_diff].strip('\n')))
                diff    = True
                # Stored previous lines
                # Normally we store only 1 line up,except when line size is too small or
                # line is in SPECIAL_LINES, we will store up to two lines
                match_lines = []
                cnt         = 5
                for pre_idx in range(sw_idx-1,-1,-1):
                    match_lines.append('=%s'%sw_lines[pre_idx].strip('\n'))
                    if sw_lines[pre_idx] != '\n':
                        if (len(sw_lines[pre_idx]) < LINE_SIZE_MIN) or (sw_lines[pre_idx].strip('\n') in SPECIAL_LINES):
                            self.__debugPrint("DEBUG '%s'"%sw_lines[pre_idx])
                            for i in range(1,5):
                                match_lines.append('=%s'%sw_lines[pre_idx-i].strip('\n'))
                            break
                        else: break

                # Search if this is an Addition or Replacement
                diff_lines = []
                found = False
                self.__debugPrint("DEBUG0")
                line_change = 0
                n_idx = sw_idx
                # SW line is NOT an empty line
                if not sw_lines[sw_idx].isspace():
                    for val_idx in range(sw_idx+idx_diff,val_len):
                        # Search if we find the same SW line in VAL file from the actual val_idx = sw_idx + idx_diff
                        if sw_lines[sw_idx] == val_lines[val_idx]:
                            self.__debugPrint("val_idx = %d"%val_idx)
                            found = True
                            break
                # SW IS an empty line
                else:
                    while 1:
                        n_idx += 1
                        if not sw_lines[n_idx].isspace():
                            break
                        if n_idx == sw_len: break
                    if n_idx < sw_len:
                        self.__debugPrint("sw_idx   =%d"%sw_idx)
                        self.__debugPrint("n_idx    =%d"%n_idx)
                        for val_idx in range(sw_idx+idx_diff,val_len):
                            if sw_lines[n_idx] == val_lines[val_idx]:
                                self.__debugPrint("FOUND")
                                self.__debugPrint("Rematch val_idx = %d and sw_idx = %d"%(val_idx,n_idx))
                                self.__debugPrint("'%s'"%val_lines[val_idx].strip('\n'))
                                found = True
                                line_change = n_idx - sw_idx
                                break
                        if line_change != 0:
                            self.__debugPrint("line_change=%d"%line_change)
                            for i in range(sw_idx+1,n_idx+1):
                               self.__debugPrint("IGNORE %d"%i)
                               replace_idxs.append(i)
                self.__debugPrint("DEBUG1")
                self.__debugPrint("idx_diff =%d"%idx_diff)
                self.__debugPrint("found = %r"%found)
                add_size    = 0 # Number of line that will be added from VAL to SW

                # If we found the same SW line in VAL
                self.__debugPrint("line_change =%d"%line_change)
                if line_change == 0:
                    if found == True:
                        # We double check if that line is present only 1 time in SW or not
                        if sw_lines[sw_idx] not in sw_lines[sw_idx+1:]:
                            # If this is the only reference of this line then we will add
                            # this part of code from VAL to SW it means that is an Addition of code
                            add = True
                            add_size    = val_idx - sw_idx - idx_diff # Number of lines will be added
                            idx_diff    = val_idx - sw_idx # Update difference of index between SW and VAL
                            self.__debugPrint("Updated idx_diff= %d -- add_size = %d"%(idx_diff,add_size))
                        else:
                            # If not, we continue to same searching algo with the next line in SW.
                            # On the same process, we calcul the start_idx and stop_idx in VAL,
                            # only in case if start_idx > stop_idx, it means that is NOT a Addition, it's a Replacement
                            self.__debugPrint("There are another same line in SW source")
                            start_idx = val_idx
                            for sw_idx_2 in range(sw_idx + 1, sw_len):
                                next_sw_line = sw_lines[sw_idx_2]
                                if next_sw_line in val_lines[sw_idx_2 + idx_diff:]:
                                    stop_idx = sw_idx_2 + idx_diff + val_lines[sw_idx_2 + idx_diff:].index(next_sw_line)
                                    self.__debugPrint("start_idx = %d"%start_idx)
                                    self.__debugPrint("stop_idx  = %d"%stop_idx)
                                    if start_idx >= stop_idx:
                                        add = False
                                    else:
                                        add = True
                                        add_size    = val_idx - sw_idx - idx_diff # Number of lines will be added
                                        idx_diff    = idx_diff + add_size # Update difference of index between SW and VAL
                                        self.__debugPrint("1 idx_diff =%d"%idx_diff)
                                        self.__debugPrint("1 add_size =%d"%add_size)
                                    break

                    self.__debugPrint("DEBUG2")
                    self.__debugPrint("idx_diff =%d"%idx_diff)
                    if add == True :
                        self.__debugPrint("ADD")
                        # Add VAL lines to buffer with pre-fixe '+'
                        self.__debugPrint("Add in SW[%d] - add_size=%d - idx_diff=%d"%(sw_idx,add_size,idx_diff))
                        for idx in range(idx_diff-add_size,idx_diff):
                            self.__debugPrint("val_idx = %d "%(idx+sw_idx-line_change))
                            diff_lines.append('+%s'%val_lines[sw_idx+idx-line_change].strip('\n'))
                            self.__debugPrint('+%s'%val_lines[sw_idx+idx-line_change].strip('\n'))
                        self.__debugPrint("End of add in SW[%d] VAL[%d]- add_size=%d - idx_diff=%d"%(sw_idx,val_idx,add_size,idx_diff))
                    else:
                        self.__debugPrint("REPLACE")
                        # In Replacement process, we will find the next line in SW that match with line in VAL,
                        # Lines in between in SW will be stored as 'replaced' with pre-fixe '-'
                        # Lines in between in VAL will be stored as 'added' with pre-fixe '+'
                        replace_done = False    # Flag to mark when replacement is done
                        self.__debugPrint("replace start in SW[%d] VAL[%d]"%(sw_idx,sw_idx+idx_diff))
                        # Add the SW line to buffer with pre-fixe '-'
                        diff_lines.append('-%s'%sw_lines[sw_idx].strip('\n'))
                        self.__debugPrint('-%s'%sw_lines[sw_idx].strip('\n'))
                        # Store the index of this replaced SW line, we will not process this line anymore
                        replace_idxs.append(sw_idx)
                        replace_size = 1 # Number of replaced SW lines
                        # Continue to search next SW line with index sw_idx+1 until we find this same line
                        # in VAL
                        for sw_idx_2 in range(sw_idx+1,sw_len):
                            self.__debugPrint("sw_idx_2 = %d"%sw_idx_2)
                            line = sw_lines[sw_idx_2]
                            # If this SW[sw_idx_2] line is not in the rest of VAL, it means that this line
                            # is in the 'replacement SW lines block'
                            if line not in val_lines[sw_idx+idx_diff:]:
                                diff_lines.append('-%s'%line.strip('\n'))
                                self.__debugPrint('-%s'%line.strip('\n'))
                                replace_idxs.append(sw_idx_2)
                                replace_size += 1
                            else:
                                # If this SW[sw_idx_2] is in the rest of VAL, we double-check that next 3 lines are
                                # the same with ones in SW
                                found_val_idx = sw_idx + idx_diff + val_lines[sw_idx+idx_diff:].index(line)
                                replace_done= True
                                for cnt in range(3):
                                    if (val_len - found_val_idx > cnt) or (sw_len - sw_idx_2 > cnt):
                                        if val_lines[found_val_idx+cnt] != sw_lines[sw_idx_2+cnt]:
                                            replace_done = False
                                            break
                                    else:
                                        self.__debugPrint("DEBUG replace_done")
                                        self.__debugPrint("val_len = %d"%val_len)
                                        self.__debugPrint("found_val_idx = %d" %found_val_idx)
                                        self.__debugPrint("cnt = %d" %cnt)
                                        self.__debugPrint("sw_len = %d" %sw_len)
                                        self.__debugPrint("sw_idx_2 = %d" %sw_idx_2)

                                if replace_done == True: # it means we found the end of 'replacement SW lines block'
                                    val_idx = found_val_idx
                                    # calcul size of 'added block' for VAL
                                    add_size        = val_idx - sw_idx - idx_diff
                                    # recalcul the difference of index between SW and VAL
                                    idx_diff    = val_idx - sw_idx_2
                                    self.__debugPrint("replace re-match in SW[%d] VAL[%d]: '%s'"%(sw_idx_2,val_idx,line.strip('\n')))
                                    self.__debugPrint("<1> add_size    = %d"%add_size)
                                    self.__debugPrint("<1> idx_diff    = %d"%idx_diff)
                                    self.__debugPrint("<1> val_idx     = %d"%val_idx)
                                    self.__debugPrint("<1> replace_size= %d"%replace_size)
                                    break
                                else:
                                    self.__debugPrint("replace_done = False")
                                    diff_lines.append('-%s'%line.strip('\n'))
                                    self.__debugPrint('-%s'%line.strip('\n'))
                                    replace_idxs.append(sw_idx_2)
                                    replace_size += 1


                        # If we already found the end of replacement
                        if replace_done == True:
                            # Add the VAL lines to buffer with pre-fixe '+'
                            for idx in range(idx_diff-add_size,idx_diff):
                                diff_lines.append('+%s'%val_lines[sw_idx_2+idx].strip('\n'))
                                self.__debugPrint('+%s'%val_lines[sw_idx_2+idx].strip('\n'))
                        else:
                            # If we didn't find the end of replacement even when we touch the end of SW file
                            # we will need to replace those 'replaced SW lines' with the rest of VAL file
                            self.__debugPrint("<2> add_size    = %d"%add_size)
                            self.__debugPrint("<2> idx_diff    = %d"%idx_diff)
                            self.__debugPrint("<2> replace_size= %d"%replace_size)
                            for idx in range(idx_diff-add_size,idx_diff):
                                # Add the rest of VAL lines to buffer with pre-fixe '+'
                                diff_lines.append('+%s'%val_lines[sw_idx_2+idx].strip('\n'))
                                self.__debugPrint('+%s'%val_lines[sw_idx_2+idx].strip('\n'))
                                # Update difference of index
                                idx_diff += 1
                            # This is for the SW line that we add in buffer in the beginning
                            # of the replacement process
                            #idx_diff -=1
                            idx_diff = idx_diff - replace_size
                            self.__debugPrint("<2.1> add_size    = %d"%add_size)
                            self.__debugPrint("<2.1> idx_diff    = %d"%idx_diff)
                            self.__debugPrint("<2.1> replace_size= %d"%replace_size)

                else:
                    self.__debugPrint("SPECIAL-LINE REPLACE")
                    if found == True:
                        replace_size =0
                        for i in range(sw_idx, n_idx):
                            replace_size+=1
                            diff_lines.append('-%s'%sw_lines[i].strip('\n'))
                            self.__debugPrint('-%s'%sw_lines[i].strip('\n'))

                        add_size = 0
                        for i in range(sw_idx+idx_diff,val_idx):
                            add_size+=1
                            diff_lines.append('+%s'%val_lines[i].strip('\n'))
                            self.__debugPrint('+%s'%val_lines[i].strip('\n'))

                        idx_diff = idx_diff + add_size - replace_size
                        self.__debugPrint("<3> add_size    = %d"%add_size)
                        self.__debugPrint("<3> replace_size= %d"%replace_size)
                        self.__debugPrint("<3> idx_diff    = %d"%idx_diff)


                # Add the Beginning Pattern
                buffer.append(begin_pattern)
                # Add lines in matched buffer
                for line in reversed(match_lines):
                    buffer.append(line)
                # Add lines in different buffer
                for line in diff_lines:
                    buffer.append(line)
                # Add end pattern
                buffer.append(end_pattern)
                self.__debugPrint("--------------------------------------------------------------------------------\n")

        # If there is still difference between sw_len + idx_diff and val_len
        # we need to add a last difference block 'End of file Pattern'
        if sw_len + idx_diff < val_len:
            self.__debugPrint("sw_len=%d -- val_len=%d -- idx_diff==%d"%(sw_len,val_len,idx_diff))
            buffer.append(end_of_file_pattern)
            for idx in range(sw_len+idx_diff,val_len):
                l = val_lines[idx].strip('\n')
                buffer.append(l)

        # Dump file out
        f = open(out,'w')
        f.write("######################################################################\n")
        f.write("### Validation Extensions of %s ###\n" %diff_path)
        f.write("######################################################################\n")
        f.write("\n\n")
        for l in buffer:
            f.write('%s\n'%l)
        f.close()









#    '''
#    Function to get the differences between two files
#    '''
#    def __diff_file(self,src_path,dst_path):
#        i           = dst_path.rfind('/'+self.type+'/')
#        diff_path   = dst_path[i+1:]
#        i           = diff_path.rfind('/')
#        path        = os.path.join(self.ext_root,diff_path[:i])
#        fname       = diff_path[i:].strip('/')
#        self.__createPath(path)
#        out = os.path.join(path,fname)
#
#        '''
#        Read SW and VAL files, strip down the blanc lines and restore as reference
#        '''
#        buffer      = []
#        sw_lines    = []
#        val_lines   = []
##        if src_path.find('Makefile') == -1 : return #DEBUG
#        sw_file     = open(src_path)
#        path        = os.path.join(self.sw_ref,diff_path[:i])
#        self.__createPath(path)
#        tmp = open(os.path.join(path,fname),"w")
#        for line in sw_file:
#            #if line.isspace() : continue
#            sw_lines.append(line)
#            tmp.write(line)
#        tmp.close()
#        sw_file.close()
#
#        val_file = open(dst_path)
#        path        = os.path.join(self.val_ref,diff_path[:i])
#        self.__createPath(path)
#        tmp =open(os.path.join(path,fname),"w")
#        for line in val_file:
#            #if line.isspace() : continue
#            val_lines.append(line)
#            tmp.write(line)
#        tmp.close()
#        val_file.close()
#
#
#        sw_len      = len(sw_lines)     # Number of line in SW file
#        val_len     = len(val_lines)    # Number of line in VAL file
#        idx_diff    = 0                 # Difference between no of line between SW and VAL
#        replace_idxs=[]                 # Index of lines to replace in SW file
#
#        # Go through all lines in SW file
#        for sw_idx in range(sw_len):
#            diff    = False # Flag of difference between SW and VAL
#            add     = False # Flag to add lines from VAL to SW file
#
#            # Don't treat if this line is marked "replaced"
#            if sw_idx in replace_idxs : continue
#
#            # If there is a difference between SW and VAL
#            if sw_lines[sw_idx] != val_lines[sw_idx+idx_diff]:
#                self.__debugPrint("--------------------------------------------------------------------------------")
#                self.__debugPrint("missmatch found in line: sw_idx=%d - val_idx=%d"%(sw_idx, sw_idx+idx_diff))
#                self.__debugPrint("sw_len = %d -- val_len = %d"%(sw_len,val_len))
#                self.__debugPrint("sw_idx = %d -- idx_diff = %d" %(sw_idx,idx_diff))
#                self.__debugPrint("SW[%d]: '%s'"%(sw_idx,sw_lines[sw_idx].strip('\n')))
#                self.__debugPrint("VAL[%d]:'%s'"%(sw_idx+idx_diff,val_lines[sw_idx+idx_diff].strip('\n')))
#                diff    = True
#                # Stored previous lines
#                # Normally we store only 1 line up,except when line size is too small or
#                # line is in SPECIAL_LINES, we will store up to two lines
#                match_lines = []
#                brk         = False
#                cnt         = 5
#                for pre_idx in range(sw_idx-1,-1,-1):
#                    match_lines.append('=%s'%sw_lines[pre_idx].strip('\n'))
#                    if brk: break
#                    if sw_lines[pre_idx] != '\n':
#                        if (len(sw_lines[pre_idx]) < LINE_SIZE_MIN) or (sw_lines[pre_idx].strip('\n') in SPECIAL_LINES):
#                        #if (sw_lines[pre_idx].strip('\n') in SPECIAL_LINES):
#                            for i in range(1,5):
#                                match_lines.append('=%s'%sw_lines[pre_idx-i].strip('\n'))
#                            break
#                        else: break
#
#                # Search if this is an Addition or Replacement
#                diff_lines = []
#                found = False
#
#                self.__debugPrint("DEBUG0")
##                for val_idx in range(sw_idx+idx_diff,val_len):
##                    # Search if we find the same SW line in VAL file from the actual val_idx = sw_idx + idx_diff
##                    if sw_lines[sw_idx] == val_lines[val_idx]:
##                        self.__debugPrint("val_idx = %d"%val_idx)
##                        if not sw_lines[sw_idx].isspace():
##                            found = True
##                            break
##                        else:
##                            n_idx = sw_idx + 1
##                            while 1:
##                                if not sw_lines[n_idx].isspace():
##                                    break
##                                n_idx += 1
##                                if n_idx == sw_len: break
##                            found = True
##                            self.__debugPrint("sw_idx   =%d"%sw_idx)
##                            self.__debugPrint("n_idx    =%d"%n_idx)
##                            for i in range(sw_idx,n_idx):
##                                if sw_lines[i] != val_lines[i+idx_diff]:
##                                    found = False
##                                    break
##                            if found == True:
##                                for i in range(sw_idx,n_idx):
##                                    self.__debugPrint("IGNORE %d"%i)
##                                    replace_idxs.append(i)
##                            break
#
#                line_change = 0
#                if not sw_lines[sw_idx].isspace():
#                    for val_idx in range(sw_idx+idx_diff,val_len):
#                        # Search if we find the same SW line in VAL file from the actual val_idx = sw_idx + idx_diff
#                        if sw_lines[sw_idx] == val_lines[val_idx]:
#                            self.__debugPrint("val_idx = %d"%val_idx)
#                            found = True
#                            break
#                else:
#                    n_idx = sw_idx
#                    while 1:
#                        n_idx += 1
#                        if not sw_lines[n_idx].isspace():
#                            break
#                        if n_idx == sw_len: break
#                    if n_idx < sw_len:
#                        self.__debugPrint("sw_idx   =%d"%sw_idx)
#                        self.__debugPrint("n_idx    =%d"%n_idx)
#                        for val_idx in range(sw_idx+idx_diff,val_len):
#                            if sw_lines[n_idx] == val_lines[val_idx]:
#                                self.__debugPrint("FOUND")
#                                self.__debugPrint("val_idx = %d"%val_idx)
#                                self.__debugPrint("'%s'"%val_lines[val_idx].strip('\n'))
#                                #found = True
#                                line_change = n_idx - sw_idx
#                                break
#                        if line_change != 0:
#                            for i in range(sw_idx+1,n_idx+1):
#                               self.__debugPrint("IGNORE %d"%i)
#                               replace_idxs.append(i)
#
#                self.__debugPrint("DEBUG1")
#                self.__debugPrint("found = %r"%found)
#                add_size    = 0 # Number of line that will be added from VAL to SW
#                # If we found the same SW line in VAL
#                if found == True:
#                    # We double check if that line is present only 1 time in SW or not
#                    if sw_lines[sw_idx] not in sw_lines[sw_idx+1:]:
#                        # If this is the only reference of this line then we will add
#                        # this part of code from VAL to SW it means that is an Addition of code
#                        add = True
#                        add_size    = val_idx - sw_idx - idx_diff # Number of lines will be added
#                        idx_diff    = val_idx - sw_idx            # Update difference of index between SW and VAL
#                        self.__debugPrint("Updated idx_diff= %d"%idx_diff)
#                    else:
#                        # If not, we continue to same searching algo with the next line in SW.
#                        # On the same process, we calcul the start_idx and stop_idx in VAL,
#                        # only in case if start_idx > stop_idx, it means that is NOT a Addition, it's a Replacement
#                        self.__debugPrint("There are another same line in SW source")
#                        start_idx = val_idx
#                        for sw_idx_2 in range(sw_idx + 1, sw_len):
#                            next_sw_line = sw_lines[sw_idx_2]
#                            if next_sw_line in val_lines[sw_idx_2 + idx_diff:]:
#                                stop_idx = sw_idx_2 + idx_diff + val_lines[sw_idx_2 + idx_diff:].index(next_sw_line)
#                                self.__debugPrint("start_idx = %d"%start_idx)
#                                self.__debugPrint("stop_idx  = %d"%stop_idx)
#                                if start_idx > stop_idx:
#                                    add = False
#                                else:
#                                    add = True
#                                    add_size    = val_idx - sw_idx - idx_diff # Number of lines will be added
#                                    idx_diff    = idx_diff + add_size # Update difference of index between SW and VAL
#                                break
#
#                self.__debugPrint("DEBUG2")
#                if add == True :
#                    self.__debugPrint("ADD")
#                    # Add VAL lines to buffer with pre-fixe '+'
#                    self.__debugPrint("Add in SW[%d] - add_size=%d - idx_diff=%d"%(sw_idx,add_size,idx_diff))
#                    for idx in range(idx_diff-add_size,idx_diff):
#                        diff_lines.append('+%s'%val_lines[sw_idx+idx].strip('\n'))
#                        self.__debugPrint('+%s'%val_lines[sw_idx+idx].strip('\n'))
#                    self.__debugPrint("End of add in SW[%d] VAL[%d]- add_size=%d - idx_diff=%d"%(sw_idx,val_idx,add_size,idx_diff))
#                else:
#                    self.__debugPrint("REPLACE")
#                    # In Replacement process, we will find the next line in SW that match with line in VAL,
#                    # Lines in between in SW will be stored as 'replaced' with pre-fixe '-'
#                    # Lines in between in VAL will be stored as 'added' with pre-fixe '+'
#                    replace_done = False    # Flag to mark when replacement is done
#                    self.__debugPrint("replace start in SW[%d] VAL[%d]"%(sw_idx,sw_idx+idx_diff))
#                    # Add the SW line to buffer with pre-fixe '-'
#                    diff_lines.append('-%s'%sw_lines[sw_idx].strip('\n'))
#                    self.__debugPrint('-%s'%sw_lines[sw_idx].strip('\n'))
#                    # Store the index of this replaced SW line, we will not process this line anymore
#                    replace_idxs.append(sw_idx)
#                    replace_size = 1 # Number of replaced SW lines
#                    # Continue to search next SW line with index sw_idx+1 until we find this same line
#                    # in VAL
#                    for sw_idx_2 in range(sw_idx+1,sw_len):
#                        line = sw_lines[sw_idx_2]
#                        # If this SW[sw_idx_2] line is not in the rest of VAL, it means that this line
#                        # is in the 'replacement SW lines block'
#                        if line not in val_lines[sw_idx+idx_diff:]:
#                            diff_lines.append('-%s'%line.strip('\n'))
#                            self.__debugPrint('-%s'%line.strip('\n'))
#                            replace_idxs.append(sw_idx_2)
#                            replace_size += 1
#                        else:
#                            # If this SW[sw_idx_2] is in the rest of VAL, it means we found the end of
#                            # 'replacement SW lines block'
#                            replace_done= True
#                            # recalcul the actual val_idx
#                            val_idx     = sw_idx + idx_diff + val_lines[sw_idx+idx_diff:].index(line)
#                            # calcul size of 'added block' for VAL
#                            add_size        = val_idx - sw_idx - idx_diff
#                            # recalcul the difference of index between SW and VAL
#                            idx_diff    = val_idx - sw_idx_2
#                            self.__debugPrint("replace re-match in SW[%d] VAL[%d]: '%s'"%(sw_idx_2,val_idx,line.strip('\n')))
#                            self.__debugPrint("1 add_size    = %d"%add_size)
#                            self.__debugPrint("1 idx_diff    = %d"%idx_diff)
#                            self.__debugPrint("1 val_idx     = %d"%val_idx)
#                            self.__debugPrint("1 replace_size= %d"%replace_size)
#                            break
#
#                    # If we already found the end of replacement
#                    if replace_done == True:
#                        # Add the VAL lines to buffer with pre-fixe '+'
#                        for idx in range(idx_diff-add_size,idx_diff):
#                            diff_lines.append('+%s'%val_lines[sw_idx_2+idx].strip('\n'))
#                            self.__debugPrint('+%s'%val_lines[sw_idx_2+idx].strip('\n'))
#                    else:
#                        # If we didn't find the end of replacement even when we touch the end of SW file
#                        # we will need to replace those 'replaced SW lines' with the rest of VAL file
#                        self.__debugPrint("2 add_size    = %d"%add_size)
#                        self.__debugPrint("2 idx_diff    = %d"%idx_diff)
#                        self.__debugPrint("2 replace_size= %d"%replace_size)
#                        for idx in range(idx_diff-add_size,idx_diff):
#                            # Add the rest of VAL lines to buffer with pre-fixe '+'
#                            diff_lines.append('+%s'%val_lines[sw_idx_2+idx].strip('\n'))
#                            self.__debugPrint('+%s'%val_lines[sw_idx_2+idx].strip('\n'))
#                            # Update difference of index
#                            idx_diff += 1
#                        # This is for the SW line that we add in buffer in the beginning
#                        # of the replacement process
#                        idx_diff -=1
#
#                # Add the Beginning Pattern
#                buffer.append(begin_pattern)
#                # Add lines in matched buffer
#                for line in reversed(match_lines):
#                    buffer.append(line)
#                # Add lines in different buffer
#                for line in diff_lines:
#                    buffer.append(line)
#                # Add end pattern
#                buffer.append(end_pattern)
#                self.__debugPrint("--------------------------------------------------------------------------------\n")
#
#        # If there is still difference between sw_len + idx_diff and val_len
#        # we need to add a last difference block 'End of file Pattern'
#        if sw_len + idx_diff < val_len:
#            buffer.append(end_of_file_pattern)
#            for idx in range(sw_len+idx_diff,val_len):
#                l = val_lines[idx].strip('\n')
#                buffer.append(l)
#
#        # Dump file out
#        f = open(out,'w')
#        f.write("######################################################################\n")
#        f.write("### Validation Extensions of %s ###\n" %diff_path)
#        f.write("######################################################################\n")
#        f.write("\n\n")
#        for l in buffer:
#            f.write('%s\n'%l)
#        f.close()


    ''' Function to move files or folder from 'path' to 'ext_p' '''
    def __move_file_or_folder(self,path,root):
        i           = path.rfind('/'+self.type+'/')
        diff_path   = path[i+1:]
        i           = diff_path.rfind('/')
        ext_p       = os.path.join(root,diff_path[:i])
        fname       = diff_path[i:].strip('/')
        self.__createPath(ext_p)
        os.system('cp -Trf "%s" "%s"'%(path,os.path.join(ext_p,fname)))


    def __check_val_extension(self,path):
        for f in self.EXTENSION_FILE:
            if path.find(f) != -1 :
                return True
        return False

    def __compare(self,sw_dir,val_dir,ignore=None):
        print("Processing %s"%(val_dir[val_dir.rfind('/'+self.type+'/')+1:]))
        if ignore == None : ignore = self.VAL_EXTENSION_IGNORE
        compared = dircmp(sw_dir, val_dir,ignore)

        # Only on Validation code source, so it will be added to Extensions
        if compared.right_only:
            for f in compared.right_only:
                path = os.path.join(val_dir,f)
                self.__move_file_or_folder(path,self.ext_root)

        # Differents between SW and VAL
        if compared.diff_files:
            for f in compared.diff_files:
                path = os.path.join(val_dir,f)
                if not self.__check_val_extension(path): continue
                print("Diff found in %s and %s" %(os.path.join(sw_dir,f),os.path.join(val_dir,f)))
                src_path = os.path.join(sw_dir,f)
                dst_path = os.path.join(val_dir,f)
                if f.find('.sdl') == -1:
#                    self.__diff_file(src_path,dst_path)
                    self.__diff_file_2(src_path,dst_path)

                else:
                    self.__diff_sdl_file(src_path,dst_path)

        if compared.funny_files:
            for f in compared.funny_files:
                print ("Cannot compare %s and %s" %(os.path.join(sw_dir,f),os.path.join(val_dir,f)))

        for subdir in compared.common_dirs:
            if self.type == 'aptio':
                if subdir.find('ShellPkg') != -1:
                    path = os.path.join(val_dir,subdir)
                    self.__debugPrint("We don't merge %s, just use the one from VAL source"%path)
                    self.__move_file_or_folder(path,self.ext_root)
                else:
                    self.__compare(os.path.join(sw_dir, subdir), os.path.join(val_dir, subdir))
            else:
                self.__compare(os.path.join(sw_dir, subdir), os.path.join(val_dir, subdir),[])


    def __get_extensions(self,path):
        common_list = []
        add_list    = []
        sub_list    = []
        end         = []
        f = open(path,"r")
        lines = f.readlines()
        f.close()
        for idx in range(len(lines)):
            begin_idx = -1
            end_idx   = -1
            if lines[idx].strip('\n') == begin_pattern or lines[idx] == begin_pattern:
                begin_idx = idx
                for pat_idx in range(idx,len(lines)):
                    if lines[pat_idx] == end_pattern or lines[pat_idx].strip('\n') == end_pattern:
                        end_idx = pat_idx
                        break
                common  = []
                add     = []
                sub     = []
                for cnt_idx in range(idx+1, pat_idx):
                    l = lines[cnt_idx].strip('\n')
                    if l[0] == '=': common.append(l[1:])
                    elif l[0] == '+': add.append(l[1:])
                    elif l[0] == '-': sub.append(l[1:])
                common_list.append(common)
                add_list.append(add)
                sub_list.append(sub)
            elif lines[idx].strip('\n') == end_of_file_pattern:
                add = []
                for idx2 in range(idx+1,len(lines)):
                    l = lines[idx2].strip('\n')
                    end.append(l)

        return (common_list, add_list, sub_list, end)



    def __add_file_or_folder(self,ext_dir,val_dir):
        compared = dircmp(ext_dir, val_dir,self.VAL_EXTENSION_IGNORE)
        if compared.left_only:
            for f in compared.left_only:
                if f in self.VAL_EXTENSION_IGNORE : continue
                path = os.path.join(ext_dir,f)
                print("Only %s found" %path)
                self.__move_file_or_folder(path,self.val_src)

        for subdir in compared.common_dirs:
            if subdir in self.VAL_EXTENSION_IGNORE : continue
            self.__add_file_or_folder(os.path.join(ext_dir, subdir), os.path.join(val_dir, subdir))


    def __read_sdl_file(self,path):
        '''
        Read SW and VAL files, strip down the blanc lines and restore as reference
        '''
        lines   = []
        f       = open(path)
        for line in f:
            #if line.isspace() : continue
            lines.append(line)
        f.close()

        l = len(lines)     # Number of line in file

        token_list  = []
        pcd_list    = []
        ignore_idxs = []
        # Go through all lines in file
        for idx in range(l):
            if idx in ignore_idxs: continue
            token_start = False
            token_end   = False
            token_lines = []

            if lines[idx].strip('\n') == 'TOKEN':
                token_start = True
                for end_idx in range(idx+1,l):
                    if lines[end_idx].strip('\n') == 'End':
                        token_end = True
                        break
                    else:
                        ignore_idxs.append(end_idx)
                        token_lines.append(lines[end_idx])

            if token_start and token_end:
                token = uefi_token()
                token.load_info(token_lines)
                token_list.append(token)
                continue



            pcd_start = False
            pcd_end   = False
            pcd_lines = []

            if lines[idx].strip('\n') == 'PcdMapping':
                pcd_start = True
                for end_idx in range(idx+1,l):
                    if lines[end_idx].strip('\n') == 'End':
                        pcd_end = True
                        break
                    else:
                        ignore_idxs.append(end_idx)
                        pcd_lines.append(lines[end_idx])

            if pcd_start and pcd_end:
                pcd = uefi_pcd()
                pcd.load_info(pcd_lines)
                pcd_list.append(pcd)
                continue


        return (token_list,pcd_list)

    def __diff_sdl_file(self, src_path,dst_path):

        (sw_tokens,sw_pcds) = self.__read_sdl_file(src_path)
        (val_tokens,val_pcds) =self.__read_sdl_file(dst_path)
        i           = dst_path.rfind('/'+self.type+'/')
        diff_path   = dst_path[i+1:]
        i           = diff_path.rfind('/')
        path        = os.path.join(self.ext_root,diff_path[:i])
        fname       = diff_path[i:].strip('/')
        self.__createPath(path)
        out = os.path.join(path,fname)

        '''
        Read SW and VAL files, strip down the blanc lines and restore as reference
        '''
        buffer      = []
        idx_diff = 0
        skips = []
        for sw_idx in range(len(sw_tokens)):
            if sw_idx + idx_diff >= len(val_tokens):break
            s_token = sw_tokens[sw_idx]
            v_token = val_tokens[sw_idx + idx_diff]
            self.__debugPrint( "======================================")
            self.__debugPrint( "TOKEN %d = %s"%(sw_idx,s_token.get_name()))
            self.__debugPrint( "idx_diff = %d"% idx_diff)

            match_lines = []
            diff_lines  = []
            change = False
            if s_token.get_name() == v_token.get_name():
                if not s_token.compare(v_token):
                    change = True
                    if sw_idx != 0:
                        match_lines.append('=TOKEN')
                        for l in sw_tokens[sw_idx-1].dump():
                            match_lines.append(l)
                        match_lines.append('=End')
                    diff_lines.append('-TOKEN')
                    for l in s_token.dump('-'):
                        diff_lines.append(l)
                    diff_lines.append('-End')

                    diff_lines.append('+TOKEN')
                    for l in v_token.dump('+'):
                        diff_lines.append(l)
                    diff_lines.append('+End')

            else:
                match = False
                for sw_idx_2 in range(sw_idx+1,len(sw_tokens)):
                    s_token2 = sw_tokens[sw_idx_2]
                    if s_token2.get_name() == v_token.get_name():
                        match = True
                        break
                if match:
                    idx_diff -= (sw_idx_2 - sw_idx)
                else:
                    end = False
                    for val_idx in range(sw_idx+idx_diff+1,len(val_tokens)):
                        v_token2 = val_tokens[val_idx]
                        if v_token2.get_name() == s_token.get_name():
                            end = True
                            break
                    if end:
                        change = True
                        size = val_idx - sw_idx - idx_diff
                        idx_diff += size
                        self.__debugPrint("End: size =%d"%size)
                        match_lines.append('=TOKEN')
                        for l in sw_tokens[sw_idx-1].dump():
                            match_lines.append(l)
                        match_lines.append('=End')
                        diff_lines.append('+TOKEN')
                        for idx in range(size):
                            for l in val_tokens[sw_idx-1+idx_diff].dump('+'):
                                diff_lines.append(l)
                        diff_lines.append('+End')
                    else:
                        idx_diff += 1

            if change:
                # Add the Beginning Pattern
                buffer.append(begin_pattern)
                # Add lines in matched buffer
                for line in match_lines:
                    self.__debugPrint(line)
                    buffer.append(line)
                # Add lines in different buffer
                for line in diff_lines:
                    self.__debugPrint(line)
                    buffer.append(line)
                # Add end pattern
                buffer.append(end_pattern)
                self.__debugPrint("-------------------------------------------")




        idx_diff = 0
        skips = []
        for sw_idx in range(len(sw_pcds)):
            if sw_idx + idx_diff >= len(val_pcds):break
            self.__debugPrint( "======================================")
            self.__debugPrint( "pcd %d"%sw_idx)
            self.__debugPrint( "idx_diff =%d"% idx_diff)
            s_pcd = sw_pcds[sw_idx]
            v_pcd = val_pcds[sw_idx + idx_diff]
            self.__debugPrint( "SW '%s'"%s_pcd.get_name())
            self.__debugPrint( "VAL'%s'"%v_pcd.get_name())
            match_lines = []
            diff_lines  = []
            change = False
            if s_pcd.get_name() == v_pcd.get_name():
                if not s_pcd.compare(v_pcd):
                    change = True
                    if sw_idx == 0:
                        for l in SDL_PCDS_SECTION_HEADER:
                            match_lines.append('=%s'%l)
                    else:
                        match_lines.append('=PcdMapping')
                        for l in sw_pcds[sw_idx-1].dump():
                            match_lines.append(l)
                        match_lines.append('=End')
                    diff_lines.append('-PcdMapping')
                    for l in s_pcd.dump('-'):
                        diff_lines.append(l)
                    diff_lines.append('-End')
                    diff_lines.append('+PcdMapping')
                    for l in v_pcd.dump('+'):
                        diff_lines.append(l)
                    diff_lines.append('+End')

            else:
                match = False
                for sw_idx_2 in range(sw_idx+1,len(sw_pcds)):
                    s_pcd2 = sw_pcds[sw_idx_2]
                    if s_pcd2.get_name() == v_pcd.get_name():
                        match = True
                        break
                if match:
                    idx_diff -= (sw_idx_2 - sw_idx)
                else:
                    end = False
                    for val_idx in range(sw_idx+idx_diff+1,len(val_pcds)):
                        v_pcd2 = val_pcds[val_idx]
                        self.__debugPrint( v_pcd2.get_name())
                        if v_pcd2.get_name() == s_pcd.get_name():
                            end = True
                            break
                    if end:
                        change = True
                        size = val_idx - sw_idx - idx_diff
                        idx_diff += size
                        self.__debugPrint( "End: size =%d"%size)
                        match_lines.append('=PcdMapping')
                        for l in sw_pcds[sw_idx-1].dump():
                            match_lines.append(l)
                        match_lines.append('=End')
                        match_lines.append('+PcdMapping')
                        for idx in range(size):
                            for l in val_pcds[sw_idx-1+idx_diff].dump('+'):
                                diff_lines.append(l)
                        match_lines.append('+End')

                    else:
                        idx_diff += 1

            if change:
                # Add the Beginning Pattern
                buffer.append(begin_pattern)
                # Add lines in matched buffer
                for line in match_lines:
                    self.__debugPrint( line)
                    buffer.append(line)
                # Add lines in different buffer
                for line in diff_lines:
                    self.__debugPrint( line)
                    buffer.append(line)
                # Add end pattern
                buffer.append(end_pattern)
                self.__debugPrint("-------------------------------------------")



        # Dump file out
        f = open(out,'w')
        f.write("######################################################################\n")
        f.write("### Validation Extensions of %s ###\n" %diff_path)
        f.write("######################################################################\n")
        f.write("\n\n")
        for l in buffer:
            f.write('%s\n'%l)
        f.close()

    def __add_extension_to_sw_file(self,dst_path):
        val_src  = os.path.join(self.val_src,self.type)
        ext_path = dst_path[dst_path.find(self.type)+len(self.type)+1:]
        #print "ext_path",ext_path
        ext_full_path = os.path.join(self.ext_root,self.type,ext_path)
        #print "ext_full_path=", ext_full_path
        val_path = os.path.join(val_src, ext_path)
        #print "val_path=", val_path
        val_dir = val_path[:val_path.rfind('/')]
        #print "val_dir=", val_dir
        fname = val_path[val_path.rfind('/')+1:]
        #print fname

        if not os.path.isfile(ext_full_path):
            self.__debugPrint("%s doesn't have extensions"%dst_path)
            return
        else:
            print ("Adding extension of file ",val_path)
            if not os.path.isdir(val_dir):
                os.makedirs(val_dir)
            sw_f = open(dst_path,"r")
            sw_lines = []
            val_lines= []
            for l in sw_f:
                #if l.isspace(): continue
                sw_lines.append(l)
            sw_f.close()
            (common_list, add_list, sub_list, end) = self.__get_extensions(ext_full_path)

            start_idx = 0
            last_add = 0

            # For each extension, we have 'common', 'add' and 'sub' lines
            for iter in range(len(common_list)):
                self.__debugPrint( "====================================")
                self.__debugPrint( "Extension Block %d"%iter)
                common = common_list[iter]

                add = add_list[iter]
                sub = sub_list[iter]
                size   = len(common)
                #if size == 0: continue

                # Search for 'common' lines
                for idx in range(start_idx, len(sw_lines)):
                    if idx == start_idx :
                        self.__debugPrint( "start_idx = %d"%start_idx)
                        self.__debugPrint( "size      = %d"%size)
                        self.__debugPrint( "len(sub)  = %d"%len(sub))
                    line = sw_lines[idx].strip('\n')
                    match = True
                    for idx2 in range(size):
                        l = sw_lines[idx+ idx2].strip('\n')
                        if l != common[idx2] :
                            match = False
                            break

                    if match == True:
                        self.__debugPrint( "Match found %d"%iter)
                        for ll in common:
                            if last_add != 0 :
                                last_add -= 1
                            else:
                                self.__debugPrint( "= %s"%ll.strip('\n'))
                                val_lines.append(ll.strip('\n'))
                        for ll in add:
                            self.__debugPrint( "+ %s"%ll.strip('\n'))
                            val_lines.append(ll.strip('\n'))

                        if len(sub) > 0:
                            first_sub_line = sub[0]
                            self.__debugPrint(first_sub_line)
                            for i in range(idx+size,len(sw_lines)):
                                if sw_lines[i].strip('\n') == first_sub_line:
                                    break
                        else : i = idx+size
                        start_idx = i + len(sub) - len(add)

                        last_add = len(add)
                        break
                    else:
                        if last_add != 0:
                            last_add -= 1
                        else:
                            self.__debugPrint( "> %s"%line)
                            val_lines.append(line)
                if match == False :
                    self.__debugPrint( "Match not found %d"%iter)

            # Update start_idx taking change from 'add' and 'sub' lines
            start_idx = start_idx + last_add
            self.__debugPrint("start_idx = %d"%start_idx)
            self.__debugPrint("SW len = %d"%len(sw_lines))
            # Copy all the extra lines from SW to VAL
            for idx in range(start_idx,len(sw_lines)):
                line = sw_lines[idx].strip('\n')
                self.__debugPrint( "DEBUG %s"%line)
                val_lines.append(line)

            # Add the End-of-file Extension
            self.__debugPrint( "End of file")
            for ll in end:
                self.__debugPrint( ll.strip('\n'))
                val_lines.append(ll.strip('\n'))

            if not os.path.isdir(val_dir):
                os.makedirs(val_dir)
            val_file = open(val_path,"w")
            for l in val_lines:
                val_file.write('%s\n'%l)
            val_file.close()

    #==============================
    # Public functions
    #==============================

    def build_diff_db(self):
        print( "==============================================================================")
        print( "BUILDING VALIDATION EXTENSION DATABASE for '%s'"%self.type)
        print( "Validation source path %s"%self.val_root)
        print( "SW source path         %s"%self.sw_root)
        print( "==============================================================================")

        self.__compare(self.sw_root, self.val_root)
        ext_path = os.path.join(self.ext_root,self.type)
        print( "==============================================================================")
        print( "EXTENSIONS for '%s' Build DONE"%self.type)
        print ("Extensions built in path '%s'"%ext_path)
        print( "==============================================================================")


    def add_extentions(self):
        print( "==============================================================================")
        print( "BUILDING VALIDATION EXTENDED CODE SOURCE for '%s'"%self.type)
        print( "Validation Extensions path %s"%self.ext_root)
        print( "SW source path             %s"%self.sw_release)
        print( "==============================================================================")

        val_src  = os.path.join(self.val_src,self.type)
        if not os.path.isdir(val_src):
            os.makedirs(val_src)


        # Copy the whole folders of SW to VAL destination path
        print("Copying SW release code from %s to VAL Source %s"%(self.sw_release,val_src))
        cmd = 'cp -Trf %s %s'%(self.sw_release,val_src)
        os.system(cmd)
        self.__debugPrint(cmd)

        print("Adding VAL Extensions to %s"%(val_src))
        sw_paths    = []
        val_folder_paths= []
        for root, dirnames, filenames in os.walk(self.sw_release):
            if self.type == 'aptio':
                for dirname in dirnames:
                    if dirname == 'ShellPkg':
                        val_folder_paths.append(os.path.join(root,dirname))
                for filename in filenames:
                    if root.find('ShellPkg') != - 1:
                        continue
                    sw_paths.append(os.path.join(root, filename))
            else :
                for filename in filenames:
                    sw_paths.append(os.path.join(root, filename))


        for path in val_folder_paths:
            val_path = path[path.find(self.sw_type)+len(self.sw_type)+1:]
            #print "val_path",val_path
            val_full_path = os.path.join(self.val_root,val_path)
            #print "val_full_path=", val_full_path
            val_src_path = os.path.join(val_src, val_path)
            #print "val_src_path=", val_src_path
            val_dir = val_src_path[:val_src_path.rfind('/')]
            #print "val_dir=", val_dir
            if not os.path.isfile(val_full_path):
                #print "Adding folder ",val_path
                if not os.path.isdir(val_dir):
                    os.makedirs(val_dir)
                cmd = 'rm -rf "%s"'%(val_src_path)
                os.system(cmd)
                print(cmd)
                self.__debugPrint(cmd)
                cmd = 'cp -rf "%s" "%s"'%(val_full_path,val_src_path)
                os.system(cmd)
                self.__debugPrint(cmd)
                print(cmd)


        num_of_file = len(sw_paths)
        percent = num_of_file/100.0
        cnt = 0
        for sw_path in sw_paths:
            val_path = sw_path[sw_path.find(self.sw_type)+len(self.sw_type)+1:]
            #print ("val_path",val_path)
            val_src_path = os.path.join(val_src, val_path)
            #print("val_src_path=", val_src_path)
            self.__add_extension_to_sw_file(val_src_path)
            cnt+=1
            if cnt%percent < 1:
                print("EXTENDED SOURCE progress: %.2d percent"%(cnt/percent),end='\r')
                sys.stdout.flush()

        print("")
        print ("EXTRA SOURCE Adding ...")
        print(self.ext_root)
        print(self.val_src)
        print(val_src)
        self.__add_file_or_folder(os.path.join(self.ext_root,self.type),val_src)
        print ("==============================================================================")
        print ("EXTENDED CODE SOURCE for '%s' DONE"%self.type)
        print ("Source built in path '%s'"%val_src)
        print ("==============================================================================")



class uefi_token:
    def __init__(self):
        self.info = {}
        self.lines = None

    def __del__(self):
        del self.info
        del self.lines

    def get_info(self):
        return self.info

    def load_info(self,lines):
        self.lines = lines
        for line in lines:
            line = line.strip('\n') # Strip space
            args = line.split('=')
            i = line.find('=')
            k = line[:i].strip('\t').replace(' ','')
            c = line[i+1:]
            self.info[k] = c

    def get_name(self):
       return self.info['Name']

    def compare(self,tok):
        for k in self.get_info():
            if k not in tok.get_info().keys(): return False
            if self.get_info()[k] != tok.get_info()[k] : return False
        return True
    def dump(self,pre='='):
        buf = []
        for l in self.lines:
            buf.append("%s%s"%(pre,l.strip('\n')))
        return buf

class uefi_pcd:
    def __init__(self):
        self.info = {}
        self.lines = None

    def __del__(self):
        del self.info
        del self.lines

    def get_info(self):
        return self.info

    def load_info(self,lines):
        self.lines = lines
        for line in lines:
            line = line.strip('\n') # Strip space
            args = line.split('=')
            i = line.find('=')
            k = line[:i].strip('\t').replace(' ','')
            c = line[i+1:]
            self.info[k] = c

    def get_name(self):
       return self.info['Name']

    def compare(self,tok):
        for k in self.get_info():
            if k not in tok.get_info().keys(): return False
            if self.get_info()[k] != tok.get_info()[k] : return False
        return True
    def dump(self,pre='='):
        buf = []
        for l in self.lines:
            buf.append("%s%s"%(pre,l.strip('\n')))
        return buf

