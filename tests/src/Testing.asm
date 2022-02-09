.class Testing:Obj

.method $constructor
.local x
.local j
const 12
store x
const 42
load x
call Int:plus
store j
load x
call Added:print
return 0