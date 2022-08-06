import sys
import os

sys.path.append(os.getcwd())

if __name__ == "__main__":
    from contract.client import Counter
    from tools.helpers import (
        parse_deployment_config,
        algod_client,
        view_application_url,
    )

    network = sys.argv[1] if len(sys.argv) == 2 else "default"

    algod_address, algod_token, pk, address = parse_deployment_config(network)
    client = algod_client(algod_address, algod_token)

    versions = client.versions()

    print(
        "Deploying application to {0}@{1} from account:{2} ...".format(
            network, client.algod_address, address
        )
    )

    contract = Counter.create(
        algod_client=client,
        client_sk=pk,
    )

    print(
        "Application deployed on application address:{0} with app_id:{1}".format(
            contract.app_address, contract.app_id
        )
    )

    url = view_application_url(versions["genesis_id"], contract.app_id)
    if url is not None:
        print("View application at: {}".format(url))
