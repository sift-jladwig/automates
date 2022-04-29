
from automates.program_analysis.CAST2GrFN.ann_cast.annotated_cast import AnnCast
from automates.program_analysis.CAST2GrFN.ann_cast.id_collapse_pass import IdCollapsePass
from automates.program_analysis.CAST2GrFN.ann_cast.container_scope_pass import ContainerScopePass
from automates.program_analysis.CAST2GrFN.ann_cast.variable_version_pass import VariableVersionPass
from automates.program_analysis.CAST2GrFN.ann_cast.grfn_var_creation_pass import GrfnVarCreationPass
from automates.program_analysis.CAST2GrFN.ann_cast.grfn_assignment_pass import GrfnAssignmentPass
from automates.program_analysis.CAST2GrFN.ann_cast.lambda_expression_pass import LambdaExpressionPass
from automates.program_analysis.CAST2GrFN.ann_cast.to_grfn_pass import ToGrfnPass

ANN_CAST_ALL_PASSES = {
        "IdCollapsePass": IdCollapsePass, 
        "ContainerScopePass": ContainerScopePass,
        "VariableVersionPass": VariableVersionPass,
        "GrfnVarCreationPass": GrfnVarCreationPass,
        "GrfnAssignmentPass": GrfnAssignmentPass,
        "LambdaExpressionPass": LambdaExpressionPass,
        "ToGrfnPass": ToGrfnPass
        }

ANN_CAST_PASS_ORDER = [
        "IdCollapsePass",
        "ContainerScopePass",
        "VariableVersionPass",
        "GrfnVarCreationPass",
        "GrfnAssignmentPass",
        "LambdaExpressionPass",
        "ToGrfnPass"
        ]

def run_all_passes(ann_cast: AnnCast):
    """
    Runs all passes on `ann_cast`, mutating it and populating
    pass information
    """
    for pass_name in ANN_CAST_PASS_ORDER:
        print(f"Running AnnCast Pass: {pass_name}")
        print(f"{'*'*20}")
        ANN_CAST_ALL_PASSES[pass_name](ann_cast)
