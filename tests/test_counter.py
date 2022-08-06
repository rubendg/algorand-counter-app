from contract.client import Counter, compile_teal
from helpers import (
    call_sandbox_command,
    create_test_account,
)
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algosdk.error import AlgodHTTPError

sandbox_dev_token = "a" * 64


def setup_module(module):
    """Ensure Algorand Sandbox is up prior to running tests from this module."""
    call_sandbox_command("up", "dev")


class TestCounter:
    algod_address = "http://localhost:4001"
    algod_token = sandbox_dev_token
    algod_client = AlgodClient(algod_token, algod_address)

    indexer_address = "http://localhost:8980"
    indexer_token = sandbox_dev_token
    indexer_client = IndexerClient(indexer_token, indexer_address)

    def _setup_counter(self, start: int = 0):
        self.private_key, self.address = create_test_account(
            self.algod_client, self.indexer_client
        )

        self.contract = Counter.create(
            algod_client=self.algod_client, client_sk=self.private_key, start=start
        )

    def test_starts_at_zero(self):
        self._setup_counter()

        global_state = self.contract.global_state()

        assert len(global_state) == 1
        assert "counter" in global_state
        assert global_state["counter"] == 0

    def test_inc(self):
        self._setup_counter()

        result = self.contract.inc()

        assert result == 1
        global_state = self.contract.global_state()
        assert global_state["counter"] == 1

    def test_anyone_can_inc(self):
        self._setup_counter()

        private_key, address = create_test_account(
            self.algod_client, self.indexer_client
        )
        result = self.contract.inc(caller=address, caller_sk=private_key)

        assert result == 1
        global_state = self.contract.global_state()
        assert global_state["counter"] == 1

    def test_anyone_can_dec(self):
        self._setup_counter()

        self.contract.inc()

        private_key, address = create_test_account(
            self.algod_client, self.indexer_client
        )
        result = self.contract.dec(caller=address, caller_sk=private_key)

        assert result == 0
        global_state = self.contract.global_state()
        assert global_state["counter"] == 0

    def test_creator_can_delete(self):
        self._setup_counter()

        self.contract.delete()
        try:
            self.contract.global_state()
            raise Exception("failed to delete application")
        except AlgodHTTPError as e:
            assert e.code == 404

    def test_others_cannot_delete(self):
        self._setup_counter()

        private_key, address = create_test_account(
            self.algod_client, self.indexer_client
        )
        try:
            self.contract.delete(caller=address, caller_sk=private_key)
            raise Exception("others should not be allowed to remove the application")
        except AlgodHTTPError as e:
            assert e.code == 400
            assert e.args[0].endswith("transaction rejected by ApprovalProgram")

    def test_creator_cannot_update(self):
        self._setup_counter()

        always_succeed_program = compile_teal(
            self.algod_client,
            """#pragma version 6
int 0
return""",
        )
        try:
            self.contract.update(always_succeed_program, always_succeed_program)
            raise Exception("application cannot be updated")
        except AlgodHTTPError as e:
            assert e.code == 400
            assert e.args[0].endswith("transaction rejected by ApprovalProgram")

    def test_underflow(self):
        self._setup_counter()

        result = self.contract.dec()
        assert result == 0

    def test_overflow(self):
        # Enable once PyTeal Router supports app creation with arguments
        #
        # uint64_max = 0xFFFFFFFFFFFFFFFF
        # self._setup_counter(start=uint64_max)
        #
        # self.contract.inc()
        pass

    def test_inc_and_dec(self):
        self._setup_counter()

        result = self.contract.inc()

        assert result == 1
        global_state = self.contract.global_state()
        assert global_state["counter"] == 1

        result = self.contract.dec()

        assert result == 0
        global_state = self.contract.global_state()
        assert global_state["counter"] == 0
