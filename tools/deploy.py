import sys
import os

from algosdk.atomic_transaction_composer import AccountTransactionSigner
from beaker.client import ApplicationClient

sys.path.append(os.getcwd())

if __name__ == "__main__":
    from tools.helpers import (
        parse_deployment_config,
        algod_client,
        view_application_url,
    )
    from contract.counter import CounterApp

    network = sys.argv[1] if len(sys.argv) == 2 else "default"

    algod_address, algod_token, pk, address = parse_deployment_config(network)
    client = algod_client(algod_address, algod_token)

    versions = client.versions()

    print(
        "Deploying application to {0}@{1} from account:{2} ...".format(
            network, client.algod_address, address
        )
    )

    app_client = ApplicationClient(client, CounterApp(), signer=AccountTransactionSigner(pk))
    app_id, app_address, tx_id = app_client.create()

    print(
        "Application deployed on application address:{0} with app_id:{1} in tx:{2}".format(
            app_address, app_id, tx_id
        )
    )

    url = view_application_url(versions["genesis_id"], app_id)
    if url is not None:
        print("View application at: {}".format(url))
