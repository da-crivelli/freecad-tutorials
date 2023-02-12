from os import path
import numpy as np
from FreecadParametricFEA import parametric as pfea


"""
A single parameter sweep on a simple 3D linkage model.
Runs a static analysis and extracts the max. Von Mises stress
and max deflection.
"""

FREECAD_PATH = "C:/Program Files/FreeCAD 0.20/bin"

# initialise the parametric FEA object
fea = pfea(freecad_path=FREECAD_PATH)
# set a path to the FreeCAD model
script_path = path.dirname(path.realpath(__file__))
fea.set_model("notch-effect.fcstd")
# list the parameters to sweep
fea.set_variables(
    [
        {
            "object_name": "NotchSketch",
            "constraint_name": "NotchSpacing",
            "constraint_values": np.linspace(4, 15, 8),
        },
        {
            "object_name": "NotchSketch",
            "constraint_name": "NotchDepth",
            "constraint_values": np.linspace(2, 6, 8),
        },
    ]
)

fea.set_outputs(
    [
        {
            "output_var": "vonMises",
            "reduction_fun": np.max,
        },
    ]
)

# setup the FEA
fea.setup_fea(fea_results_name="CCX_Results", solver_name="SolverCcxTools")
# results = fea.run_parametric(dry_run=True)
results = fea.run_parametric()

fea.plot_fea_results()


print(results)
