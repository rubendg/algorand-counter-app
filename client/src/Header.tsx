import {accountExplorer} from "./Algod";
import {Box, Button, Stack} from "@mui/material";
import React from "react";
import {WalletConnectionState} from "./types";

const formatAccount = (account: string) => {
    return account.substring(0, 6) + '...' + account.substring(account.length - 6, account.length)
}

type Props = React.PropsWithChildren<{
    appState: WalletConnectionState
    onDisconnect: () => void
}>

export function Header({ appState, onDisconnect, children }: Props) {
    let header
    if (!appState.connected || !appState.account) {
        header = <div style={{ background: '#000', height: 10 }}></div>
    } else {
        header = (
            <Box style={{ background: '#000', minHeight: 50, verticalAlign: 'middle', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', color: '#fff' }}>
                <div>Connected to <b>{appState.network}</b> with account <a href={accountExplorer(appState.network, appState.account)} style={{color:'#fff'}}>{formatAccount(appState.account)}</a> | </div>
                <div style={{padding:15}}><Button variant="contained" onClick={onDisconnect}>Disconnect</Button></div>
            </Box>
        )
    }

    return (
        <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minHeight="100vh">
            <Stack>
                <div style={{textAlign:'left', verticalAlign:'middle'}}><h1>Algorand Counter App</h1></div>
                {header}
                <Box boxShadow={3} minWidth="50vw" style={{padding:10, paddingBottom: 20}}>
                    {children}
                </Box>
            </Stack>
        </Box>
    )
}
