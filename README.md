# tiny_vm
A tiny virtual machine interpreter for Quack programs

## Work in progress

This is intended to become the core of an interpreter for the Winter 2022
offering of CIS 461/561 compiler construction course at University of Oregon, 
if I can ready it in time. 

#Submission By Jarett Nishijo
#What works:  
-Arithmetic/Variable Assignments (Tiny Calculator)  
-Type Declarations (Nano-Quack)  
-Control Flow (Mini-Quack)  
-Conditional Statements (Mini-Quack)  
-Jumps (Mini-Quack)  
-Field Access (Full Quack)  

#What Doesn't Work:  
-User-Defined Methods and Classes (Full Quack)  
I was unable to get User-Defined Methods and classes up and running. However, I've hand written user-defined classes
and can verify that field access works.
I was having implementation issues when it came to scaling. The ASTBuilder classes
you gave us were more intuitive than my initial implementation so I spent a lot of time
rebuilding the ASTs using your library.

#Test Cases:
All test cases that were written by me are in tests/qktests. Expected
output was not provided. Feed a quack file into the shell script to produce ASM output.
#How to Run:  

Run quack.sh with an input test.qk file.  
Run quackc.sh to only generate object code without running VM. Object code
can be found in ./tests/OBJ/Main.json

Usage: ./quack.sh [file].qk  

