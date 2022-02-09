.class Assign:Obj

.method $constructor
.local i, j
    const 13
    const 42
    call Int:plus
    store i

    const 32
    load i
    call Int:sub

    store j
    load j
    call Int:print

    return 0
