import importlib
import sys
import os
import json

sys.path.append(os.getcwd())

output_dir = "build"

if __name__ == "__main__":
    from contract.counter import CounterApp

    app = CounterApp()

    approval_out = "{0}/{1}_approval.teal".format(output_dir, CounterApp.__name__)
    clear_out = "{0}/{1}_clear.teal".format(output_dir, CounterApp.__name__)
    abi_out = "{0}/{1}.json".format(output_dir, CounterApp.__name__)

    with open(approval_out, "w") as h:
        h.write(app.approval_program)

    with open(clear_out, "w") as h:
        h.write(app.clear_program)

    with open(abi_out, "w") as h:
        h.write(json.dumps(app.contract.dictify(), indent=4))
