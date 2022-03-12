
/**
 * GENERATED CODE, DO NOT EDIT
 * Generated 2022-02-19 16:11:59.775473 by build_bytecode_table.py
 * 
 * Integer encoding of VM operations ---
 * Map those integer encodings to function pointers (for executing)
 * and to strings (for debugging and assembling).
 */
 
#include "vm_code_table.h"
op_tbl_entry vm_op_bytecodes[] = {

	 { "halt", vm_op_halt, 0 }, //0  Stops the processor.
	 { "const", vm_op_const, 1 }, //1  Push constant; constant value follows
	 { "call", vm_op_methodcall, 1 }, //2  Call an interpreted method
	 { "call_native", vm_op_call_native, 1 }, //3  Trampoline to native method
	 { "enter", vm_op_enter, 0 }, //4  Prologue of called method
	 { "return", vm_op_return, 1 }, //5  Return from method, reclaiming locals
	 { "new", vm_op_new, 1 }, //6  Allocate a new object instance
	 { "pop", vm_op_pop, 0 }, //7  Discard top of stack
	 { "alloc", vm_op_alloc, 1 }, //8  Allocate stack space for locals
	 { "load", vm_op_load, 1 }, //9  Load (push) a local variable onto stack
	 { "store", vm_op_store, 1 }, //10  Store (pop) top of stack to local variable
	 { "load_field", vm_op_load_field, 1 }, //11  Load from object field
	 { "store_field", vm_op_store_field, 1 }, //12  Store to object field
	 { "roll", vm_op_roll, 1 }, //13  [obj arg1 ... argn] -> [arg1 ... argn obj]
	 { "jump", vm_op_jump, 1 }, //14  Unconditional relative jump
	 { "jump_if", vm_op_jump_if, 1 }, //15  Conditional relative jump, if true
	 { "jump_ifnot", vm_op_jump_ifnot, 1 }, //16  Conditional relative jump, if false
	 { "is_instance", vm_op_is_instance, 1 }, //17  Test membership in class (for typecase)

    { 0, 0, 0}  // SENTRY
};

