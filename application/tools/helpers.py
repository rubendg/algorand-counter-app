import base64
import configparser

import algosdk
from algosdk.atomic_transaction_composer import AtomicTransactionComposer, TransactionWithSigner, TransactionSigner
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from algosdk.logic import get_application_address

ALGOEXPLORER_TESTNET_ENDPOINT = "https://testnet.algoexplorer.io"
ALGOEXPLORER_BETANET_ENDPOINT = "https://betanet.algoexplorer.io"
ALGOEXPLORER_MAINNET_ENDPOINT = "https://algoexplorer.io"


def algoexplorer_base_url(genesis_id):
    if genesis_id.startswith("testnet-"):
        return ALGOEXPLORER_TESTNET_ENDPOINT
    elif genesis_id.startswith("betanet-"):
        return ALGOEXPLORER_BETANET_ENDPOINT
    elif genesis_id.startswith("mainnet-"):
        return ALGOEXPLORER_MAINNET_ENDPOINT
    return None


def view_tx_url(genesis_id, id) -> str | None:
    base_url = algoexplorer_base_url(genesis_id)
    if base_url:
        return "{0}/tx/{1}".format(base_url, id)
    return None


def view_application_url(genesis_id, id) -> str | None:
    base_url = algoexplorer_base_url(genesis_id)
    if base_url:
        return "{0}/application/{1}".format(base_url, id)
    return None


def parse_deployment_config(network, deployment_config="deploy.ini"):
    config = configparser.ConfigParser()
    config.read(deployment_config)

    sender_mnemonic = config.get(network, "sender_mnemonic", raw=True)
    if sender_mnemonic is None:
        raise Exception(
            "Please set 'sender_mnemonic' to the Algorand account that creates the "
            "smart application."
        )

    algod_address = config.get(network, "algod_address")
    if algod_address is None:
        raise Exception("Please set 'algod_address'")

    algod_token = config.get(network, "algod_client_token", fallback="")

    pk = algosdk.mnemonic.to_private_key(sender_mnemonic)
    address = algosdk.account.address_from_private_key(pk)

    return algod_address, algod_token, pk, address


def algod_client(algod_address, algod_token):
    headers = None
    # Patch the authentication header only in the case of purestake.io
    if algod_address.find("purestake.io") != -1:
        headers = {"X-API-Key": algod_token}
    return AlgodClient(algod_token, algod_address, headers)


def deploy_from_descriptor(client: AlgodClient, creator: str, signer: TransactionSigner, descriptor):
    sp = client.suggested_params()

    resp = client.compile(descriptor['teal']['approval'])
    approval = base64.b64decode(resp["result"])

    resp = client.compile(descriptor['teal']['clear'])
    clear = base64.b64decode(resp["result"])

    atc = AtomicTransactionComposer()
    atc.add_transaction(
        TransactionWithSigner(
            txn=transaction.ApplicationCreateTxn(
                sender=creator,
                sp=sp,
                on_complete=transaction.OnComplete.NoOpOC,
                approval_program=approval,
                clear_program=clear,
                global_schema=transaction.StateSchema(num_uints=descriptor['state']['global']['uints'],
                                                      num_byte_slices=descriptor['state']['global']['byte_slices']),
                local_schema=transaction.StateSchema(num_uints=descriptor['state']['local']['uints'],
                                                     num_byte_slices=descriptor['state']['local']['byte_slices']),
                extra_pages=None,
                app_args=[],
            ),
            signer=signer,
        )
    )

    create_result = atc.execute(client, 4)

    create_txid = create_result.tx_ids[0]

    result = client.pending_transaction_info(create_txid)
    app_id = result["application-index"]
    app_addr = get_application_address(app_id)

    return app_id, app_addr, create_txid
