import os
import pty
import subprocess
from pathlib import Path

from algosdk import account, mnemonic
from algosdk.future.transaction import PaymentTxn
from typing import Tuple

from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algosdk.future import transaction


def _sandbox_directory():
    """Return full path to Algorand's sandbox executable.
    The location of sandbox directory is retrieved either from the SANDBOX_DIR
    environment variable or if it's not set then the location of sandbox directory
    is implied to be the sibling of this Django project in the directory tree.
    """
    return os.environ.get("SANDBOX_DIR") or str(
        Path(__file__).resolve().parent.parent.parent / "algorand-sandbox"
    )


def _sandbox_executable():
    """Return full path to Algorand's sandbox executable."""
    return _sandbox_directory() + "/sandbox"


def call_sandbox_command(*args):
    """Call and return sandbox command composed from provided arguments."""
    return subprocess.run(
        [_sandbox_executable(), *args], stdin=pty.openpty()[1], capture_output=True
    )


def create_test_account(
    algod_client: AlgodClient, indexer_client: IndexerClient, amount: int = 10**6
) -> Tuple[str, str]:
    test_private_key, test_address = account.generate_account()

    def _initial_funds_address():
        """Get the address of initially created account having enough funds.
        Such an account is used to transfer initial funds for the accounts
        created in this tutorial.
        """
        accounts = indexer_client.accounts().get("accounts")
        return next(
            (
                a.get("address")
                for a in accounts
                if a.get("created-at-round") == 0
                and a.get("status") == "Online"  # "Online" for devMode
            ),
            None,
        )

    def _export_passphrase(address: str) -> str:
        process = call_sandbox_command("goal", "account", "export", "-a", address)
        if process.stderr:
            raise RuntimeError(process.stderr.decode("utf8"))

        passphrase = ""
        parts = process.stdout.decode("utf8").split('"')
        if len(parts) > 1:
            passphrase = parts[1]
        if passphrase == "":
            raise ValueError(
                "Can't retrieve passphrase from the address: %s\nOutput: %s"
                % (address, process.stdout.decode("utf8"))
            )
        return passphrase

    def _fund(from_address, to_address, signing_key):
        params = algod_client.suggested_params()
        unsigned_txn = PaymentTxn(
            sender=from_address, sp=params, receiver=to_address, amt=amount
        )
        signed_txn = unsigned_txn.sign(signing_key)
        tx_id = algod_client.send_transaction(signed_txn)

        transaction.wait_for_confirmation(algod_client, tx_id, 4)

    funding_address = _initial_funds_address()
    if funding_address is None:
        raise Exception(
            "Failed to find an address that can be used to fund the test account"
        )

    funding_address_passphrase = _export_passphrase(funding_address)
    funding_signing_key = mnemonic.to_private_key(funding_address_passphrase)

    _fund(
        from_address=funding_address,
        to_address=test_address,
        signing_key=funding_signing_key,
    )

    return test_private_key, test_address
