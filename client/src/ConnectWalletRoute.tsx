import {useNavigate} from "react-router-dom";
import React, {useEffect} from "react";
import {Network} from "./Algod";
import {ConnectAccount} from "./ConnectAccount";
import {WalletConnectionState} from "./types";

interface Props {
    walletConnectionState: WalletConnectionState
    updateAppState: (update: (appState: WalletConnectionState) => WalletConnectionState) => void
    onConnect: () => void
}

export function ConnectWalletRoute({walletConnectionState, updateAppState, onConnect}: Props) {
    const navigate = useNavigate()

    useEffect(() => {
        if(walletConnectionState.connected) {
            navigate('/counter')
        }
    }, [navigate, walletConnectionState.connected])

    const onChangeNetwork = (network: Network) => updateAppState(st => ({...st, network}))

    return (
        <ConnectAccount network={walletConnectionState.network} onChangeNetwork={onChangeNetwork} onConnect={onConnect}/>
    )
}
