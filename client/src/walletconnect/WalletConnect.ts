import QRCodeModal from "algorand-walletconnect-qrcode-modal";
import WalletConnect from "@walletconnect/client";
import {createContext} from "react";
import {formatJsonRpcRequest, JsonRpcRequest} from "@json-rpc-tools/utils";
import {encodeUnsignedTransaction, Transaction, TransactionSigner} from "algosdk";
import {SignTxnParams, WalletTransaction} from "./spec";
import {uint8ArrayFromBase64} from "../helpers";

const connectProps = {
    bridge: "https://bridge.walletconnect.org",
    qrcodeModal: QRCodeModal,
}
const connector = new WalletConnect(connectProps);

export const WalletConnectContext = createContext<WalletConnect>(connector);

function algoSignTxn(requestParams: SignTxnParams, id?: number | undefined): JsonRpcRequest<SignTxnParams> {
    return formatJsonRpcRequest("algo_signTxn", requestParams, id)
}

function txnToBase64(txn: Transaction): string {
    return Buffer.from(encodeUnsignedTransaction(txn)).toString("base64")
}

// Records the need for a WalletConnect signer instance: https://github.com/algorand/js-algorand-sdk/issues/411
export function WalletConnectSigner(wc: WalletConnect, account: string, message: string): TransactionSigner {
    let requestID = 0
    return async (txnGroup, indexesToSign): Promise<Uint8Array[]> => {
        const txnsToBeSigned: WalletTransaction[] = []
        for (const i of indexesToSign) {
            const txn = txnGroup[i]

            txnsToBeSigned.push({
                txn: txnToBase64(txn),
                message: message,
            })
        }

        const request = algoSignTxn([txnsToBeSigned], ++requestID)
        const result: Array<string | null> = await wc.sendCustomRequest(request)

        const decodedResult = result.map(element => {
            return element ? uint8ArrayFromBase64(element) : null
        })

        return decodedResult.filter(e => e !== null) as Uint8Array[]
    }
}