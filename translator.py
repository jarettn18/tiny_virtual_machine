from lark import Lark, Transformer, visitors, v_args

"""
ADD SUPPORT FOR:
Integer Assignments
    -i: Int = 42;
    -j: Int = i - 32;
    j.print();
String Assignments:
    -cat: String = "Nora";
    -other: String = " can solve puzzles";
    (cat + other).print();
    "\n".print();
    
Writing your own unit tests:
    -Add a .asm file to tests/src
    -add a .txt file to tests/expect
    -add file/type of testing to src/TESTS.csv
"""
grammar2 = """
        ?start: stmt*               
        
        ?stmt: lexp typedecl "=" exp ";" //-> create_var
            | lexp "." method "(" args ")" ";"       //-> method_call
        
        ?exp: product
        | exp "+" product   //-> add
        | exp "-" product   //-> sub

        ?product: atom
        | product "*" atom  //-> mul
        | product "/" atom  //-> div

        ?atom: NUMBER           -> number
         | "-" atom         //-> neg
         | NAME             //-> var
         | "(" exp ")"
         
        lexp: NAME //-> init_var
        typedecl: ":" NAME
        args: NAME*
        method: NAME
        
        
        %import common.NUMBER
        %import common.CNAME -> NAME
        %import common.WS_INLINE

        %ignore WS_INLINE
        """

practice_grammar = """
                    stmt -> Lexpr typedecl "=" exp ";"
                    Lexpr -> IDENT
                    Typedecl -> ":" IDENT
                    
                    ?exp: NUMBER    -> number
                    """
grammar = """
        ?start: stmt*               
        
        ?stmt: lexp typedecl "=" exp ";"        
            | lexp "." method "(" args ")" ";"
        
        exp: sum
            | sent
            | bool
            
            
        ?sum: product
            | sum "+" product   -> add
            | sum "-" product   -> sub
    
        ?product: atom
            | product "*" atom  -> mul
            | product "/" atom  -> div
    
        ?atom: NUMBER           -> number
             | "-" atom         -> neg
             | NAME             -> var
             | "(" sum ")"
             
        lexp: NAME
            | STRING
        typedecl: ":" NAME
        args: NAME*
        method: NAME
        bool: "true"        -> ctrue   
            | "false"       -> cfalse    
            | "nothing"        -> cnone
            
        sent: STRING              -> cstring
            | sent "+" STRING   -> addstring
            | NAME "+" STRING     -> addvarstring
        
        
        
        
        %import common.NUMBER
        %import common.CNAME -> NAME
        %import common.WS_INLINE
        %import common.ESCAPED_STRING -> STRING

        %ignore WS_INLINE
        """
calc_grammar = """
    ?start: sum
          | NAME "=" sum    -> assign_var

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    
    %ignore WS_INLINE
"""
local_vars = {}

@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg
    number = int

    def __init__(self):
        self.vars = {}

    def init_var(self, var):
        if var not in list(self.vars.keys()):
            print("var is", var)

        ### TODO MAKE .LOCAL VARIABLES INIT AT TOP OF ASM FILE
        return var

    def assert_type(self, type):
        return type

    def create_var(self, lexp, typedecl, exp):

        self.vars[lexp] = [typedecl, exp]
        local_vars[lexp] = [typedecl, exp]
        data = (f"{exp}\n"
                f"store {lexp}")
        return data

    def add(self, this, other):
        data = (f"{other}\n"
                f"{this}\n"
                f"call Int:plus")

        return data

    def addstring(self, this, other):
        data = (f"const {other}\n"
                f"{this}\n"
                f"call String:plus")
        return data

    def addvarstring(self, this, other):
        data = (f"const {other}\n"
                f"load {this}\n"
                f"call String:plus")
        return data

    def sub(self, this, other):
        data = (f"{other}\n"
                f"{this}\n"
                f"call Int:sub")

        return data

    def mul(self, this, other):
        data = (f"{other}\n"
                f"{this}\n"
                f"call Int:mul")

        return data

    def div(self, this, other):
        data = (f"{other}\n"
                f"{this}\n"
                f"call Int:div")

        return data

    def neg(self, this):
        data = (f"{this}\n"
                f"const 0\n"
                f"call Int:sub")

        return data

    def number(self, this):
        data = f"const {this}"
        #print(data)
        return data

    def cstring(self, this):
        data = f"const {this}"
        return data

    def ctrue(self):
        data = f"const true"
        return data

    def cfalse(self):
        data = f"const false"
        return data

    def cnone(self):
        data = f"const nothing"
        return data

    def assign_var(self, name, type, value):
        self.vars[name] = value
        data = (f"{value}\n"
                f"store {name}")
        return data

    def var(self, name):
        return f"load {name}"

class vis(visitors.Visitor_Recursive):

    def __init__(self, fp):
        self.var_table = {}
        self.stack = []
        self.fp = fp

    def __default__(self, tree):

        if tree.data == "lexp":
            if tree.children[0].value not in self.var_table and tree.children[0].type == "NAME":
                self.var_table[tree.children[0].value] = "added"
            self.stack.append(tree.children[0].value)

    def typedecl(self, tree):
        if tree.data == "typedecl":
            lexp = self.stack.pop()
            self.var_table[lexp] = tree.children[0].value
            self.stack.append(lexp)

    def exp(self, tree):
        if tree.data == "exp":
            self.fp.write(f"{tree.children[0]}\n")
            #print(f"{tree.children[0]}\n")
            x = self.stack.pop()
            self.fp.write(f"store {x}\n")
            #print(f"store {x}\n")

    def method(self, tree):
        if tree.data == "method":
            #lexp of the method
            x = self.stack.pop()
            type = "String"
            if (x in self.var_table):
                self.fp.write(f"load {x}\n")
                type = self.var_table[x]
            else:
                self.fp.write(f"const {x}\n")
            #print(f"load {x}\n")
            #method call
            self.fp.write(f"call {type}:{tree.children[0]}\n")


            #print(f"Call {type}:{tree.children[0]}\n")

    def NUMBER(self, tree):
        if tree.data == "NUMBER":
            print("found a number")


calc_parser = Lark(calc_grammar, parser='lalr', transformer=CalculateTree())
#calc_parser = Lark(calc_grammar)
calc_parser = Lark(grammar, parser='lalr', transformer=CalculateTree())
calc = calc_parser.parse

def main():
    local_vars = {}
    s = "-5 + 4"
    #s = "i: Int = 42 + 13;j: Int = i - 32;j.print();cat: String = \"Nora\";cat.print(); "
    s = "i: String = \"Hello \";j: String = i + \"World\";j.print();\"hi\".print();"
    s = "x: String = \"Hello\" + \" World\" + \"hi\";x.print();"
    #s = "i: Bool = true;"
    #s = "i: Int = 42 + 3;"
    x = "j: Int = i - 32;"
    #x = "j: Int = i - 32;"

    #print(calc(s))
    with open("tests/src/Testing.asm", "w") as fp:
        #print(calc_parser.parse(s).pretty())
        #print(calc_parser.parse(s))
        fp.write(".class Testing:Obj\n\n.method $constructor\n")
        #fp.write(calc(s) + "\n")
        data = calc(s)

        y = data.find_data("lexp")
        for l_expression in y:
            if (l_expression.children[0].value not in local_vars and l_expression.children[0].type == "NAME"):
                local_vars[l_expression.children[0].value] = "added"
                fp.write(f".local {l_expression.children[0].value}\n")
                #print(f".local {l_expression.children[0].value}\n")
        vis(fp).visit(data)

        fp.write("return 0")
    fp.close()

def test():
    print(calc("1+1"))

if __name__ == '__main__':
    # test()
    main()