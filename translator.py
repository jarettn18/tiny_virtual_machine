from lark import Lark, Transformer, v_args

calc_grammar = """
    ?start: sum
          | NAME "=" sum    -> assign_var

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?atom: NUMBER           -> const
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

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        try:
            return self.vars[name]
        except KeyError:
            raise Exception("Variable not found: %s" % name)


#calc_parser = Lark(calc_grammar, parser='lalr', transformer=CalculateTree())
calc_parser = Lark(calc_grammar)
#calc_parser = Lark(calc_grammar, parser='lalr', transformer=CalculateTree())
calc = calc_parser.parse


def main():
    try:
        s = input('> ')
    except:
        pass

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
    with open("unit_tests/Sample.asm", "w") as fp:
    #print(calc_parser.parse(s).pretty())
    #print(calc_parser.parse(s))
        fp.write(".class Sample:Obj\n\n.method $constructor\n")
        fp.write(new_data)
        fp.write("call Int:print\npop\nreturn 0")
    fp.close()


def test():
    print(calc("1+1"))

if __name__ == '__main__':
    # test()
    main()