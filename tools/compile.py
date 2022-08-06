import importlib
import sys
import os
import json
from pyteal import OptimizeOptions

sys.path.append(os.getcwd())

output_dir = "build"

if __name__ == "__main__":
    mod = sys.argv[1]

    p = importlib.import_module(mod)

    approval_program, clear_state_program, contract = p.router.compile_program(
        version=6, optimize=OptimizeOptions(scratch_slots=True)
    )

    approval_out = "{0}/{1}_approval.teal".format(output_dir, mod)
    clear_out = "{0}/{1}_clear.teal".format(output_dir, mod)
    abi_out = "{0}/{1}.json".format(output_dir, mod)

    with open(approval_out, "w") as h:
        h.write(approval_program)

    with open(clear_out, "w") as h:
        h.write(clear_state_program)

    with open(abi_out, "w") as h:
        h.write(json.dumps(contract.dictify(), indent=4))
