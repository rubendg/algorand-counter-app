import sys
import os
import json

sys.path.append(os.getcwd())

output_dir = "build"

if __name__ == "__main__":
    from contract.counter import CounterApp

    app = CounterApp()

    approval_out = "{0}/approval.teal".format(output_dir)
    clear_out = "{0}/clear.teal".format(output_dir)
    abi_out = "{0}/abi.json".format(output_dir)
    deployment_descriptor_out = "{0}/deployment.json".format(output_dir)

    deployment_descriptor = {
        "teal": {
            "approval": app.approval_program,
            "clear": app.clear_program,
        },
        "state": {
            "global": {
                "uints": app.app_state.schema().num_uints,
                "byte_slices": app.app_state.schema().num_byte_slices,
            },
            "local": {
                "uints": app.acct_state.schema().num_uints,
                "byte_slices": app.acct_state.schema().num_byte_slices,
            },
        },
        "abi": app.contract.dictify(),
    }

    with open(approval_out, "w") as h:
        h.write(str(app.approval_program))

    with open(clear_out, "w") as h:
        h.write(str(app.clear_program))

    with open(abi_out, "w") as h:
        h.write(json.dumps(app.contract.dictify(), indent=4))

    with open(deployment_descriptor_out, "w") as h:
        h.write(json.dumps(deployment_descriptor, indent=4))
