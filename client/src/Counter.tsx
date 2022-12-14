import React, {useContext, useState} from "react";
import {Button, ButtonGroup, Stack} from "@mui/material";
import {WalletConnectContext, WalletConnectSigner} from "./walletconnect/WalletConnect";
import {
    Algodv2,
} from "algosdk";
import {CounterContract} from "./contract/CounterContract";
import {Pending, usePendingState} from "./helpers";


interface Props {
    account: string,
    client: Algodv2,
    appID: number,
    initialCount: bigint
}

export function Counter({ account, client, appID, initialCount }: Props) {
    const [count, setCounter] = useState(initialCount)
    const [pending, withPending] = usePendingState()

    const wc = useContext(WalletConnectContext)
    const signer = WalletConnectSigner(wc, account, 'Sign to increase the counter')

    const counter = new CounterContract(client, appID, account, signer)

    const increase = withPending(async () => {
        setCounter(await counter.inc())
    })

    const decrease = withPending(async () => {
        setCounter(await counter.dec())
    })

    return (
        <Pending pending={pending}>
            <Stack>
                <div style={{paddingLeft: 20, paddingRight: 20, paddingTop: 10, paddingBottom: 10, textAlign: 'center'}}><h1>Count: {count.toString(10)}</h1></div>
                <ButtonGroup variant="outlined" aria-label="text button group" style={{display: "flex", justifyContent: "center"}}>
                    <Button onClick={increase}>Increase</Button>
                    <Button onClick={decrease}>Decrease</Button>
                </ButtonGroup>
            </Stack>
        </Pending>
    )
}
