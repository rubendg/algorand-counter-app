import {useNavigate} from "react-router-dom";
import React, {useEffect} from "react";
import {CounterSelection} from "./CounterSelection";
import {WalletConnectionState} from "./types";

interface Props {
    walletConnectionState: WalletConnectionState
}

export function CounterManagementRoute({walletConnectionState}: Props) {
    const navigate = useNavigate()

    useEffect(() => {
        if(!walletConnectionState.connected) {
            navigate('/')
        }
    }, [navigate, walletConnectionState.connected])

    const onCounterSelected = (appID: number) => {
        navigate('/counter/'+appID)
    }

    return (
        <CounterSelection onCounterSelected={onCounterSelected}/>
    )
}
