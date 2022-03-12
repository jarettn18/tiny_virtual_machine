
.class Main:Obj
.method $constructor
.locals idx, x, y
const 10
store idx

            const 5
load idx
call Int:less
jump_if then_1
jump or_4
or_4:
const 5
load idx
call Int:equals
jump_if then_1
jump else_2
then_1:
const "If Hello"
store x
load x
call String:print

            jump endif_3

            else_2:
const 5
const 3
call Int:plus
store y
load y
call Int:print

            endif_3:
        
const nothing
return 0


