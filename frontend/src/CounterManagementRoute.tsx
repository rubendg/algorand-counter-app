import {useNavigate} from "react-router-dom";
import React, {useContext, useEffect} from "react";
import {CounterSelection} from "./CounterSelection";
import {WalletConnectionState} from "./types";
import {Button, Stack} from "@mui/material";
import {CounterContract} from "./CounterContract";
import {WalletConnectContext, WalletConnectSigner} from "./walletconnect/WalletConnect";
import {clientForNetwork} from "./Algod";
import {Pending, usePendingState} from "./helpers";

interface Props {
    walletConnectionState: WalletConnectionState
}

export function CounterManagementRoute({walletConnectionState}: Props) {
    const navigate = useNavigate()
    const wc = useContext(WalletConnectContext)
    const [pending, withPending] = usePendingState()

    useEffect(() => {
        if(!walletConnectionState.connected) {
            navigate('/')
        }
    }, [navigate, walletConnectionState.connected])

    const gotoAppID = (appID: number) => {
        navigate('/counter/'+appID)
    }

    const create = withPending(async () => {
        const signer = WalletConnectSigner(wc, walletConnectionState.account!, 'Create new counter')
        const appID = await CounterContract.create(clientForNetwork(walletConnectionState.network), walletConnectionState.account!, signer)
        gotoAppID(appID)
    })

    return <Pending pending={pending}>
        <Stack rowGap={1}>
            <Button variant="outlined" onClick={create}>Create New</Button>
            <span>Or find existing application:</span>
            <CounterSelection onCounterSelected={gotoAppID}/>
        </Stack>
    </Pending>
}
