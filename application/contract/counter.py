from typing import Final

from pyteal import Expr, Seq, Int, abi, If, TealType, Global, Approve
from beaker import (
    Application,
    external,
    ApplicationStateValue,
    create,
    delete,
    Authorize,
    update,
)

uint64_max = 0xFFFFFFFFFFFFFFFF


class CounterApp(Application):
    """A counter for everyone"""

    counter: Final[ApplicationStateValue] = ApplicationStateValue(
        stack_type=TealType.uint64,
        descr="A counter",
    )

    def __init__(self):
        super().__init__(version=6)

    @create
    def create(self):
        return self.initialize_application_state()

    @delete(authorize=Authorize.only(Global.creator_address()))
    def delete(self):
        return Approve()

    @update(authorize=Authorize.only(Global.creator_address()))
    def update(self):
        return Approve()

    @external
    def inc(self, *, output: abi.Uint64) -> Expr:
        """increment the counter"""
        return Seq(
            If(self.counter < Int(uint64_max), self.counter.set(self.counter + Int(1))),
            output.set(self.counter),
        )

    @external
    def dec(self, *, output: abi.Uint64) -> Expr:
        """decrement the counter"""
        return Seq(
            If(
                self.counter > Int(0),
                self.counter.set(self.counter - Int(1)),
            ),
            output.set(self.counter),
        )
