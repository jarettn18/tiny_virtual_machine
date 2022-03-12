"""
Lark Parser Generator
================

REPL calculator shows how to write a basic calculator with variables.
"""
from lark import Lark, Transformer, v_args, visitors
import argparse
import sys
import json
from typing import List, Callable
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def cli():
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("source", type=argparse.FileType("r"),
                            nargs="?", default=sys.stdin)
    args = cli_parser.parse_args()
    return args

JUMP_COUNT = 0
type_table = {}

def new_label(prefix: str) -> str:
    global JUMP_COUNT
    JUMP_COUNT += 1
    return f"{prefix}_{JUMP_COUNT}"

def ignore(node: "ASTNode", visit_state):
    log.debug(f"No visitor action at {node.__class__.__name__} node")
    return

def flatten(m: list):
    """Flatten nested lists into a single level of list"""
    flat = []
    for item in m:
        if isinstance(item, list):
            flat += flatten(item)
        else:
            flat.append(item)
    return flat

class ASTNode:
    """Abstract base class"""
    def __init__(self):
        self.children = []    # Internal nodes should set this to list of child nodes

    def walk(self, visit_state, pre_visit: Callable =ignore, post_visit: Callable=ignore):
        pre_visit(self, visit_state)
        for child in flatten(self.children):
            log.debug(f"Visiting ASTNode of class {child.__class__.__name__}")
            child.walk(visit_state, pre_visit, post_visit)
        post_visit(self, visit_state)

    def initialization(self, visit_state: dict):
        ignore(self, visit_state)

    def type_check(self, visit_state: dict):
        ignore(self, visit_state)

    def r_eval(self) -> List[str]:
        """Evaluate for value"""
        raise NotImplementedError(f"r_eval not implemented for node type {self.__class__.__name__}")

    def c_eval(self, true_branch: str, false_branch: str) -> List[str]:
        raise NotImplementedError(f"c_eval not implemented for node type {self.__class__.__name__}")

class ProgramNode(ASTNode):
    '''program : [(classes)* (statement)*]'''
    def __init__(self, classes: List[ASTNode] = [], methods: List[ASTNode] = [], stmt_block: List[ASTNode] = []):
        self.classes = classes
        main_class = ClassNode("Main", [], "Obj", methods, stmt_block)
        self.classes.append(main_class)
        self.children = self.classes

    def __str__(self) -> str:
        return "\n".join([str(c) for c in self.classes])


class ClassNode(ASTNode):
    '''classes : class_sig class_body'''
    def __init__(self, name: str, formals: List[ASTNode],
                 super_class: str,
                 methods: List[ASTNode],
                 block: List[ASTNode]):
        self.name = name
        self.formals = formals
        self.super_class = super_class
        self.methods = methods
        self.constructor = MethodNode("$constructor", formals, name, block)
        self.children = methods + [self.constructor]

    def __str__(self):
        ret = f"\n.class {self.name}:{self.super_class}\n"
        formals_str = ", ".join([str(fm) for fm in self.formals])
        if formals_str:
            ret += f".field {formals_str}\n"
        methods_str = "\n".join([f"{method}\n" for method in self.methods])
        ret += f"{self.constructor}\n{methods_str}\n"
        return ret

    def initialization(self, visit_state: dict):
        """Create class entry in symbol table (as a preorder visit)"""
        if self.name in visit_state:
            raise Exception(f"Shadowing class {self.name} is not permitted")
        visit_state["current_class"] = self.name
        visit_state[self.name] = {
            "super": self.super_class,
            "fields": [str(fm.var_type) for fm in self.formals],
            "methods": {}
        }

class MethodNode(ASTNode):
    def __init__(self, name: str, formals: List[ASTNode],
                 returns: str, body: List[ASTNode]):
        self.name = name
        self.formals = formals
        self.variables = {}
        self.returns = returns
        self.body = body
        self.children = [formals, body]

    def __str__(self):
        ret = f".method {self.name}\n"
        if self.formals:
            formals_str = ", ".join([str(fm) for fm in self.formals])
            ret += f".args {formals_str}\n"
        if len(type_table.keys()) > 0:
            locals_str = ", ".join([str(fm) for fm in type_table.keys()])
            ret += f".locals {locals_str}\n"
        ret += f"{self.body}"
        f_size = len(self.formals)
        if f_size:
            ret += f"\nreturn {f_size}\n"
        else:
            ret += f"\nconst nothing\nreturn {len(self.formals)}"
        return ret

    # Add this method to the symbol table
    def initialization(self, visit_state: dict):
        visit_state["current_method"] = self.name
        clazz = visit_state["current_class"]
        if self.name in visit_state[clazz]["methods"]:
            raise Exception(f"Redeclaration of method {self.name} not permitted")
        params = [formal.var_type for formal in self.formals]
        visit_state[clazz]["methods"][self.name] = { "params": params, "ret": self.returns }


class FormalNode(ASTNode):
    def __init__(self, var_name: ASTNode, var_type: ASTNode):
        self.var_name = var_name
        self.var_type = var_type
        self.children = [var_name, var_type]

    def __str__(self):
        print("formal here")
        ret = f"{self.var_name}"
        return ret


class ReturnNode(ASTNode):
    """return : "return" [r_exp]"""
    def __init__(self, ret: List[ASTNode]):
        self.ret = ret
        self.children = ret

    def __str__(self):
        ret = "\n".join([str(r) for r in self.ret])
        return ret

class BlockNode(ASTNode):
    def __init__(self, stmts: List[ASTNode]):
        self.stmts = stmts
        self.children = stmts

    def __str__(self):
        return "\n".join([str(stmt) for stmt in self.stmts])


class AssNode(ASTNode):
    """assignment : l_exp [":" ident] "=" r_exp"""
    def __init__(self, left: ASTNode, ident: ASTNode, right: ASTNode):
        self.left = left
        self.ident = ident
        self.right = right
        self.children = [right, left]
        self.add_to_type_table()
        #print(self.left.c_eval(), "is", self.right.c_eval())

    def __str__(self):
        ret = "\n".join([str(re) for re in self.children])
        return ret

    def add_to_type_table(self):
        if type(OpNode("test", self.left, self.right)) == type(self.right):
            type_table[self.left.c_eval()] = self.right.type
        else:
            if self.left.c_eval() in type_table.keys():
                var = self.left.c_eval()
                val = self.right.c_eval()
                a_type = "idk"
                if (len(val) > 1):
                    #could be a string
                    if val[0] == '"' and val[len(val) - 1] == '"':
                        a_type = "String"
                    elif val == "True" or val == "False" or val == "None":
                        a_type = "Bool"
                    elif (val.isdigit()):
                        a_type = "Int"
                    else:
                        type_table[var] = "Obj"
                    if a_type != type_table[var]:
                        type_table[var] = "Obj"
            else:
                var = self.left.c_eval()
                val = self.right.c_eval()
                if (len(val) > 1):
                    #could be a string
                    if val[0] == '"' and val[len(val) - 1] == '"':
                        type_table[var] = "String"
                    elif val == "True" or val == "False" or val == "None":
                        type_table[var] = "Bool"
                    elif (val.isdigit()):
                        type_table[var] = "Int"
                    else:
                        type_table[var] = "Obj"
                else:
                    if val.isdigit():
                        type_table[var] = "Int"


class IfNode(ASTNode):
    """if condition stmt_block [otherwise*]"""
    def __init__(self,
                 cond: ASTNode,
                 thenpart: ASTNode,
                 elsepart: ASTNode):
        self.cond = cond
        self.thenpart = thenpart
        self.elsepart = elsepart
        self.children = [cond, thenpart, elsepart]

    def __str__(self):
        then_label = new_label("then")
        else_label = new_label("else")
        endif_label = new_label("endif")
        iftest = "\n".join([str(it) for it in flatten(self.cond.c_eval(then_label, else_label))])
        return f'''
            {iftest}\n{then_label}:\n{self.thenpart}\n
            jump {endif_label}\n
            {else_label}:\n{self.elsepart}\n
            {endif_label}:
        '''

class WhileNode(ASTNode):
    """while_stmt : "while" condition stmt_block"""
    """if condition stmt_block [otherwise*]"""
    def __init__(self,
                 cond: ASTNode,
                 whilepart: ASTNode):
        self.cond = cond
        self.whilepart = whilepart
        self.children = [cond, whilepart]

    def __str__(self):
        cond_label = new_label("cond")
        loop_label = new_label("loop")
        endloop_label = new_label("endloop")
        iftest = "\n".join([str(it) for it in flatten(self.cond.c_eval(loop_label, endloop_label))])
        return f'''
            {cond_label}:\n{iftest}\n
            {loop_label}:\n{self.whilepart}\n
            jump {cond_label}\n{endloop_label}
        '''


class AndNode(ASTNode):
    """Boolean and, short circuit; can be evaluated for jump or for boolean value"""
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right
        self.children = [left, right]

    def c_eval(self, true_branch: str, false_branch: str) -> List[str]:
        """Use in a conditional branch"""
        continue_label = new_label("and")
        return ( self.left.c_eval(continue_label, false_branch)
                 + [continue_label + ":"]
                 + self.right.c_eval(true_branch, false_branch)
                 )


class OrNode(ASTNode):
    """Boolean or, short circuit; can be evaluated for jump or for boolean value"""

    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right
        self.children = [left, right]

    def c_eval(self, true_branch: str, false_branch: str) -> List[str]:
        """Use in a conditional branch"""
        continue_label = new_label("or")
        return (self.left.c_eval(true_branch, continue_label)
                + [continue_label + ":"]
                + self.right.c_eval(true_branch, false_branch)
                )


class ComparisonNode(ASTNode):
    """
    Comparisons are the leaves of conditional branches
    and can also return boolean values
    """
    def __init__(self, comp_op: str, left: ASTNode, right: ASTNode):
        self.comp_op = comp_op
        self.left = left
        self.right = right
        self.children = [right, left]

    def c_eval(self, true_branch: str, false_branch: str) -> List[str]:
        bool_code = self.children
        return bool_code + [f"call {self.get_type()}:{self.comp_op}\njump_if {true_branch}", f"jump {false_branch}"]

    def get_type(self):
        if type(self.left) == type(ConstNode(3)) or type(self.right) == type(ConstNode(3)):
            return "Int"
        elif type(self.left) == type(StrConstNode("hi")) or type(self.right) == type(StrConstNode("Hi")):
            return "String"
        else:
            return "Obj"

class NotNode(ASTNode):
    """"not" r_exp -> not"""
    def __init__(self, right: List[ASTNode]):
        self.right = right
        self.children = right

    def c_eval(self, true_branch: str, false_branch: str) -> List[str]:
        return self.right.c_eval(false_branch, true_branch)

class MethodCallNode(ASTNode):
    """r_exp "." ident "(" args ")"""
    def __init__(self, r_exp, ident: ASTNode, args: List[ASTNode]):
        self.r_exp = r_exp
        self.ident = ident
        self.args = args
        self.children = [r_exp, ident, args]

    def __str__(self):
        if type(self.r_exp) is type(LoadNode("test")):
            if len(self.args) > 0:
                return [f"{self.r_exp}\n{self.args}\ncall {self.ident}"]
            else:
                return f"{self.r_exp}\ncall {self.get_type()}:{self.ident}"

    def get_type(self):
        if type(self.r_exp) == type(LoadNode("test")):
            return type_table[self.r_exp.var.name]
        else:
            return "Hello"

class ArgsNode(ASTNode):
    """r_exp"""
    def __init__(self, right: ASTNode):
        self.right = right
        self.children = [right]

    def __str__(self):
        return str(self.right)


class OpNode(ASTNode):
    """Arithmetic operations"""
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op
        self.left = left
        self.right = right
        self.children = [left, right]
        self.type = self.right.type

    def __str__(self):
        ret = "\n".join([str(re) for re in flatten(self.r_eval())])
        return ret

    def r_eval(self) -> List[str]:
        return [self.left, self.right, f"call {self.right.type}:{self.op}"]

    def type_check(self):
        if self.left.type != self.right.type:
            raise TypeError(f"Type mismatch between {self.left} and {self.right}")
        else:
            return self.left.type


class NegateNode(ASTNode):
    """Arithmetic operations"""
    def __init__(self, exps: List[ASTNode]):
        self.exps = exps
        self.children = exps

    def __str__(self):
        ret = "\n".join([str(re) for re in flatten(self.r_eval())])
        return ret

    def r_eval(self) -> List[str]:
        return [self.exps, "const 0", "call Int:sub"]


class ConstNode(ASTNode):
    """Integer constant"""
    def __init__(self, number: str):
        self.const = number
        self.type = "Int"

    def __str__(self):
        return f"const {self.const}"

    def c_eval(self):
        return f"{self.const}"


class StrConstNode(ASTNode):
    """string constant"""
    def __init__(self, string: str):
        self.string = string
        self.type = "String"

    def __str__(self):
        return f"const {self.string}"

    def c_eval(self):
        return f"{self.string}"

class StoreNode(ASTNode):
    """ident   -> call_var"""
    def __init__(self, ident: ASTNode):
        self.ident = ident
        self.children = [ident]

    def __str__(self):
        return f"store {self.ident}"

    def initialization(self, visit_state: dict):
        clazz = visit_state["current_class"]
        method = visit_state["current_method"]
        if isinstance(self.ident, VarNode):
            loc_dict = visit_state[clazz]["methods"][method]["locals"]
            if self.ident.name not in loc_dict.keys():
                loc_dict[self.ident.name] = "Obj"

    def c_eval(self):
        return f"{self.ident}"


class StoreFieldNode(ASTNode):
    def __init__(self,
                 field: ASTNode,
                 value: ASTNode):
        self.field = field
        self.value = value
        self.children = [field, value]

    def __str__(self):
        return f'''
            {self.field}\nstore_field {self.value}
        '''


class LoadNode(ASTNode):
    """ident   -> call_var"""
    def __init__(self, var: ASTNode):
        self.var = var
        self.children = [var]

    def __str__(self):
        return f"load {self.var}"

    def r_eval(self) -> List[str]:
        return [f"load {self.var}"]


class LoadFieldNode(ASTNode):
    def __init__(self,
                 field: ASTNode,
                 value: ASTNode):
        self.field = field
        self.value = value
        self.children = [field, value]

    def __str__(self):
        return f'''
            {self.field}\nload_field {self.value}
        '''


class VarNode(ASTNode):
    def __init__(self, name: str):
        self.name = name
        self.type = "save"

    def __str__(self):
        return f"{self.name}"


class ASTBuilder(Transformer):
    """Translate Lark tree to AST"""
    def program(self, e):
        log.debug("->program")
        classes, methods, stmt_block = e
        return ProgramNode(classes, methods, stmt_block)

    def classes(self, e):
        return e

    def clazz(self, e):
        log.debug("->clazz")
        name, formals, super, methods, constructor = e
        if formals is None:
            formals = []
        if methods is None:
            methods = []
        return ClassNode(name, formals, super, methods, constructor)

    def methods(self, e):
        return e

    def method(self, e):
        log.debug("->method")
        name, formals, returns, body = e
        if formals is None:
            formals = []
        if returns is None:
            returns = "Obj"
        return MethodNode(name, formals, returns, body)

    def formals(self, e):
        return e

    def formal(self, e):
        log.debug("->formal")
        var_name, var_type = e
        return FormalNode(var_name, var_type)

    def block(self, e):
        return e

    def stmt_block(self, e) -> ASTNode:
        log.debug("->block")
        return BlockNode(e)

    def assignment(self, e):
        left, ident, right = e
        return AssNode(left, ident, right)

    def method_call(self, e):
        if (len(e) == 2):
            right, ident = e
            args = []
        else:
            right, ident, args = e
        return MethodCallNode(right, ident, args)

    def args(self, e):
        value = e[0]
        return ArgsNode(value)

    def while_stmt(self, e) -> ASTNode:
        log.debug("->while_stmt")
        cond, whilepart = e
        return WhileNode(cond, whilepart)

    def if_stmt(self, e) -> ASTNode:
        log.debug("->if_stmt")
        cond, thenpart, elsepart = e
        return IfNode(cond, thenpart, elsepart)

    def else_stmt(self, e) -> ASTNode:
        log.debug("->elseblock")
        return e[0]  # Unwrap one level of block

    def condition(self, e):
        log.debug("->condition")
        return e

    def nots(self, e):
        log.debug("->not")
        return NotNode(e[0])

    def bool_and(self, e):
        left, right = e
        return AndNode(left, right)

    def bool_or(self, e):
        left, right = e
        return OrNode(left, right)

    def less_than(self, e):
        left, right = e
        return ComparisonNode("less", left, right)

    def greater_than(self, e):
        left, right = e
        return ComparisonNode("less", right, left)

    def less_equal(self, e):
        left, right = e
        return OrNode(ComparisonNode("less", left, right), ComparisonNode("equals", left, right))

    def greater_equal(self, e):
        left, right = e
        return OrNode(ComparisonNode("less", right, left), ComparisonNode("equals", right, left))

    def equals(self, e):
        left, right = e
        return ComparisonNode("equals", left, right)

    def plus(self, e):
        left, right = e
        return OpNode("plus", left, right)

    def sub(self, e):
        left, right = e
        return OpNode("sub", left, right)

    def mult(self, e):
        left, right = e
        return OpNode("mult", left, right)

    def div(self, e):
        left, right = e
        return OpNode("div", left, right)

    def neg(self, e):
        return NegateNode(e[0])

    def store(self, e):
        return StoreNode(e[0])

    def store_field(self, e):
        field, value = e
        return StoreFieldNode(field, value)

    def load(self, e):
        return LoadNode(e[0])

    def load_field(self, e):
        field, value = e
        return LoadFieldNode(field, value)

    def ident(self, e):
        log.debug("->variable_ref")
        return VarNode(e[0].value)

    def const(self, e):
        return ConstNode(e[0].value)

    def strconst(self, e):
        return StrConstNode(e[0].value)

    def lit_not(self, e):
        return ConstNode(e[0].value)

    def lit_true(self, e):
        return ConstNode(e[0].value)

    def lit_false(self, e):
        return ConstNode(e[0].value)

    def returns(self, e):
        return ReturnNode(e)


def main():
    args = cli()
    quack_parser = Lark(open("qklib/quack_grammar.txt"), parser='lalr')
    quack = quack_parser.parse
    text = "".join(args.source.readlines())
    #code = sys.stdin.read()
    tree = quack(text)
    #print(tree.pretty())

    #ultimate transformation
    ast: ASTNode = ASTBuilder().transform(tree)
    builtins = open("qklib/builtin_methods.json")
    symtab = json.load(builtins)
    #ast.walk(symtab, initialization_walk, type_check_walk)
    #print("AST")
    print(ast)
    json.dumps(symtab,indent=4)


if __name__ == '__main__':
    if len(sys.argv) < 1:
        sys.exit(1)
    main()
    #os.system('./bin/tiny_vm Quack')