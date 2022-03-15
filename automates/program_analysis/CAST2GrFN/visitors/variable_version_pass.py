import typing
from collections import defaultdict
from functools import singledispatchmethod

from automates.program_analysis.CAST2GrFN.visitors.annotated_cast import *


class VariableVersionPass:
    def __init__(self, ann_cast: AnnCast):
        self.ann_cast = ann_cast
        self.nodes = self.ann_cast.nodes

        # dict mapping container scopes strs to dicts which
        # map Name id to highest version in that container scope
        self.con_scope_to_highest_var_vers = {}

        # Fill out the version field of AnnCastName nodes and
        # populate the dictionaries for containers nodes
        # that hold the mappings of variable ids to their 
        # highest version in that scope

        # FunctionDef: expectation is that arguments will receive correct version of zero when visiting
        # because FunctionDef has its own scope, nodes in the body should be able to be handled without special cases

        for node in self.ann_cast.nodes:
            # when visitor starts, assign_lhs is False
            self.visit(node, False)

    def init_highest_var_vers_dict(self, con_scopestr, var_ids):
        """
        Initialize highest var version dict for scope `con_scopestr`
        If the scope is the module, then use a defaultdict starting at zero
        otherwise, create a dictionary mapping each of the ids to zero
        """
        # DONE: add an additional var ids parameter, and initialize all those 
        # variables instead of defaultdict (unless con_scopestr is "module")
        # create versions 0 of any modified or accessed variables
        if con_scopestr == "module":
           self.con_scope_to_highest_var_vers[con_scopestr] = defaultdict(int)
        else:
            # TODO: Could we ever have a container with no modified or accessed variables?
            #       Maybe a debugging function that only prints?
            assert(len(var_ids) > 0)
            self.con_scope_to_highest_var_vers[con_scopestr] = {}
            for id in var_ids:
                self.con_scope_to_highest_var_vers[con_scopestr][id] = 0
            print(f"initialized highest_vars_vers_dict {self.con_scope_to_highest_var_vers[con_scopestr]}")
                       

    def get_highest_ver_in_con_scope(self, con_scopestr, id):
        """
        Grab the current version of `id` in scope for `con_scopestr`
        Should only be called after `con_scopestr` is in the `self.con_scope_to_highest_var_vers`
        """
        return self.con_scope_to_highest_var_vers[con_scopestr][id]

    def incr_version_in_con_scope(self, con_scopestr, id):
        """
        Grab the next version of `id` in scope for `con_scopestr`
        Should only be called after `con_scopestr` is in the `self.con_scope_to_highest_var_vers`
        """
        print(f"incr: id={id}  scope dictionary {con_scopestr}={self.con_scope_to_highest_var_vers[con_scopestr]} ")
        # TODO: if id is in the container scope, increment it
        if id in self.con_scope_to_highest_var_vers[con_scopestr]:
            #print(f"incr: id={id} is in dict")
            self.con_scope_to_highest_var_vers[con_scopestr][id] += 1
        # otherwise, add it as version 0
        else:
            #print(f"incr: id={id} is NOT in dict")
            self.con_scope_to_highest_var_vers[con_scopestr][id] = 0

    def incr_vars_in_con_scope(self, scopestr, vars):
        """
        This will increment all versions of variables in `scopestr` that are
        in the iterable `vars` which contains variable ids
        """
        for var_id in vars:
            self.incr_version_in_con_scope(scopestr, var_id)

    def merge_accessed_modified_vars(self, node):
        """
        Merge the ids of the accessed and modified variables of `node` and
        return the merge as a list ids
        """
        ids = set(node.modified_vars.keys())
        ids.update(node.accessed_vars.keys())
        return list(ids)
        

    def visit(self, node: AnnCastNode, assign_lhs: bool):
        # type(node) is a string which looks like
        # "class '<path.to.class.ClassName>'"
        class_name = str(type(node))
        last_dot = class_name.rfind(".")
        class_name = class_name[last_dot + 1 : -2]
        print(f"\nProcessing node type {class_name}")
        return self._visit(node, assign_lhs)

    @singledispatchmethod
    def _visit(self, node: AnnCastNode, assign_lhs: bool):
        """
        Visit each AnnCastNode
        Parameters:
          - `assign_lhs`: this denotes whether we are visiting the LHS or RHS of an AnnCastAssignment
                      This is used to determine whether a variable (AnnCastName node) is
                      accessed or modified in that context
        """
        raise Exception(f"Unimplemented AST node of type: {type(node)}")

    def visit_node_list(self, node_list: typing.List[AnnCastNode], assign_lhs):
        return [self.visit(node, assign_lhs) for node in node_list]

    @_visit.register
    def visit_assignment(self, node: AnnCastAssignment, assign_lhs: bool):
        # TODO: what if the rhs has side-effects
        self.visit(node.right, assign_lhs)
        assert isinstance(node.left, AnnCastVar)
        self.visit(node.left, True)

    @_visit.register
    def visit_attribute(self, node: AnnCastAttribute, assign_lhs: bool):
        pass

    @_visit.register
    def visit_binary_op(self, node: AnnCastBinaryOp, assign_lhs: bool):
        # visit LHS first
        self.visit(node.left, assign_lhs)

        # visit RHS second
        self.visit(node.right, assign_lhs)

    @_visit.register
    def visit_boolean(self, node: AnnCastBoolean, assign_lhs: bool):
        pass

    @_visit.register
    def visit_call(self, node: AnnCastCall, assign_lhs: bool):
        assert isinstance(node.func, AnnCastName)
        self.visit_node_list(node.arguments, assign_lhs)
        # in the current scope, increment all versions of variables
        # that are modified by this call
        # TODO: Once FunctionDef store Name nodes, convert to ID
        # TODO: func_id = node.func.id
        func_name = node.func.name
        function_def = self.ann_cast.func_name_to_def[func_name]
        # the enclosing container scope is stored in the Call's AnnCastName node
        con_scopestr = con_scope_to_str(node.func.con_scope)
        self.incr_vars_in_con_scope(con_scopestr, function_def.modified_vars)

    
    # TODO: How to handle class definitions?
    @_visit.register
    def visit_class_def(self, node: AnnCastClassDef, assign_lhs: bool):
        pass

    @_visit.register
    def visit_dict(self, node: AnnCastDict, assign_lhs: bool):
        pass

    @_visit.register
    def visit_expr(self, node: AnnCastExpr, assign_lhs: bool):
        self.visit(node.expr, assign_lhs)

    @_visit.register
    def visit_function_def(self, node: AnnCastFunctionDef, assign_lhs: bool):
        # increment versions of vars in previous scope that are modified by this container
        prev_scopestr = con_scope_to_str(node.con_scope[:-1])
        for var_id in node.modified_vars:
            self.incr_version_in_con_scope(prev_scopestr, var_id)

        # Initialize scope_to_highest_var_vers
        con_scopestr = con_scope_to_str(node.con_scope)
        # DONE:
        # create versions 0 of any modified or accessed variables
        # use that merge_variables function on accessed_vars and modified_vars
        # pass in as extra parameter
        self.init_highest_var_vers_dict(con_scopestr, self.merge_accessed_modified_vars(node))
        
        # visit children
        self.visit_node_list(node.func_args, assign_lhs)
        self.visit_node_list(node.body, assign_lhs)

        # store highest var version
        node.body_highest_var_vers = self.con_scope_to_highest_var_vers[con_scopestr]

        # DEBUGGING
        print(f"\nFor FUNCTION: {con_scopestr}")
        print(f"  BodyHighestVers: {node.body_highest_var_vers}")

    @_visit.register
    def visit_list(self, node: AnnCastList, assign_lhs: bool):
        self.visit_node_list(node.values, assign_lhs)

    @_visit.register
    def visit_loop(self, node: AnnCastLoop, assign_lhs: bool):
        # Initialize scope_to_highest_var_version
        expr_scopestr = con_scope_to_str(node.con_scope + [LOOPEXPR])
        body_scopestr = con_scope_to_str(node.con_scope + [LOOPBODY])
        # Initialize LoopExpr
        # DONE:
        # create versions 0 of any modified or accessed variables
        # use that merge_variables function on accessed_vars and modified_vars
        # pass in as extra parameter
        self.init_highest_var_vers_dict(expr_scopestr, self.merge_accessed_modified_vars(node))

        # Initialize LoopBody
        # create versions 0 of any modified or accessed variables
        # use that merge_variables function on accessed_vars and modified_vars
        # pass in as extra parameter
        self.init_highest_var_vers_dict(body_scopestr, self.merge_accessed_modified_vars(node))

        # visit children
        self.visit(node.expr, assign_lhs)
        self.visit_node_list(node.body, assign_lhs)

        # store highest var version
        node.expr_highest_var_vers = self.con_scope_to_highest_var_vers[expr_scopestr]
        node.body_highest_var_vers = self.con_scope_to_highest_var_vers[body_scopestr]
        
        # increment versions of vars in previous scope that are modified by this container
        prev_scopestr = con_scope_to_str(node.con_scope[:-1])
        self.incr_vars_in_con_scope(prev_scopestr, node.modified_vars)

        # DEBUGGING
        print(f"\nFor LOOP: {con_scope_to_str(node.con_scope)}")
        print(f"  ExprHighestVers: {node.expr_highest_var_vers}")
        print(f"  BodyHighestVers: {node.body_highest_var_vers}")

    @_visit.register
    def visit_model_break(self, node: AnnCastModelBreak, assign_lhs: bool):
        pass

    @_visit.register
    def visit_model_continue(self, node: AnnCastModelContinue, assign_lhs: bool):
        pass

    @_visit.register
    def visit_model_if(self, node: AnnCastModelIf, assign_lhs: bool):
        # Initialize scope_to_highest_var_version
        expr_scopestr = con_scope_to_str(node.con_scope + [IFEXPR])
        ifbody_scopestr = con_scope_to_str(node.con_scope + [IFBODY])
        elsebody_scopestr = con_scope_to_str(node.con_scope + [ELSEBODY])
        # initialize IfExpr
        # DONE:
        # create versions 0 of any modified or accessed variables
        # use that merge_variables function on accessed_vars and modified_vars
        # pass in as extra parameter
        self.init_highest_var_vers_dict(expr_scopestr, self.merge_accessed_modified_vars(node))

        # initialize IfBody
        # create versions 0 of any modified or accessed variables
        # use that merge_variables function on accessed_vars and modified_vars
        # pass in as extra parameter
        self.init_highest_var_vers_dict(ifbody_scopestr, self.merge_accessed_modified_vars(node))

        # initialize ElseBody
        # create versions 0 of any modified or accessed variables
        # use that merge_variables function on accessed_vars and modified_vars
        # pass in as extra parameter
        self.init_highest_var_vers_dict(elsebody_scopestr, self.merge_accessed_modified_vars(node))

        # visit children
        self.visit(node.expr, assign_lhs)
        self.visit_node_list(node.body, assign_lhs)
        self.visit_node_list(node.orelse, assign_lhs)

        # store highest var version
        node.expr_highest_var_vers = self.con_scope_to_highest_var_vers[expr_scopestr]
        node.ifbody_highest_var_vers = self.con_scope_to_highest_var_vers[ifbody_scopestr]
        node.elsebody_highest_var_vers = self.con_scope_to_highest_var_vers[elsebody_scopestr]

        print(f"\nFor IF: {con_scope_to_str(node.con_scope)}")
        print(f"  ExprHighestVers: {node.expr_highest_var_vers}")
        print(f"  IfBodyHighestVers: {node.ifbody_highest_var_vers}")
        print(f"  ElseBodyHighestVers: {node.elsebody_highest_var_vers}")
        prev_scopestr = con_scope_to_str(node.con_scope[:-1])
        print("Enclosing scope:")
        print(f"  {prev_scopestr}: {self.con_scope_to_highest_var_vers[prev_scopestr] }")

        # increment versions of vars in previous scope that are modified by this container
        prev_scopestr = con_scope_to_str(node.con_scope[:-1])
        self.incr_vars_in_con_scope(prev_scopestr, node.modified_vars)

    @_visit.register
    def visit_return(self, node: AnnCastModelReturn, assign_lhs: bool):
        self.visit(node.value, assign_lhs)

    @_visit.register
    def visit_module(self, node: AnnCastModule, assign_lhs: bool):
        # TODO: decide if we want to keep track of versions in module
        # TODO:
        # create versions 0 of any modified or accessed variables
        # use that merge_variables function on accessed_vars and modified_vars
        # pass in as extra parameter
        # This won't work for module, instead we actually do want a defaultdict
        # since at the module it can "see" all variables
        self.init_highest_var_vers_dict("module",[])
        self.visit_node_list(node.body, assign_lhs)

    @_visit.register
    def visit_name(self, node: AnnCastName, assign_lhs: bool):
        con_scopestr = con_scope_to_str(node.con_scope)
        # TODO: Should we not increment on first use even its LHS of an assigment?
        if assign_lhs:
            print(f"On LHS: {node.name}:{node.id}" )
            # if not in, skip this increment
            self.incr_version_in_con_scope(con_scopestr, node.id)
            print("after incr scope dict is",  self.con_scope_to_highest_var_vers[con_scopestr])
        node.version = self.get_highest_ver_in_con_scope(con_scopestr, node.id)

    @_visit.register
    def visit_number(self, node: AnnCastNumber, assign_lhs: bool):
        pass

    @_visit.register
    def visit_set(self, node: AnnCastSet, assign_lhs: bool):
        pass

    @_visit.register
    def visit_string(self, node: AnnCastString, assign_lhs: bool):
        pass

    @_visit.register
    def visit_subscript(self, node: AnnCastSubscript, assign_lhs: bool):
        pass

    @_visit.register
    def visit_tuple(self, node: AnnCastTuple, assign_lhs: bool):
        pass

    @_visit.register
    def visit_unary_op(self, node: AnnCastUnaryOp, assign_lhs: bool):
        self.visit(node.value, assign_lhs)

    @_visit.register
    def visit_var(self, node: AnnCastVar, assign_lhs: bool):
        self.visit(node.val, assign_lhs)
