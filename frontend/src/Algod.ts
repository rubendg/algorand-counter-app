import {Algodv2} from "algosdk";

const mainNetClient = new Algodv2("", "https://mainnet-api.algonode.cloud", "");
const testNetClient = new Algodv2("", "https://node.testnet.algoexplorerapi.io", "");
const localNetClient = new Algodv2("", "https://localhost", "4001");

export enum Network {
    MainNet = "mainnet",
    TestNet = "testnet",
    LocalNet = "localnet"
}

export const accountExplorer = (network: Network, account: string) => {
    let base;
    switch (network) {
        case Network.MainNet:
            base = 'https://algoexplorer.io/address'
            break
        case Network.TestNet:
            base = 'https://testnet.algoexplorer.io/address'
            break
        case Network.LocalNet:
            base = "http://localhost:4001"
            break
        default:
            throw new Error(`Unknown network type: ${network}`);
    }
    return `${base}/${account}`;
}

export function clientForNetwork(network: Network): Algodv2 {
    switch (network) {
        case Network.MainNet:
            return mainNetClient;
        case Network.TestNet:
            return testNetClient;
        case Network.LocalNet:
            return localNetClient
        default:
            throw new Error(`Unknown network: ${network}`);
    }
}