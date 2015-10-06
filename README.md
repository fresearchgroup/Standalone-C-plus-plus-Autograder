# Standalone-C-Autograder
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
<li>submssions Folder: Containing the following
<li>Date Folder: Containing the following
<ol>
<li>Roll Number Folder 1 ... n, each containing a program
</ol>
</ol>
</ol>
</ol>

<pre>
<b><sub>
                                 cs101-standalone-autograder-2015-05-28
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

</sub></b>

</pre>

