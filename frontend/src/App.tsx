import React, {Dispatch, SetStateAction, useContext, useEffect, useState,} from 'react';
import './App.css';
import QRCodeModal from "algorand-walletconnect-qrcode-modal";
import {WalletConnectContext} from "./walletconnect/WalletConnect";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import {Header} from "./Header";
import {ConnectWalletRoute} from "./ConnectWalletRoute";
import {CounterManagementRoute} from "./CounterManagementRoute";
import {WalletConnectionState} from "./types";
import {CounterRoute} from "./CounterRoute";
import {Network} from "./Algod";

export function setNetwork(network: Network) {
    localStorage.setItem('network', network)
}

export function getNetwork(): Network {
    return localStorage.getItem('network') as Network || Network.MainNet
}

function useWalletConnectionState(): [WalletConnectionState, Dispatch<SetStateAction<WalletConnectionState>>] {
    const connector = useContext(WalletConnectContext)

    const [walletConnectionState, setWalletConnectionState] = useState<WalletConnectionState>({
        network: getNetwork(),
        account: (connector.accounts && connector.accounts[0]) || null,
        connected: connector.connected
    })

    // persist network preference, because it cannot be derived from wallet connection: https://github.com/perawallet/pera-wallet/issues/93
    setNetwork(walletConnectionState.network)

    return [walletConnectionState, setWalletConnectionState]
}

function App() {
    const connector = useContext(WalletConnectContext)
    const [walletConnectionState, setWalletConnectionState] = useWalletConnectionState()

    useEffect(() => {
        if (connector.connected) {
            console.log('closing')
            QRCodeModal.close()
        }

        console.log('subscribe to wc events')
        if (connector.pending && !connector.connected) {
            connector.transportClose()
        }

        connector.on('connect', (error, payload) => {
            console.log('connect', error, payload)
            if(error) {
                throw error
            }

            setWalletConnectionState(st => ({...st, connected:true, account: connector.accounts[0]}))
        })

        connector.on('session_update', (error, payload) => {
            console.log('session_update', error, payload)
            if(error) {
                throw error
            }
            setWalletConnectionState(st => ({...st, connected:true, account: connector.accounts[0]}))
        })

        connector.on('disconnect', (error, payload) => {
            console.log('disconnect', error, payload)
            if(error) {
                throw error
            }
            setWalletConnectionState(st => ({...st, connected:false, account: null}))
        })

        return () => {
            console.log('unsubscribe to wc events')
            connector.off('connect')
            connector.off('session_update')
            connector.off('disconnect')
        }
    }, [connector, setWalletConnectionState, walletConnectionState])

    const connect = async () => {
        if (connector.connected) return
        if (connector.pending) return QRCodeModal.open(connector.uri, null)
        await connector.createSession()
    }

    const disconnect = async () => {
        if (!connector.connected) return;
        await connector.killSession()
    }

    return (
        <WalletConnectContext.Provider value={connector}>
            <BrowserRouter>
                <Header appState={walletConnectionState} onDisconnect={disconnect}>
                    <Routes>
                        <Route path="/" element={<ConnectWalletRoute walletConnectionState={walletConnectionState} onConnect={connect} updateAppState={setWalletConnectionState}/>}/>
                        <Route path="/counter" element={<CounterManagementRoute walletConnectionState={walletConnectionState} />}/>
                        <Route path="/counter/:appID" element={<CounterRoute walletConnectionState={walletConnectionState}/>}/>
                    </Routes>
                </Header>
            </BrowserRouter>
        </WalletConnectContext.Provider>
    );
}

export default App;
