# runs a FEA model in Freecad based on a parameter sweep,
# and presents the results to the user.

import sys, time

FREECADPATH = "C:\\Program Files\\FreeCAD 0.20\\bin"
sys.path.append(FREECADPATH)

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

pd.options.plotting.backend = "plotly"

import FreeCAD
from femtools import ccxtools

# settings
filename = "fea-parametric\\FEA_Parametric.fcstd"
object_name = "Pocket"
constraint_name = "Spacing"
constraint_units = "mm"
fea_results_name = "CCX_Results"
solver_name = "SolverCcxTools"

# range of the parameter values to sweep (passed directly to np.arange)
(param_min, param_max, param_step) = (15, 30, 2)


def main(filename):

    results_df = pd.DataFrame()
    # results_df = pd.DataFrame(
    #     columns=["Target_Value", "vonMises_Max", "displacement_Max"]
    # )

    doc = FreeCAD.open(filename)

    # loop over the parameter
    for target_length in np.arange(param_min, param_max, param_step):
        # change the target parameter in the CAD model
        freecad_change_param(
            freecad_document=doc,
            object_name=object_name,
            constraint_name=constraint_name,
            target_value=target_length,
        )

        # run (& time) the FEA
        start_time = time.process_time()
        fea_results_obj = freecad_run_fea(
            freecad_document=doc,
            solver_name=solver_name,
            fea_results_name=fea_results_name,
        )
        fea_runtime = time.process_time() - start_time

        # adding results to a Pandas dataframe
        results_df = pd.concat(
            [
                results_df,
                pd.DataFrame(
                    {
                        "Target_Value": target_length,
                        "vonMises_Max": max(fea_results_obj.vonMises),
                        "displacement_Max": max(fea_results_obj.DisplacementLengths),
                        "FEA_runtime": fea_runtime,
                    },
                    index=[target_length],
                ),
            ]
        )

    # plot the results

    plot_fea_results(results_dataframe=results_df)
    print(results_df)


def plot_fea_results(results_dataframe):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=results_dataframe["Target_Value"],
            y=results_dataframe["vonMises_Max"],
            name="Max. Von Mises (MPa)",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=results_dataframe["Target_Value"],
            y=results_dataframe["displacement_Max"],
            name="Max. displacement (mm)",
        ),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(title_text="FreeCAD optimisation on {}".format(filename))

    # Set x-axis title
    fig.update_xaxes(title_text="{} ({})".format(constraint_name, constraint_units))

    # Set y-axes titles
    fig.update_yaxes(title_text="Max. Von Mises (MPa)", secondary_y=False)
    fig.update_yaxes(title_text="Max. displacement (mm)", secondary_y=True)

    fig.show()


def freecad_run_fea(freecad_document, solver_name: str, fea_results_name: str):
    """runs a FEA analysis in the specified freecad document

    Args:
        freecad_document: freecad document object (as obtained with FreeCAD.open())
        solver_name (str): name of the solver (e.g. SolverCcxTools)
        fea_results_name (str): name of the FEA results container (e.g. CCX_Results)

    Returns:
        fea object: a FreeCAD object containing the FEA results
    """
    solver_object = freecad_document.getObject(solver_name)

    fea = ccxtools.FemToolsCcx(solver=solver_object)
    fea.purge_results()
    fea.reset_all()
    fea.update_objects()

    # there should be some error handling here
    fea.check_prerequisites()
    fea.run()

    fea_results_obj = freecad_document.getObject(fea_results_name)
    return fea_results_obj


def freecad_change_param(
    freecad_document, object_name: str, constraint_name: str, target_value: float
):
    """changes a parameter (e.g. a named constraint) inside a freecad document.
    Currently works if the constraint is inside the driving sketch of the
    referenced object (e.g. a pocket)

    Args:
        freecad_document: freecad document object (as obtained with FreeCAD.open())
        object_name (str): name of the Freecad object containing the sketch containing the constraint
        constraint_name (str): name of the constraint to modify
        target_value (float): target value for the constraint
    """
    target_sketch = freecad_document.getObject(object_name).Profile[0]

    # loop over constraints to find the target
    edge_idx = None
    for (edge_idx, constraint) in enumerate(target_sketch.Constraints):
        if constraint.Name == constraint_name:
            break

    # set the datum to the desired value
    target_sketch.setDatum(edge_idx, target_value)

    # apply changes and recompute
    freecad_document.recompute()


if __name__ == "__main__":
    main(filename)
