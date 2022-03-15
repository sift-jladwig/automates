from automates.program_analysis.CAST2GrFN.model.cast import (
    AstNode,
    Assignment,
    Attribute,
    BinaryOp,
    BinaryOperator,
    Boolean,
    Call,
    ClassDef,
    Dict,
    Expr,
    FunctionDef,
    List,
    Loop,
    ModelBreak,
    ModelContinue,
    ModelIf,
    ModelReturn,
    Module,
    Name,
    Number,
    Set,
    String,
    SourceRef,
    Subscript,
    Tuple,
    UnaryOp,
    UnaryOperator,
    VarType,
    Var,
)

import typing

# used in ContainerScopePass functions `con_scope_to_str()` and `visit_name()`
CON_STR_SEP = "."

# TODO: do we need to add any other characters to ensure the name 
# is an illegal identifier
LOOPBODY = "loop-body"
ELSEBODY = "else-body"
IFBODY = "if-body"
LOOPEXPR = "loop-expr"
IFEXPR = "if-expr"

def con_scope_to_str(scope: typing.List):
    return CON_STR_SEP.join(scope)

def var_dict_to_str(str_start, vars):
    vars_id_and_names = [f" {name}: {id}" for id, name in vars.items()]
    return str_start + ", ".join(vars_id_and_names)

def ann_cast_name_to_fullid(node):
    """
    Returns a string representing the fullid of the name node.
    The fullid has format
      'name.id.version.con_scopestr'
    This should only be called after both VariableVersionPass and 
    ContainerScopePass have completed
    """
    pieces = [node.name, str(node.id), str(node.version), con_scope_to_str(node.con_scope)]
    return CON_STR_SEP.join(pieces)

def build_fullid(var_name: str, id: int, version: int, con_scopestr: str):
    """
    Returns a string representing the fullid.
    The fullid has format
      'var_name.id.version.con_scopestr'
    """
    pieces = [var_name, str(id), str(version), con_scopestr]
    return CON_STR_SEP.join(pieces)

class AnnCast:
    def __init__(self, ann_nodes: List):
        self.nodes = ann_nodes
        # TODO: I think it would be better if the `name` attribute of FunctionDef's actually
        # stored `Name` nodes instead of just being a str.  Storing a `Name` node there would allow
        # us to refer to FunctionDef's with an ID.  On the GCC side, the gcc AST json already has these
        # IDs filled out, and they are stored at the `Name` nodes at call sites.  We could add this same ID
        # to the `Name` node created at the FunctionDef.  
        # On the Python side, we have rules to assign IDs at call sites.  It is likely those same rules coudl
        # be used when parsing FunctionDef's.
        # Once this is implemented, this dict could map function IDs to there FunctionDef nodes.  
        # For now, it maps a str (the name attribute of a FunctionDef) to the FunctionDef node.
        # For now, this dict will be filled out during the ContainerScopePass.  Possibly this could be moved to a 
        # different pass, but will need to be during/after IdCollapsePass
        self.func_name_to_def = {}
        self.grfn_id_to_grfn_var = {}
        # the fullid of a AnnCastName node is a string which includes its variable name, numerical id,  version, and scope
        self.fullid_to_grfn_id = {}

class AnnCastNode(AstNode):
    def __init__(self,*args, **kwargs):
        self.incoming_vars = {}
        self.outgoing_vars = {}
        AstNode.__init__(self)

class AnnCastAssignment(AnnCastNode):
    def __init__(self, left, right, source_refs ):
        self.left = left
        self.right = right
        self.source_refs = source_refs

    def __str__(self):
        return Assignment.__str__(self)

class AnnCastAttribute(AnnCastNode):
    def __init__(self, value, attr, source_refs):
        self.value = value
        self.attr = attr
        self.source_refs = source_refs

    def __str__(self):
        return Attribute.__str__(self)

class AnnCastBinaryOp(AnnCastNode):
    def __init__(self, op, left, right, source_refs):
        self.op = op
        self.left = left
        self.right = right
        self.source_refs = source_refs

    def __str__(self):
        return BinaryOp.__str__(self)

class AnnCastBoolean(AnnCastNode):
    def __init__(self, boolean, source_refs):
        self.boolean = boolean
        self.source_refs = source_refs

    def __str__(self):
        return Boolean.__str__(self)

class AnnCastCall(AnnCastNode):
    def __init__(self, func, arguments, source_refs):
        self.func = func
        self.arguments = arguments
        self.source_refs = source_refs

    def __str__(self):
        return Call.__str__(self)

class AnnCastClassDef(AnnCastNode):
    def __init__(self, name, bases, func, fields, source_refs):
        self.name = node.name
        self.bases = node.bases
        self.func = node.func
        self.fields = node.fields
        self.source_refs = node.source_refs

    def __str__(self):
        return ClassDef.__str__(self)

class AnnCastDict(AnnCastNode):
    def __init__(self, keys, values, source_refs):
        self.keys = keys
        self.values = values
        self.source_refs = source_refs

    def __str__(self):
        return Dict.__str__(self)

class AnnCastExpr(AnnCastNode):
    def __init__(self, expr, source_refs):
        self.expr = expr
        self.source_refs = source_refs

    def __str__(self):
        return Expr.__str__(self)

class AnnCastFunctionDef(AnnCastNode):
    def __init__(self, name, func_args, body, source_refs):
        self.name = name
        self.func_args = func_args
        self.body = body
        self.source_refs = source_refs

        # dicts mapping a Name id to its string name
        # used for container interfaces
        self.modified_vars: typing.Dict[id, str]
        self.accessed_vars: typing.Dict[id, str]
        self.con_scope: typing.List
    
        # dicts mapping a Name id to its GrFN variable identifier (VariableIdentifier)
        self.incoming_interface_in: typing.Dict
        self.incoming_interface_out: typing.Dict
        self.outgoing_interface_in: typing.Dict
        self.outgoing_interface_out: typing.Dict

        # dict mapping Name id to highest version at end of "block"
        # TODO: What about using a default dict
        self.body_highest_var_vers = {}

    def __str__(self):
        return FunctionDef.__str__(self)

class AnnCastList(AnnCastNode):
    def __init__(self, values, source_refs):
        self.values = values
        self.source_refs = source_refs

    def __str__(self):
        return List.__str__(self)

class AnnCastClassDef(AnnCastNode):
    def __init__(self, name, bases, funcs, fields, source_refs):
        self.name = name
        self.bases = bases
        self.funcs = funcs
        self.fields = fields
        self.source_refs = source_refs

    def __str__(self):
        return ClassDef.__str__(self)

class AnnCastLoop(AnnCastNode):
    def __init__(self, expr, body, source_refs):
        self.expr = expr
        self.body = body
        self.source_refs = source_refs

        # dicts mapping a Name id to its string name
        # used for container interfaces
        self.modified_vars: typing.Dict[id, str]
        self.accessed_vars: typing.Dict[id, str]
        self.con_scope: List

        # dicts mapping Name id to highest version at end of "block"
        # TODO: What about using a default dict
        self.expr_highest_var_vers = {}
        self.body_highest_var_vers = {}

        # dicts mapping a Name id to its GrFN variable identifier (VariableIdentifier)
        self.incoming_interface_in: typing.Dict
        self.incoming_interface_out: typing.Dict
        self.outgoing_interface_in: typing.Dict
        self.outgoing_interface_out: typing.Dict
        self.condition_in: typing.Dict
        self.condition_out: typing.Dict
        self.decision_in: typing.Dict
        self.decision_out: typing.Dict
        self.exit: typing.Dict

        # TODO: Might delete below attributes
        # Dicts mapping strings to Names
        self.loop_body_variables = {}
        self.entry_variables = {}

        # Entry and Exit condition variables
        # used at the top decision to determin `entry_variables`
        self.entry_condition_variables = {}

        # used at the bottom decision to determin `exit_variables`
        # NOTE: depending on how Decision nodes are handled in GrFN, this
        # condition variable may not be necessary
        self.exit_condition_var = None


    def __str__(self):
        return Loop.__str__(self)


class AnnCastModelBreak(AnnCastNode):
    def __init__(self, source_refs):
        self.source_refs = source_refs

    def __str__(self):
        return ModelBreak.__str__(self)

class AnnCastModelContinue(AnnCastNode):
    def __init__(self, node:ModelContinue):
        self.source_refs = node.source_refs

    def __str__(self):
        return ModelContinue.__str__(self)

class AnnCastModelIf(AnnCastNode):
    def __init__(self, expr, body, orelse, source_refs):
        self.expr = expr
        self.body = body
        self.orelse = orelse

        # dicts mapping a Name id to string name
        # used for container interfaces
        self.modified_vars: typing.Dict[id, str]
        self.accessed_vars: typing.Dict[id, str]
        self.con_scope: List

        # dicts mapping Name id to highest version at end of "block"
        # TODO: What about using a default dict
        self.expr_highest_var_vers = {}
        self.ifbody_highest_var_vers = {}
        self.elsebody_highest_var_vers = {}

        # dicts mapping a Name id to its GrFN variable identifier (VariableIdentifier)
        self.incoming_interface_in: typing.Dict
        self.incoming_interface_out: typing.Dict
        self.outgoing_interface_in: typing.Dict
        self.outgoing_interface_out: typing.Dict
        self.condition_in: typing.Dict
        self.condition_out: typing.Dict
        self.decision_in: typing.Dict
        self.decision_out: typing.Dict

        self.source_refs = source_refs

        # TODO: Maybe delete
        self.updated_vars_if_branch = {}
        self.updated_vars_else_branch = {}

        

    def __str__(self):
        return ModelIf.__str__(self)

class AnnCastModelReturn(AnnCastNode):
    def __init__(self, value, source_refs):
        self.value = value
        self.source_refs = source_refs

    def __str__(self):
        return ModelReturn.__str__(self)

class AnnCastModule(AnnCastNode):
    def __init__(self, name, body, source_refs):
        self.name = name
        self.body = body
        self.source_refs = source_refs

    def __str__(self):
        return Module.__str__(self)


class AnnCastName(AnnCastNode):
    def __init__(self, name, id, source_refs):
        self.name = name
        self.id = id
        self.source_refs = source_refs
        # container_scope is used to aid GrFN generation
        self.con_scope = None
        # versions are bound to the cope of the variable
        self.version = None
        self.grfn_id = None

    def __str__(self):
        return Name.__str__(self)


class AnnCastNumber(AnnCastNode):
    def __init__(self, number, source_refs):
        self.number = number
        self.source_refs = source_refs

    def __str__(self):
        return Number.__str__(self)

class AnnCastSet(AnnCastNode):
    def __init__(self, values, source_refs):
        self.values = values
        self.source_refs = source_refs

    def __str__(self):
        return Set.__str__(self)

class AnnCastString(AnnCastNode):
    def __init__(self, string, source_refs):
        self.string = string
        self.source_refs = source_refs

    def __str__(self):
        return String.__str__(self)

class AnnCastSubscript(AnnCastNode):
    def __init__(self, value, slice, source_refs):
        self.value = node.value
        self.slice = node.slice
        self.source_refs = source_refs

    def __str__(self):
        return Subscript.__str__(self)

class AnnCastTuple(AnnCastNode):
    def __init__(self, values, source_refs):
        self.values = values
        self.source_refs = source_refs

    def __str__(self):
        return Tuple.__str__(self)

class AnnCastUnaryOp(AnnCastNode):
    def __init__(self, op, value, source_refs):
        self.op = op
        self.value = value
        self.source_refs = source_refs

    def __str__(self):
        return UnaryOp.__str__(self)

class AnnCastVar(AnnCastNode):
    def __init__(self, val, type, source_refs):
        self.val = val
        self.type = type
        self.source_refs = source_refs

    def __str__(self):
        return Var.__str__(self)

