from beaker import sandbox, Application
from beaker.client import ApplicationClient, LogicException

from algosdk.error import AlgodHTTPError

from contract.counter import CounterApp
from tests.helpers import call_sandbox_command

sandbox_dev_token = "a" * 64


def setup_module(module):
    """Ensure Algorand Sandbox is up prior to running tests from this module."""
    call_sandbox_command("up", "dev")


class NoopApp(Application):
    pass


class TestCounter:

    algod_client = sandbox.get_algod_client()
    accounts = sandbox.get_accounts()
    creator = accounts.pop()
    other = accounts.pop()

    def _setup_counter(self):
        client = ApplicationClient(self.algod_client, CounterApp(), signer=self.creator.signer)
        return client, client.create()

    def test_starts_at_zero(self):
        client, _ = self._setup_counter()

        st = client.get_application_state()

        assert len(st) == 1
        assert "counter" in st
        assert st["counter"] == 0

    def test_inc(self):
        client, _ = self._setup_counter()

        result = client.call(CounterApp.inc)

        assert result.return_value == 1
        st = client.get_application_state()
        assert st["counter"] == 1

        result = client.call(CounterApp.inc)

        assert result.return_value == 2
        st = client.get_application_state()
        assert st["counter"] == 2

    def test_anyone_can_inc(self):
        client, _ = self._setup_counter()

        result = client.call(CounterApp.inc, sender=self.other.address, signer=self.other.signer)

        assert result.return_value == 1
        st = client.get_application_state()
        assert st["counter"] == 1

    def test_anyone_can_dec(self):
        client, _ = self._setup_counter()

        client.call(CounterApp.inc)

        result = client.call(CounterApp.dec, sender=self.other.address, signer=self.other.signer)

        assert result.return_value == 0
        st = client.get_application_state()
        assert st["counter"] == 0

    def test_creator_can_delete(self):
        client, _ = self._setup_counter()

        client.delete()
        try:
            client.get_application_state()
            raise Exception("failed to delete application")
        except AlgodHTTPError as e:
            assert e.code == 404

    def test_others_cannot_delete(self):
        client, _ = self._setup_counter()
        try:
            client.delete(sender=self.other.address, signer=self.other.signer)
            raise Exception("others should not be allowed to remove the application")
        except LogicException:
            pass

    def test_creator_can_update(self):
        [_, [app_id, _, _]] = client, _ = self._setup_counter()
        client = ApplicationClient(self.algod_client, NoopApp(), app_id=app_id, signer=self.creator.signer)
        client.update()

    def test_others_cannot_update(self):
        [_, [app_id, _, _]] = client, _ = self._setup_counter()
        client = ApplicationClient(self.algod_client, NoopApp(), app_id=app_id, signer=self.creator.signer)

        try:
            client.update(sender=self.other.address, signer=self.other.signer)
            raise Exception("application cannot be updated")
        except LogicException:
            pass

    def test_underflow(self):
        client, _ = self._setup_counter()

        result = client.call(CounterApp.dec)
        assert result.return_value == 0

    def test_overflow(self):
        # Enable once PyTeal Router supports app creation with arguments
        # uint64_max = 0xFFFFFFFFFFFFFFFF
        # client, _ = self._setup_counter(start=uint64_max)
        #
        # st = client.get_application_state()
        # assert st["counter"] == uint64_max
        #
        # result = client.call(CounterApp.inc)
        #
        # assert result.return_value == uint64_max
        pass

    def test_inc_and_dec(self):
        client, _ = self._setup_counter()

        result = client.call(CounterApp.inc)

        assert result.return_value == 1
        st = client.get_application_state()
        assert st["counter"] == 1

        result = client.call(CounterApp.dec)

        assert result.return_value == 0
        st = client.get_application_state()
        assert st["counter"] == 0
