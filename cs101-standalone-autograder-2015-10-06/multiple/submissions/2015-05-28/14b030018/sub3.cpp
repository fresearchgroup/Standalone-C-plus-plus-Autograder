#include <iostream>
using namespace std;

// Please write your code, within the "BEGIN-END" blocks given below.
// A "BEGIN-END" block is identified as follows :
//
// "//// BEGIN: Some string DONT_ERASE_xx_yy"
// 
//
// "//// END: Some other string DONT_ERASE_xx_yy"
//
// where "xx" is the block number and "yy" is the
// marks allocated for the block
//
// The FIRST block (BLOCK 1 i.e. DONT_ERASE_01_0) carries 0 marks and 
// is a placeholder for your personal information, to be written as a comment.
//
// WARNING :
// (1) Do NOT write any cout or cin statements
// (2) Do NOT delete or modify the existing code i.e. main function, comments, blocks, etc.
// (3) Write your code in between BEGIN and END of the respective blocks only
// (4) Do NOT rename the .cpp file

////---------------------------------------------------------
//// BEGIN: Fill your details as comments below DONT_ERASE_01_0
//// Name: Firuza Aibara
////
//// END: Fill your details as comments above DONT_ERASE_01_0
////---------------------------------------------------------

int main()
{
    //Arithmetic Operation
    int num1, num2, arithmeticResult;
    char option;
    cout<<"Enter two numbers (Range: 1 to 100)" << endl;
    cin>>num1>>num2;
    cout<< "Enter Character input (A or a or S or s)" << endl;
    cin>>option;

////--------------------------------------------------------
//// BEGIN: Write code to perform arithmetic operation DONT_ERASE_02_01
//// Store the result in variable 'arithmeticResult'

    if(option=='A' || option=='a')  {
        cout << "Addition of " << num1 + num2;  
    }
    else if(option=='S' || option=='s')  {
        arithmeticResult = num1 - num2;  
    }
    else {
        arithmeticResult=-999;
    }

//// END: End of Code to perform arithmetic operation DONT_ERASE_02_01
////--------------------------------------------------------

    cout<<"Aritmetic result = " << arithmeticResult << endl;

    return 0;
}
