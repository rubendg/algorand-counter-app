from pyteal import (
    Expr,
    Router,
    Return,
    Global,
    Txn,
    BareCallActions,
    OnCompleteAction,
    Approve,
    Seq,
    Int,
    Reject,
    abi,
    ScratchVar,
    If,
    TealType,
)

from contract.helper import global_bindings

scratch_count = ScratchVar(TealType.uint64)

is_creator: Expr = Txn.sender() == Global.creator_address()

counter = global_bindings["counter"]  # uint64

on_create: Expr = Seq(counter.set(Int(0)), Approve())

router = Router(
    name="counter-app",
    descr="count by increments or decrements of 1",
    bare_calls=BareCallActions(
        no_op=OnCompleteAction.create_only(on_create),
        update_application=OnCompleteAction.always(Reject()),
        delete_application=OnCompleteAction.always(Return(is_creator)),
        clear_state=OnCompleteAction.never(),
    ),
)


@router.method(description="increment the counter")
def inc(*, output: abi.Uint64) -> Expr:
    return Seq(
        scratch_count.store(counter.get()),
        counter.set(scratch_count.load() + Int(1)),
        output.set(counter.get()),
    )


@router.method(description="decrement the counter")
def dec(*, output: abi.Uint64) -> Expr:
    return Seq(
        scratch_count.store(counter.get()),
        If(
            cond=scratch_count.load() > Int(0),
            thenBranch=counter.set(scratch_count.load() - Int(1)),
        ),
        output.set(counter.get()),
    )
