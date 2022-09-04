import React, {useContext, useState} from "react";
import {Backdrop, Button, ButtonGroup, CircularProgress, Stack} from "@mui/material";
import {WalletConnectContext, WalletConnectSigner} from "./walletconnect/WalletConnect";
import {
    Algodv2,
} from "algosdk";
import {CounterContract} from "./CounterContract";

function usePendingState(): [boolean, (f: () => Promise<void>) => (() => Promise<void>)] {
    const [pending, setPending] = useState(false)

    const withPending = (f: () => Promise<void>) => {
        return async () => {
            setPending(true)
            try {
                return await f()
            } catch (e) {
                throw e
            } finally {
                setPending(false)
            }
        }
    }

    return [pending, withPending]
}

interface Props {
    account: string,
    client: Algodv2,
    appID: number,
    initialCount: bigint,
    creator: string
}

export function Counter({ account, client, appID, initialCount, creator }: Props) {
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

    const del = async () => {
        // todo
        // const sp = await client.getTransactionParams().do()
        // const tx = makeApplicationDeleteTxn(account, sp, appID)
    }

    return (
        <Stack direction="row">
            <Backdrop
                sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
                open={pending}>
                <CircularProgress color="inherit" />
            </Backdrop>
            <ButtonGroup variant="outlined" aria-label="text button group">
                <div style={{paddingLeft: 20, paddingRight: 20, paddingTop: 10, paddingBottom: 10, textAlign: 'center'}}>Count: {count.toString(10)}</div>
                <Button onClick={increase}>Increase</Button>
                <Button onClick={decrease}>Decrease</Button>
                <Button onClick={del} disabled={creator !== account}>Delete</Button>
            </ButtonGroup>
        </Stack>
    )
}
