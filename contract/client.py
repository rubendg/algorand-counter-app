import base64

import algosdk.abi
from typing import Tuple

from algosdk.abi import Contract
from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
)


class Counter:
    @classmethod
    def _contract(cls):
        with open("build/contract.counter.json", "r") as h:
            return algosdk.abi.Contract.from_json(h.read())

    @classmethod
    def _approval_program_teal(cls):
        with open("build/contract.counter_approval.teal", "r") as h:
            return h.read()

    @classmethod
    def _clear_program_teal(cls):
        with open("build/contract.counter_clear.teal", "r") as h:
            return h.read()

    @classmethod
    def instance(
        cls,
        algod_client: AlgodClient,
        app_id: int,
        client_sk: str,
        client_address: str = None,
    ):
        return Counter(
            algod_client=algod_client,
            contract=cls._contract(),
            app_address=algosdk.logic.get_application_address(app_id),
            app_id=app_id,
            client_address=client_address,
            client_sk=client_sk,
        )

    @classmethod
    def create(
        cls,
        algod_client: AlgodClient,
        client_sk: str,
        client_address: str = None,
        start: int = 0,
    ) -> "Counter":
        if client_address is None:
            client_address = algosdk.account.address_from_private_key(client_sk)

        contract = Counter._contract()

        approval_program = compile_teal(algod_client, cls._approval_program_teal())
        clear_program = compile_teal(algod_client, cls._clear_program_teal())

        params = algod_client.suggested_params()
        txn = transaction.ApplicationCreateTxn(
            sender=client_address,
            sp=params,
            on_complete=transaction.OnComplete.NoOpOC,
            # ATM the PyTeal Router does not accept application creation with arguments
            # see https://github.com/algorand/pyteal/blob/master/pyteal/ast/router.py#L536
            # app_args=[start],
            approval_program=approval_program,
            clear_program=clear_program,
            global_schema=transaction.StateSchema(num_uints=int(1)),
            local_schema=transaction.StateSchema(),
        )
        signed_txn = txn.sign(client_sk)
        tx_id = signed_txn.transaction.get_txid()

        algod_client.send_transactions([signed_txn])

        transaction.wait_for_confirmation(algod_client, tx_id, 2)

        transaction_response = algod_client.pending_transaction_info(tx_id)
        app_id = transaction_response["application-index"]

        return Counter(
            algod_client=algod_client,
            contract=contract,
            app_address=algosdk.logic.get_application_address(app_id),
            app_id=app_id,
            client_address=client_address,
            client_sk=client_sk,
        )

    def __init__(
        self,
        algod_client: AlgodClient,
        contract: Contract,
        app_id: int,
        app_address: str,
        client_sk: str,
        client_address: str = None,
    ):
        if client_address is None:
            client_address = algosdk.account.address_from_private_key(client_sk)

        self.algod_client = algod_client
        self.app_id = app_id
        self.app_address = app_address
        self.client_sk = client_sk
        self.client_address = client_address
        self.inc_method = contract.get_method_by_name("inc")
        self.dec_method = contract.get_method_by_name("dec")

    def _call(self, caller, caller_sk, method, method_args=None):
        caller, caller_sk = self._caller_default(caller, caller_sk)
        signer = AccountTransactionSigner(caller_sk)

        if method_args is None:
            method_args = []
        sp = self.algod_client.suggested_params()
        comp = AtomicTransactionComposer()
        comp.add_method_call(
            app_id=self.app_id,
            method=method,
            sender=caller,
            sp=sp,
            signer=signer,
            method_args=method_args,
        )
        response = comp.execute(self.algod_client, wait_rounds=2)

        return_values = [
            result.return_value
            for result in response.abi_results
            if result.method.name == method.name
        ]

        if len(return_values) != 1:
            raise Exception(
                "failed to call {0}.{1} no value returned".format(
                    self.__class__.__name__, method.name
                )
            )

        return return_values[0]

    def _caller_default(self, caller=None, caller_sk=None) -> Tuple[str, str]:
        caller = self.client_address if caller is None else caller
        caller_sk = self.client_sk if caller_sk is None else caller_sk
        return caller, caller_sk

    def dec(self, caller=None, caller_sk=None):
        return self._call(caller=caller, caller_sk=caller_sk, method=self.dec_method)

    def inc(self, caller=None, caller_sk=None):
        return self._call(caller=caller, caller_sk=caller_sk, method=self.inc_method)

    def global_state(self):
        app_info = self.algod_client.application_info(application_id=self.app_id)
        return teal_kv_store_to_dict(app_info["params"]["global-state"])

    def delete(self, caller=None, caller_sk=None):
        caller, caller_sk = self._caller_default(caller, caller_sk)
        sp = self.algod_client.suggested_params()
        tx = transaction.ApplicationDeleteTxn(sender=caller, sp=sp, index=self.app_id)
        signed_tx = tx.sign(caller_sk)
        tx_id = self.algod_client.send_transaction(signed_tx)
        return tx_id, transaction.wait_for_confirmation(self.algod_client, tx_id, 2)

    def update(
        self, approval_program: bytes, clear_program: bytes, caller=None, caller_sk=None
    ):
        caller, caller_sk = self._caller_default(caller, caller_sk)
        sp = self.algod_client.suggested_params()
        tx = transaction.ApplicationUpdateTxn(
            sender=caller,
            sp=sp,
            index=self.app_id,
            approval_program=approval_program,
            clear_program=clear_program,
        )
        signed_tx = tx.sign(caller_sk)
        tx_id = self.algod_client.send_transaction(signed_tx)
        return tx_id, transaction.wait_for_confirmation(self.algod_client, tx_id, 2)


def compile_teal(algod_client: AlgodClient, teal: str) -> bytes:
    compile_response = algod_client.compile(teal)
    return base64.b64decode(compile_response["result"])


def teal_kv_store_to_dict(teal_kv_store) -> dict:
    """
    Maps the TealKekValueStore structure to a more convenient python representation

    See https://developer.algorand.org/docs/rest-apis/algod/v2/#tealkeyvaluestore

    :param teal_kv_store:
    :return: dict
    """
    mapping = dict()
    for item in teal_kv_store:
        value = item["value"]
        match value["type"]:
            case 1:
                v = base64.b64decode(value["bytes"])
            case 2:
                v = value.get("uint", 0)
            case _:
                raise Exception(
                    "unknown type found in teal kv store: {0}".format(value["type"])
                )
        k = base64.b64decode(item["key"]).decode("ascii")
        mapping[k] = v
    return mapping
