#!/usr/bin/env python

import sys, time, os
import os
from optparse import OptionParser

def AddOption( option, help_str, type, default_value, short=""):
    full_option = "--" + option
    if ( type == "string"):
        metavar = default_value
        parser.add_option (short,full_option,help=help_str,default=default_value,type=type,metavar=metavar)
    elif(type == "bool"):
        if ( default_value == True):
            parser.add_option (short,full_option,help=help_str,default=default_value,action="store_false")
        else:
            parser.add_option (short,full_option,help=help_str,default=default_value,action="store_true")
    elif(type == "int"):
            parser.add_option (short,full_option,help=help_str,metavar=default_value,default=default_value,type=type)

def DefaultOptions():
    # This is a pre-built function to add the necessaries options
    # You can use the AddOption methode to add more options to your systems
    AddOption("build_extensions",
              "Differ between VAL reference source and SW reference source to build VAL Extensions",
              "bool",
              False,
              "-e"
              )
    AddOption("build_extended_souce",
              "Use VAL Extensions to build VAL Extended source base on SW build release",
              "bool",
              False,
              "-s"
            )
    AddOption("val_reference_path",
              "Path of Validation reference source",
              "string",
              "/projects/hcm/skylark/users/nhnguyen/frmwrk/GIT/xval_skylark",
              "-v"
              )

    AddOption("destination_path",
              "Path where we want to store VAL Extensions and Extended source",
              "string",
              "VAL_parse",
              "-d"
              )
    AddOption("sw_releases_path",
              "Path contains all SW releases",
              "string",
              "/projects/hcm/skylark/users/nhnguyen/frmwrk/sw_release",
              "-r"
              )

    AddOption("sw_ref_version",
              "SW Version used as reference to create VAL Extensions",
              "string",
              "4.04.25-beta",
              "-o"
              )
    AddOption("sw_build_version",
              "SW Version used to build VAL Extended Source code",
              "string",
              "4.04.27-beta",
              "-n"
              )
    AddOption("ext_files",
              "File contains a list of VAL files which have extensions",
              "string",
              "ext_files",
              "-f"
              )

def DoParse():
    global opt_dict
    global types
    DefaultOptions()
    try:
        (options, args) = parser.parse_args()
        opt_dict = vars(options)
        for arg in args:
            type = arg.lower()
            if type not in ['atf','aptio','linux']:
                raise Exception("'%s' is not supported"%arg)
            types.append(type)
    except Exception as str:
        print str
        parser.print_help()
        sys.exit()

def GetOption(opt):
    global opt_dict
    long_opt = "--" + opt
    if parser.has_option(long_opt):
        return opt_dict[opt]
    else:
        return None


if __name__ == '__main__':
    from extension import *
    types = []
    usage = "usage: %prog [parse options] <ATF|APTIO|LINUX>"
    parser = OptionParser(usage=usage,prog="val_parser")
    opt_dict = []
    DoParse()

    if len(types) == 0:
        parser.print_help()
        sys.exit()

    val_parse = GetOption('destination_path')
    if not os.path.isabs(val_parse):
        path = os.popen('pwd').read().strip('\n')
        val_parse = os.path.join(path,val_parse)

    val_root = GetOption('val_reference_path')
    if not os.path.isabs(val_root):
        path = os.popen('pwd').read().strip('\n')
        val_root = os.path.join(path,val_root)
    if not os.path.isdir(val_root):
        raise Exception("Folder '%s' doesn't exist" %val_root)

    sw_root = GetOption('sw_releases_path')
    if not os.path.isabs(sw_root):
        path = os.popen('pwd').read().strip('\n')
        sw_root = os.path.join(path,sw_root)
    if not os.path.isdir(sw_root):
        raise Exception("Folder '%s' doesn't exist" %sw_root)

    ext_files_path = GetOption('ext_files')
    if not os.path.isabs(ext_files_path):
        path = os.popen('pwd').read().strip('\n')
        ext_files_path = os.path.join(path,ext_files_path)
    if not os.path.isfile(ext_files_path):
        raise Exception("File '%s' doesn't exist" %ext_files_path)


    sw_ref  = GetOption('sw_ref_version')
    sw_build= GetOption('sw_build_version')


    build_ext = GetOption('build_extensions')
    build_src = GetOption('build_extended_souce')

    for type in types:
        ext = extension(val_root=val_root,val_parse=val_parse,sw_root=sw_root,sw_ref=sw_ref,sw_build=sw_build,type=type,ext_files_path=ext_files_path)

        if build_ext:
            ext.build_diff_db()

        if build_src:
            ext.add_extentions()
