#!/usr/bin/env python

################################################################################
# Perform automatic evaluation of a set of student assignments
################################################################################

__author__  = "Anindya Sen (anindya@cse.iitb.ac.in)"
__version__ = "$Revision: 1.0 $"
__date__    = "$Date: 2014/10/09$"
__license__ = "Python"

import sys, shutil
import difflib
import subprocess, os, glob, signal
import math, re
import time, datetime
from optparse import OptionParser
from xml.dom import minidom
from eval_assign import *

def parse_cmd_line() :

    parser = OptionParser()
    parser.add_option("-i", "--inputs", dest="inputs", type="string", 
                      help = "comma-separated list of filenames each containing\
                              a single testcase to be provided to program via stdin")
    
    parser.add_option("-f", "--test_frequency", dest="test_frequency", type="int", default="1",
                      help = "number of times per block a testcase will run (default = 1)")

    parser.add_option("-r", "--reference_src", dest="ref_src", type="string", 
                      help = "file containing correct program")
    
    parser.add_option("-s", "--submissions_dir", dest="sub_dir", type="string", 
                      help = "directory containing programs submitted by students")
    
    parser.add_option("-t", "--timeout", dest="timeout", type="int", default="30",
                      help = "wall-clock time before a program is aborted (default = 30s)")

    parser.add_option("-o", "--csv", dest="csv_file", type="string", default = "",
                      help = "csv file to which the scores are written")
	
    (options, args) = parser.parse_args()
    return options



if __name__ == "__main__":
    
    options = parse_cmd_line()

    # read program files
    try :
        ref_src   = open(options.ref_src,'r').read()

        # compute information for each block (including bonus blocks)
        block_info = scan_blocks(ref_src)
        
        student_dir_list = os.listdir(options.sub_dir)
		
        if not options.csv_file == "" : 
    		# create and open output csv file where the scores will be written
            csv_file = open(options.csv_file, 'w')
            csv_file.write('Date, Roll Number, ')
            
            for key,val in block_info.iteritems() :
                if not key == 1 :
                    csv_file.write('Block %s, ' %key)
            csv_file.write('\n')
		
    except IOError, why :
        print str(why)
        raise


    max_bonus_score = sum([val[1] for key,val in block_info.iteritems()])
    max_score = sum([val[1] for key,val in block_info.iteritems()
                                                     if val[2] == False])

    # generate list of testcases
    testcases = generate_testcases(options.inputs, "", ref_src, "/tmp/cs101_reference")

    for student in student_dir_list : 

        # add to target exe the current time + student id to get unique executable files
        current_time = datetime.datetime.now().strftime('%d%H%M%S')
        target_exe = "/tmp/cs101_" + current_time + "_" + student + ".out"
        
        student_dir = os.path.join(options.sub_dir, student)
        out_file    = open(student_dir + "/result.txt", "w")
        err_file    = open(student_dir + "/err_report.txt", "w")

        # get the latest cpp file uploaded by student
        files = filter(os.path.isfile, glob.glob(student_dir + "/*.cpp"))
        files.sort(key=os.path.getmtime)

        if not files :
            sys.stderr.write("Error : Missing submission by " + student + ".  Skipping evaluation\n")
            continue

        sub_src_file = files[-1]
        sub_src = open(sub_src_file,'r').read()

        # evaluate submitted source
        print "\nEvaluating '" + sub_src_file + "' submitted by " + student + " : "
        block_score_list = eval_student_submission(sub_src, block_info, target_exe,
                                                   testcases, options.timeout, 
                                                   options.test_frequency,
                                                   out_file, err_file)

        # write scores to csv file
        total_score = sum(block_score_list)

        if not options.csv_file == "" : 
            csv_file.write("%s, %-15s, " %(os.path.basename(options.sub_dir), student))
            for score in block_score_list :
                csv_file.write("%.2f, " %score)
            csv_file.write("%.2f\n" %total_score)

        print "\nTotal Score : %.2f" % total_score

        # close files and clean-up
        try :
            out_file.close()
            err_file.close()
            os.remove(target_exe)
        except OSError:
            pass

    if not options.csv_file == "" : 
        csv_file.close()
