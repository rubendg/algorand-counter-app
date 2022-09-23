import {WalletConnectionState} from "./types";
import {Link, useNavigate, useParams} from "react-router-dom";
import React, {useEffect, useState} from "react";
import {applicationExplorer, clientForNetwork} from "./Algod";
import {Alert, Stack} from "@mui/material";
import {Counter} from "./Counter";
import {CounterContract} from "./contract/CounterContract";
import {Algodv2} from "algosdk";

export class UnexpectedApplication extends Error {}

export async function fetchCounterAppInfo(client: Algodv2, appID: number) {
    const { params: { creator, 'global-state': globalState, 'approval-program': approvalProgram, 'clear-state-program': clearProgram  } } = await client.getApplicationByID(appID).do()

    if (approvalProgram !== CounterContract.approvalProgram || clearProgram !== CounterContract.clearProgram) {
        throw new UnexpectedApplication()
    }

    return {appID, count: globalState[0].value.uint, creator }
}

type Props = { walletConnectionState: WalletConnectionState }

export function CounterRoute({ walletConnectionState }: Props) {
    const navigate = useNavigate()

    let { appID } = useParams();
    const parsedAppID = Number(appID || '')

    useEffect(() => {
        if(!walletConnectionState.connected || !walletConnectionState.account) {
            return navigate('/')
        }

        if(!appID) {
            return navigate('/counter')
        }
    }, [navigate, walletConnectionState, appID])

    const [error, setError] = useState<string>()
    const [appInfo, setAppInfo] = useState<any>()

    const client = clientForNetwork(walletConnectionState.network)

    useEffect(() => {
        (async function () {
            try {
                const info = await fetchCounterAppInfo(client, parsedAppID)
                setAppInfo(info)
            } catch(e: any) {
                if ('status' in e && e.status === 404) {
                    setError("Application is either deleted or does not exist")
                    return
                }

                if (e instanceof UnexpectedApplication) {
                    setError("Requested application is not a Counter application")
                    return
                }

                throw e
            }
        })()
    }, [parsedAppID, client])

    return (
        <Stack rowGap={1}>
            <div>
                <Link to={"/counter"}>Back</Link> / Application: <a href={applicationExplorer(walletConnectionState.network, parsedAppID)} target="_blank" rel="noreferrer">{appID}</a>
            </div>
            {error && <Alert severity="error" style={{marginBottom:10}}>{error}</Alert>}
            {!error && walletConnectionState.account && appInfo && <Counter account={walletConnectionState.account} client={client} appID={parsedAppID} initialCount={appInfo.count} />}
        </Stack>
    )
}