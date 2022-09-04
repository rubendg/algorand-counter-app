import {Network} from "./Algod";

export interface WalletConnectionState {
    network: Network,
    account: string | null,
    connected: boolean
}