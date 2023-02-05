from FreecadParametricFEA import parametric as pfea

import numpy as np

FREECAD_PATH = "C:/Program Files/FreeCAD 0.20/bin"

fea = pfea(freecad_path=FREECAD_PATH)

fea.set_model(freecad_document="./plate.FCStd")

fea.set_variables(
    [
        {
            "object_name": "Sketch",
            "constraint_name": "HoleDiameter",
            "constraint_values": np.linspace(10, 20, 5),
        },
        {
            "object_name": "Pad",
            "constraint_name": "Length",
            "constraint_values": np.linspace(5, 10, 5),
        },
    ]
)

fea.setup_fea(fea_results_name="CCX_Results", solver_name="SolverCcxTools")

results = fea.run_parametric()

fea.plot_fea_results()
print(results)
