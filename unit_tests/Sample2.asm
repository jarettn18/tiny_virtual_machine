.class Sample:Obj

.method $constructor
.local i
.local j
.local cat
const 13
const 42
Call Int:plus
store i
const 32
load i
Call Int:sub
store j
load j
Call Int:print
const "Nora"
store cat
load cat
Call String:print
return 0