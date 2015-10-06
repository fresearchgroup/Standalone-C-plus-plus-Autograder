# Standalone C++ Autograder
Autograder to grade single and multiple C++ Program Submissions
##Autograder and Related Files
The autograder (python programs) and Sample Programs (Soltuion, Test cases, and sample program submitted by students) are available for download. Please note that the .tar.gz file is the updated version dated, <font color="red">06 October 2015, 1230hrs</font>. Incase, you have an earlier version, it is advisable to download the latest one.


## Structure
The structure/hierarchy of the .tar.gz is given below

<ol>
<li> <b>autograder-program</b> Folder: Containing 2 python files 
<ol>
<li> batch_eval_assign.py: Used for grading multiple submissions
<li> eval_assign.py: Used for grading single program file
<li> script_to_grade_single_program.sh: Contains the autograder script to grade single submissions. (It is also mentioned below)
<li> script_to_grade_multiple_programs.sh: Contains the autograder script to grade multiple submissions. (It is also mentioned below)
</ol>
<li> <b>single</b> Folder: Containing the following files. This structure should be used only to grade single programming files
<ol>
<li>input1, input2, input3: Test Cases
<li>reference.cpp: Solution Program
<li>sample-submissions-by-students: Contains multiple .cpp files
</ol>
<li> <b>multiple</b> Folder: Containing the following files. This structure should be used only to grade multiple programming files at once
<ol>
<li>solutions Folder: Containing the following
<ol>
<li>Date Folder: Containing the following
<ol>
<li>reference.cpp - Solution program
<li>testcases folder: Containing input test cases
</ol>
</ol>
<li>submissions Folder: Containing the following
<ol>
<li>Date Folder: Containing the following
<ol>
<li>Roll Number Folder 1 ... n, each containing a program
</ol>
</ol>
</ol>
</ol>
</ol>

<pre>
<b>
                                 cs101-standalone-autograder-2015-10-06
               ___________________________________________________|___________________________________
              |                    |                                                                  | 
    autograder-program          single                                                           multiple 
                          <font color="red">(To grade single programs)                          (To grade multiple programs - batch) </font>                 
         |                        |                                                _______________|___________                                 
         |                        |                                               |                           |
  batch_eval_assign.py      input1                                            solutions                  submissions      
  eval_assign.py            input2                                                |                           |
                            input3                                           2015-05-28                 2015-05-28
                            reference.cpp                          _______________|                 __________|____________
                            sample-submissions-by-students        |               |                |          |            |
                                              |                   |               |                |          |            |
                                              |                   |               |                |          |            |
                                              |             reference.cpp      testcases         RollNo1    RollNo2  ...  RollNo_n  
                                              |                                   |                |           |            |
                                              |                                   |                |           |            |
                                         sub1.cpp                                 |                |           |            |
                                         sub2.cpp                                 |                |           |            |
                                         sub3.cpp                                 |            sub1.cpp    sub2.cpp   ...  sub_n.cpp
                                         sub4.cpp                                 |   
                                         sub5.cpp                              input1
                                                                               input2
                                                                               input3

</b>

</pre>


##To Grade Single File
###Grade Program: sub4.cpp
Assuming that you are in 'autograder-program' directory, run the following command to grade a submission (sub4.cpp) present in 'single' folder
<pre><b>  ./eval_assign.py -r ../single/reference.cpp 
 -s ../single/sample-submissions-by-students/sub4.cpp 
 -i ../single/input1,../single/input2,../single/input3 
 -k 123
</b></pre>
Since the program written in sub4.cpp does not fulfill the requirements of what the program should perform, the following output will be generated by the autograder on the terminal
<pre><b> Testing Block 2 :
 Testing Block 2 :
   Testcase = '../single/input1', Score = 0.33
   Testcase = '../single/input1', Score = 0.33
 Testing Block 2 :
   Testcase = '../single/input2', Score = 0.00
   Testcase = '../single/input2', Score = 0.00
   Testcase = '../single/input2', Score = 0.00
     Error : Output does not match expected output
     Error : Output does not match expected output
   Testcase = '../single/input3', Score = 0.00
   Testcase = '../single/input3', Score = 0.00
   Testcase = '../single/input3', Score = 0.00
     Error : Output does not match expected output
     Error : Output does not match expected output
   Block 2 Score = 0.33
   Block 2 Score = 0.33
 Total Score : 0.33
</b></pre>

###Grade Program: sub5.cpp
Assuming that you are in 'autograder-program' directory, run the following command to grade a submission (sub5.cpp) present in 'single' folder
<pre><b>  ./eval_assign.py -r ../single/reference.cpp 
 -s ../single/sample-submissions-by-students/sub5.cpp 
 -i ../single/input1,../single/input2,../single/input3 
 -k 123
</b></pre>
Since there is no error in the code given in sub5.cpp, the following output will be generated by the autograder on the terminal 

<pre><b> Testing Block 2 :
 Testing Block 2 :
   Testcase = '../single/input1', Score = 0.33
   Testcase = '../single/input1', Score = 0.33
   Testcase = '../single/input2', Score = 0.33
   Testcase = '../single/input2', Score = 0.33
   Testcase = '../single/input3', Score = 0.33
   Testcase = '../single/input3', Score = 0.33
   Block 2 Score = 1.00
   Block 2 Score = 1.00
 Total Score : 1.00
</b></pre>

##To Grade Multiple Files
Assuming that you are in 'autograder-program' directory, run the following command to grade many submissions present in 'multiple' folder
<pre><b> ./batch_eval_assign.py -r ../multiple/solutions/2015-05-28/reference.cpp
 -s ../multiple/submissions/2015-05-28
 -i ../multiple/solutions/2015-05-28/testcases/input1,../multiple/solutions/2015-05-28/testcases/input2,../multiple/solutions/2015-05-28/testcases/input3
 -f 5 -t 10 -o ../multiple/scores.csv > ../multiple/log.log
</b></pre>
Since this command is also given in <b>autograder-program/script_to_grade_multiple_programs.sh</b>, you can also run the following command to grade multiple submissions present in the 'multiple' folder
<pre><b> ./script_to_grade_multiple_programs.sh
</b></pre>
The autograder will grade all the submissions present in multiple/submissions/ directory. 

<b>View Scores:</b> The list of marks obtained all students will be in <b>multiple/scores.csv</b> file. 

<b>Log Report:</b> A detailed report of each student (i.e. which test cases passed, etc.) can be viewed in <b>multiple/log.log</b> file.

Apart from this, the error report and the score obtained is also individually stored in the respective directories, e.g. <b>multiple/submissions/2015-05-28/14b030016/err_report.txt'''

##Help for Autograder
Assuming that you are in the 'autograder-program' directory
<pre><b>   ./batch_eval_assign.py -help
   ./eval_assign.py -help
</b></pre>
