class Node:
    """
    Base class for all AST nodes.
    Every node must implement to_dict().
    """
    def to_dict(self):
        """Convert node to dictionary for JSON output IR"""
        raise NotImplementedError
    

class Program(Node):
    def __init__(self, items):
        self.items = items

    def to_dict(self):
        return {
            'type': 'Program',
            'items': [item.to_dict() for item in self.items]
        }


class FunctionDef(Node):
    def __init__(self, name, params, return_type, body, lineno):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'FunctionDef',
            'name': self.name,
            'params': [p.to_dict() for p in self.params],
            'return_type': self.return_type.to_dict(),
            'body': [s.to_dict() for s in self.body],
            'lineno': self.lineno
        }


class Param(Node):
    def __init__(self, name, type_node, lineno):
        self.name = name
        self.type_node = type_node
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'Param',
            'name': self.name,
            'param_type': self.type_node.to_dict(),
            'lineno': self.lineno
        }


class Type(Node):
    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno

    def to_dict(self):
        return {'type': 'Type', 'name': self.name, 'lineno': self.lineno}
    

class Comment(Node):
    def __init__(self, text, lineno):
        self.text = text
        self.lineno = lineno
    
    def to_dict(self):
        return {
            'type': 'Comment',
            'text': self.text,
            'lineno': self.lineno
        }
    

class AssignStmt(Node):
    """
    Assignment statement node
    
    Attributes:
        name: Variable name (string)
        expr: Expression being assigned (Node)
    """
    def __init__(self, name, expr, lineno):
        self.name = name
        self.expr = expr
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'AssignStmt',
            'name': self.name,
            'expr': self.expr.to_dict(),
            'lineno': self.lineno
        }


class IfStmt(Node):
    """
    If statement node
    
    Attributes:
        condition: Boolean expression (Node)
        true_body: Statement(s) to execute if true (Node)
        false_body: Statement(s) to execute if false (Node or None)
    """
    def __init__(self, condition, true_body, false_body, lineno):
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body
        self.lineno = lineno

    def to_dict(self):
        d = {
            'type': 'IfStmt',
            'condition': self.condition.to_dict(),
            'true_body': [s.to_dict() for s in self.true_body],
            'lineno': self.lineno
        }
        if self.false_body:
            d['false_body'] = [s.to_dict() for s in self.false_body]
        return d


class WhileStmt(Node):
    def __init__(self, condition, body, lineno):
        self.condition = condition
        self.body = body
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'WhileStmt',
            'condition': self.condition.to_dict(),
            'body': [s.to_dict() for s in self.body],
            'lineno': self.lineno
        }


class ReturnStmt(Node):
    def __init__(self, expr, lineno):
        self.expr = expr
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'ReturnStmt',
            'expr': self.expr.to_dict(),
            'lineno': self.lineno
        }


class BinOp(Node):
    """
    Binary operation node (e.g., +, -, *, /)
    
    Attributes:
        op: The operator (string)
        left: Left operand (Node)
        right: Right operand (Node)
    """
    def __init__(self, op, left, right, lineno):
        self.op = op
        self.left = left
        self.right = right
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'BinOp',
            'op': self.op,
            'left': self.left.to_dict(),
            'right': self.right.to_dict(),
            'lineno': self.lineno
        }


class UnaryOp(Node):
    def __init__(self, op, operand, lineno):
        self.op = op
        self.operand = operand
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'UnaryOp',
            'op': self.op,
            'operand': self.operand.to_dict(),
            'lineno': self.lineno
        }


class Constant(Node):
    """
    Constant value node (numbers, strings, booleans)
    
    Attributes:
        type: Type of constant ('int', 'bool')
        value: The actual value
    """
    def __init__(self, value_type, value, lineno):
        self.value_type = value_type
        self.value = value
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'Constant',
            'value_type': self.value_type,
            'value': self.value,
            'lineno': self.lineno
        }


class Identifier(Node):
    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'Identifier',
            'name': self.name,
            'lineno': self.lineno
        }


class FunctionCall(Node):
    def __init__(self, name, args, lineno):
        self.name = name
        self.args = args
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'FunctionCall',
            'name': self.name,
            'args': [a.to_dict() for a in self.args],
            'lineno': self.lineno
        }


class ListLiteral(Node):
    def __init__(self, elements, lineno):
        self.elements = elements
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'ListLiteral',
            'elements': [e.to_dict() for e in self.elements],
            'lineno': self.lineno
        }


class ListIndex(Node):
    def __init__(self, name, index, lineno):
        self.name = name
        self.index = index
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'ListIndex',
            'name': self.name,
            'index': self.index.to_dict(),
            'lineno': self.lineno
        }


class LenExpr(Node):
    def __init__(self, expr, lineno):
        self.expr = expr
        self.lineno = lineno

    def to_dict(self):
        return {
            'type': 'LenExpr',
            'expr': self.expr.to_dict(),
            'lineno': self.lineno
        }
