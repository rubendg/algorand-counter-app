import sys
import os

sys.path.append(os.getcwd())

if __name__ == "__main__":
    from tools.helpers import parse_deployment_config, algod_client, view_tx_url
    from contract.client import Counter

    if len(sys.argv) < 2:
        raise Exception("Missing app_id")
    [app_id_str, network] = (
        sys.argv[1],
        sys.argv[2] if len(sys.argv) == 3 else "default",
    )

    app_id = int(app_id_str)

    algod_address, algod_token, pk, address = parse_deployment_config(network)
    client = algod_client(algod_address, algod_token)

    versions = client.versions()

    print(
        "Removing application:{0} at {1}@{2} using account:{3} ...".format(
            app_id, network, client.algod_address, address
        )
    )

    tx_id, tx_info = Counter.instance(
        algod_client=client, app_id=app_id, client_sk=pk
    ).delete()

    print("Removed application in tx_id:{0}".format(tx_id))

    url = view_tx_url(versions["genesis_id"], tx_id)
    if url is not None:
        print("View transaction at: {}".format(url))
