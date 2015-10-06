#!/usr/bin/env python

################################################################################
# Perform automatic evaluation of a single student assignment
################################################################################

__author__  = "Anindya Sen (anindya@cse.iitb.ac.in)"
__version__ = "$Revision: 1.0 $"
__date__    = "$Date: 2014/10/09$"
__license__ = "Python"

import sys, shutil
import difflib
import subprocess, os, signal
import math, re, time
from optparse import OptionParser
from xml.dom import minidom

# for implementing process timeout
class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm


def parse_cmd_line() :

    parser = OptionParser()
    parser.add_option("-i", "--inputs", dest="inputs", type="string", 
                      help = "comma-separated list of filenames each containing\
                              a single testcase to be provided to program via stdin")
    
    parser.add_option("-e", "--expected_outputs", dest="expected_outputs", 
                      type="string", default="",
                      help = "comma-separated (optional) list of filenames each\
                              containing the output of the corresponding\
                              testcase provided in inputs")

    parser.add_option("-f", "--test_frequency", dest="test_frequency", type="int", default="1",
                      help = "number of times per block a testcase will run (default = 1)")

    parser.add_option("-k", "--student_key", dest="student_key", type="string", 
                      help = "unique identifier for a student")
    
    parser.add_option("-r", "--reference_src", dest="ref_src", type="string", 
                      help = "file containing correct program")
    
    parser.add_option("-s", "--submitted_src", dest="sub_src", type="string", 
                      help = "file containing program submitted by student")
    
    parser.add_option("-t", "--timeout", dest="timeout", type="int", default="30",
                      help = "wall-clock time before a program is aborted (default = 30s)")

    parser.add_option("-v", "--verbose", dest="verbose", action="store_false",
                      help = "verbose output")
    
    (options, args) = parser.parse_args()
    return options



################################################################################
# Remove all lines which are comments-only 
################################################################################

def strip_comment_only_lines(text) :
    
    comment_only_line_regexp = "//*.*"
    comments_stripped = ""

    for line in [s.lstrip() for s in text.splitlines()] :
        if not re.match(comment_only_line_regexp, line) : 
            comments_stripped += line + '\n'

    return comments_stripped



################################################################################
# If the marks for a particular block is missing, the autograder assigns to it 
# a default value of 1.
################################################################################

def scan_blocks(ref_src) :

    block_delimiter = "\n *////[^\n]*(BEGIN|END)([^\n]*)DONT_ERASE_([^\n]*)\n"
    block_matches   = re.findall(block_delimiter, ref_src)

    block_info = []
    block_ids_seen = []

    for block in block_matches :
        
        # check if this is a bonus question
        if block[1].find('BONUS') == -1 :
            bonus_block = False
        else :
            bonus_block = True


        if block[0] == 'BEGIN' :
            # get block_id and marks (default = 1)
            block_id_str, marks_str = block[2].split('_') if \
                                           '_' in block[2]  else (block[2], '1')
            block_id = int(block_id_str)
            marks    = int(marks_str)

            previous_block_id = block_id
            begin_block = " *////[^\n]*" + block[0] + block[1] + "DONT_ERASE_" + block[2] + "\n"

        elif block[0] == 'END' :
            # make sure that all begin/end occur in pairs
            if not block_id == previous_block_id :
                raise SyntaxError("Unmatched BEGIN/END comments in " +
                                  "reference file (Block ID : " + 
                                  str(previous_block_id) + ")")

            end_block = " *////[^\n]*" + block[0] + block[1] + "DONT_ERASE_" + block[2] + "\n"

            # capture block text
            block_text_regexp = begin_block + "(.*)" + end_block
            block_text = re.search(block_text_regexp, ref_src, re.DOTALL).group(1)

            # check if 'block_id' has been used earlier
            if block_id in block_ids_seen :
                raise SyntaxError("Multiple blocks with identical ID = " + str(block_id))

            block_info.append((block_id, (block_text, marks, bonus_block)))
            block_ids_seen.append(block_id)
    
    # final block should be an 'END' block
    if block_matches[-1][0] == 'BEGIN' :
        raise SyntaxError("Unmatched BEGIN/END comments in " +
                          "reference file (Block ID : "      + 
                          str(block_id) + ")")

    return dict(block_info)



################################################################################
# Given a list of comma-separated input filenames and another (possibly empty)
# list of comma-separated output filenames, generate a list of testcases.
################################################################################

def generate_testcases(inputs, outputs, ref_src, target_exe) :

    input_file_list = inputs.split(',')
    num_testcases   = len(input_file_list)

    # create a list of (file, i/p, o/p), one for each testcase
    try :
        testcases = []
        for f in input_file_list :
            stdin = open(f,'r').read()
            testcases.append([f, stdin])
    except IOError, why :
        sys.stderr.write(str(why))
        raise

    # expected output files already specified, no need to regenerate
    if not outputs == "" :

        # number of input and output files must be equal!
        output_file_list = outputs.split(',')
        if not len(output_file_list) == num_testcases :
            sys.stderr.write("Error : The number of input and output files do not match\n")
            raise Exception

        # read, in order, each expected output file
        try :
            i = 0
            for f in output_file_list :
                testcases[i].append(open(f,'r').read())
                i += 1

        except IOError, why :
            sys.stderr.write(str(why))
            raise Exception
    
    # expected outputs not provided by user,
    # generate it by compiling and running ref_src
    else : 
        (stdout, stderr, comp_status) = compile_code(ref_src, target_exe)
        
        if not comp_status == 0:
            sys.stderr.write("Error : Failed to compile reference file\n")
            raise Exception
        
        for testcase in testcases :
            (stdout, stderr, rcode) = run_code(target_exe, testcase[1], "", 100)
            testcase.append(stdout)

    return testcases



################################################################################
# Divide student submission into three parts :
#   (a) All text before (and including) the begin of block with id = block_id   
#   (b) All text between the begin and end of block with id = block_id   
#   (c) All text after (and including) the end of block with id = block_id   
# and return each part as a separate string
################################################################################

def trisect_src(src, block_id) :

    block_str_id = str(block_id)
    if block_id < 10 :
        block_str_id = "0" + block_str_id
    
    end_intro_str   = " *////[^\n]*BEGIN[^\n]*DONT_ERASE_" + block_str_id + "[^\n]*\n"
    begin_concl_str =   " *////[^\n]*END[^\n]*DONT_ERASE_" + block_str_id + "[^\n]*\n"

    intro_match = re.search(".*" + end_intro_str, src, re.DOTALL)
    concl_match = re.search(begin_concl_str + ".*", src, re.DOTALL)

    # check for beginning of block in student implementation
    if intro_match :
        intro = intro_match.group(0)
    else :
        raise SyntaxError("  Error : Unable to find start of block " \
                          + str(block_id) + " in student implementation\n")

    # check for end of block in student implementation
    if concl_match :
        concl = concl_match.group(0)
    else :
        raise SyntaxError("  Error : Unable to find end of block " \
                          + str(block_id) + " in student implementation\n")

    # capture block text
    body_regexp = end_intro_str + "(.*)" + begin_concl_str
    body = re.search(body_regexp, src, re.DOTALL).group(1)

    return intro, body, concl
    


################################################################################
# Function to replace all but one block (specified by block_id) in destination
# with a matching correct block (minus the block delimiters) from the reference
# implementation.
# 
# block_info contains the blocks from reference implementation.
#
# If a block in destination does NOT appear in the prespecified format, that block
# is ignored i.e. no replacement is performed, and an error message is sent to
# stderr.
################################################################################

def swap_all_but_one_blocks(destination, block_info, block_id, err_file) :

    swapped = destination

    for i in range(1,len(block_info) + 1) :
        if i == block_id : continue
        
        try :
            (intro, body, concl) = trisect_src(swapped, i)
            if i == 1 :
                # don't remove contents of block 1 in student code
                swapped = intro + body + block_info[i][0] + concl
            else :
                swapped = intro + block_info[i][0] + concl

        except SyntaxError, why :
            err_file.write(str(why))
            sys.stderr.write(str(why))

    return swapped



################################################################################
# Compile src written in c++ using the g++ compiler.  Instead of writing src to
# a file and passing the filename to g++, src is directly sent to compile
# command via stdin.  Function returns the return code of the compile command
# along with its stdout and stderr output.
################################################################################

def compile_code(src, target_exe) :

    cmd = "g++ -Wall -o " + target_exe + " -x c++ -"
    process = subprocess.Popen(cmd, bufsize=-1,
                               shell=True, close_fds=True,
                               preexec_fn=os.setsid,
                               stdin  = subprocess.PIPE,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE)

    (c_stdout, c_stderr) = process.communicate(input=src)

    # compilation status
    c_status =  process.returncode
    return (c_stdout, c_stderr, c_status)



################################################################################
# Program executes target_exe with input provided by std_in and returns stdout,
# stderr as strings along with the return code.
#
# target_exe is run with std_input feeding data to its stdin.
#
# The final output is compared with expected_output and output is considered
# correct if it matches expected_output EXACTLY.
#
# Function returns :
# out : output produced by running program
# err : error message generated by running program
# return code :
#    1 : output is correct
#    0 : output is incorrect
################################################################################

def run_code(target_exe, std_input, expected_output, timeout) :

    process = subprocess.Popen(target_exe, bufsize=-1,
                               shell=True, close_fds=True,
                               preexec_fn=os.setsid,
                               stdin  = subprocess.PIPE,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE)
    
    # monitor execution time 
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)

    # http://stackoverflow.com/questions/1191374/subprocess-with-timeout
    try :
        (out, err) = process.communicate(std_input)
        rcode      = process.returncode
        signal.alarm(0)  # reset alarm
    except Alarm :
        (out, err) = ("", "Process Timeout\n")
        rcode      = process.returncode
        os.killpg(process.pid, signal.SIGKILL) 
   
    #print "Output : ", out 
    #print "Expected Output : ", expected_output 

    #check if output matches expected output
    if out == expected_output :
        # program compiled successfully and output is correct
        return (out, err, 1)
    else :
        # program compiled successfully but output is incorrect
        return (out, err, 0)



################################################################################
# evaluate student submission one block at a time
################################################################################

def eval_student_submission(sub_src, block_info, target_exe, testcases, timeout, test_freq, out_file, err_file) :

    block_score_list = []

    for block_id in range(2, len(block_info) + 1) :

        block_score = 0

        test_block_str = "\nTesting Block " + str(block_id) + " :"

        print test_block_str
        out_file.write(test_block_str + "\n")
        block_error = False

        try :
            (intro, body, concl) = trisect_src(sub_src, block_id)
        except SyntaxError, why :
            err_file.write(str(why))
            sys.stderr.write(str(why))
            block_score_str = "  Block %s Score = %.2f" %(block_id, block_score)
            print block_score_str
            out_file.write(block_score_str + "\n" )
            block_score_list.append(block_score)
            continue

        body = strip_comment_only_lines(body)

        # no need to evaluate block if it is empty
        if ''.join(body.split()) == '' : 
            msg = "  Empty block " + str(block_id) + ".  Skipping evaluation."
            out_file.write(msg + '\n')
            print msg
            block_score_str = "  Block %s Score = %.2f" %(block_id, block_score)
            print block_score_str
            out_file.write(block_score_str + "\n" )
            block_score_list.append(block_score)
            continue

        exec_code = swap_all_but_one_blocks(sub_src, block_info, block_id, err_file)
        #print "Testing block :" + str(block_id) + ".  Begin executable."
        #print exec_code
        #print "End executable"
        
        (out, err, comp_status) = compile_code(exec_code, target_exe)
        
        # program failed to compile
        if not comp_status == 0:
            err_file.write(test_block_str + "\n")
            err_file.write("  Error : Failed to compile student submission :\n")
            for line in err.splitlines() :
                err_file.write(10 * ' ' + line + '\n')

            sys.stderr.write(test_block_str + "\n")
            sys.stderr.write("  Error : Failed to compile student submission :\n")
            for line in err.splitlines() :
                sys.stderr.write(10 * ' ' + line + '\n')

            block_score_str = "  Block %s Score = %.2f" %(block_id, block_score)
            print block_score_str
            out_file.write(block_score_str + "\n" )
            block_score_list.append(block_score)
            continue

        # run generated target_exe on each testcase
        for testcase in testcases :

            # run executable with testcase as many times until
            # (a) received status = 0 (output is incorrect) OR
            # (b) test_freq number of runs have been made
            for run in range(test_freq) :
                (out, err, status) = run_code(target_exe, testcase[1], testcase[2], timeout)
                if status == 0 : break

            # output matches expected_output.  add score
            if status == 1 :
                part_score = block_info[block_id][1]/(1.0 * len(testcases))
                block_score += part_score
                testcase_score_str = "  Testcase = '" + testcase[0] + "', Score = %.2f" %part_score
                print testcase_score_str
                out_file.write(testcase_score_str + "\n" )

            # output does NOT match expected_output.
            elif status == 0 :
                if not block_error :
                    err_file.write(test_block_str + "\n")
                    block_error = True

                testcase_score_str = "  Testcase = '" + testcase[0] + "', Score = 0.00"
                print testcase_score_str
                out_file.write(testcase_score_str + "\n")
                err_file.write(testcase_score_str + "\n")

                output_mismatch_str = "    Error : Output does not match expected output"
                err_file.write(output_mismatch_str + "\n")
                sys.stderr.write(output_mismatch_str + "\n")
                for line in err.splitlines() :
                    err_file.write(12 * ' ' + line + '\n')
                    sys.stderr.write(12 * ' ' + line + '\n')

        block_score_str = "  Block %s Score = %.2f" %(block_id, block_score)
        print block_score_str
        out_file.write(block_score_str + "\n" )
        block_score_list.append(block_score)

    return block_score_list



if __name__ == "__main__":
    
    options = parse_cmd_line()

    # assign a unique executable filename
    if not options.student_key :
        sys.stderr.write("Error: Missing student key\n")
        raise Exception
    target_exe = "/tmp/cs101_" + options.student_key + ".out"

    # read program files
    try :
        ref_src   = open(options.ref_src,'r').read()
        sub_src   = open(options.sub_src,'r').read()
    except IOError, why :
        sys.stderr.write(why)
        raise IOError

    # compute information for each block (including bonus blocks)
    try :
        block_info = scan_blocks(ref_src)
    except SyntaxError, why :
        sys.stderr.write(why)

    max_bonus_score = sum([val[1] for key,val in block_info.iteritems()]) 
    max_score = sum([val[1] for key,val in block_info.iteritems() 
                                                     if val[2] == False]) 

    # generate list of testcases
    if not options.inputs:
        sys.stderr.write("IOError: Missing testcases\n")
        raise IOError
    testcases = generate_testcases(options.inputs, options.expected_outputs,
                                                        ref_src, target_exe)

    # evaluate submitted source
    block_score_list = eval_student_submission(sub_src, block_info, target_exe, testcases,
                                               options.timeout, options.test_frequency,
                                               sys.stdout, sys.stderr)

    score = sum(block_score_list)
    print "\nTotal Score : %.2f\n" % score
