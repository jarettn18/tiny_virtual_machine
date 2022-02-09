.class Cat:Obj

.method $constructor
.local i
.local j

const "Hello "
store i

const "World"
load i
call String:plus
store j

load j
call String:print

return 0

