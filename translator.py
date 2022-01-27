from lark import Lark, Transformer, v_args

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

@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg
    number = int

    def __init__(self):
        self.vars = {}

    def add(self, this, other):
        data = (f"{other}\n"
                f"{this}\n"
                f"Call Int:plus")

        return data

    def sub(self, this, other):
        data = (f"{other}\n"
                f"{this}\n"
                f"Call Int:sub")

        return data

    def mul(self, this, other):
        data = (f"{other}\n"
                f"{this}\n"
                f"Call Int:mul")

        return data

    def div(self, this, other):
        data = (f"{other}\n"
                f"{this}\n"
                f"Call Int:div")

        return data

    def neg(self, this):
        data = (f"const 0\n"
                f"{this}\n"
                f"Call Int:sub")

        return data

    def number(self, this):
        return f"const {this}"

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        try:
            return self.vars[name]
        except KeyError:
            raise Exception("Variable not found: %s" % name)


calc_parser = Lark(calc_grammar, parser='lalr', transformer=CalculateTree())
#calc_parser = Lark(calc_grammar)
#calc_parser = Lark(calc_grammar, parser='lalr', transformer=CalculateTree())
calc = calc_parser.parse


def main():
    s = "(5-3)+2"

    #print(calc(s))
    """
    data = calc_parser.parse(s).pretty()
    data = data.replace("add", "call Int:plus")
    data = data.replace("sub", "call Int:sub")
    data = data.replace("mul", "call Int:mul")
    data = data.replace("div", "call Int:div")
    data = data.replace("neg", "call Int:sub\nconst 0")
    li = data.split("\n")
    new_data = ""
    for i in reversed(li):
        new_data = new_data + i + "\n"
        
    #print(new_data)
    """
    with open("unit_tests/Sample2.asm", "w") as fp:
    #print(calc_parser.parse(s).pretty())
    #print(calc_parser.parse(s))
        fp.write(".class Sample:Obj\n\n.method $constructor\n")
        fp.write(calc(s) + "\n")
        #print(calc(s))
        fp.write("call Int:print\npop\nreturn 0")
    fp.close()



def test():
    print(calc("1+1"))

if __name__ == '__main__':
    # test()
    main()