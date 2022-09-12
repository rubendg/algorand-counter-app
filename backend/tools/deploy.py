import json
import sys
import os

from algosdk.atomic_transaction_composer import AccountTransactionSigner
from beaker.client import ApplicationClient
from optparse import OptionParser
sys.path.append(os.getcwd())

parser = OptionParser()
parser.add_option("-d", "--descriptor", dest="descriptor",
                  help="read deployment descriptor from FILE", type="str", metavar="FILE", default=None)
parser.add_option("-n", "--network",
                  dest="network", default="default",
                  help="the target network")


if __name__ == "__main__":
    from tools.helpers import (
        parse_deployment_config,
        algod_client,
        view_application_url, deploy_from_descriptor,
)
    from contract.counter import CounterApp

    (options, args) = parser.parse_args()

    algod_address, algod_token, pk, address = parse_deployment_config(options.network)
    client = algod_client(algod_address, algod_token)

    versions = client.versions()

    print(
        "Deploying backend to {0}@{1} from account:{2} ...".format(
            options.network, client.algod_address, address
        )
    )

    signer = AccountTransactionSigner(pk)

    if options.descriptor:
        with open(options.descriptor, 'r') as f:
            descriptor = json.load(f)
            app_id, app_address, tx_id = deploy_from_descriptor(client, address, signer, descriptor)
    else:
        app_client = ApplicationClient(
            client, CounterApp(), signer=AccountTransactionSigner(pk)
        )
        app_id, app_address, tx_id = app_client.create()

    print(
        "Application deployed on backend address:{0} with app_id:{1} in tx:{2}".format(
            app_address, app_id, tx_id
        )
    )

    url = view_application_url(versions["genesis_id"], app_id)
    if url is not None:
        print("View backend at: {}".format(url))
