import {
    ABIMethod,
    Algodv2,
    AtomicTransactionComposer,
    makeApplicationCreateTxn,
    OnApplicationComplete,
    TransactionSigner, waitForConfirmation
} from "algosdk";
import raw from "raw.macro";
import {uint8ArrayFromBase64} from "../helpers";

// CounterContract makes interacting with the Counter ABI more convenient
export class CounterContract {
    private static contract: { approvalProgram: string, clearProgram: string } = JSON.parse(raw('../../contract.json'))

    static approvalProgram = this.contract.approvalProgram
    static clearProgram = this.contract.clearProgram

    client: Algodv2
    appID: number
    sender: string
    signer: TransactionSigner

    static async create(client: Algodv2, sender: string, signer: TransactionSigner) {
        const sp = await client.getTransactionParams().do()

        const numLocalInts = 0
        const numLocalByteSlices = 0
        const numGlobalByteSlices = 1
        const numGlobalInts = 1

        const [signedTx] = await signer(
            [makeApplicationCreateTxn(sender, sp, OnApplicationComplete.NoOpOC, uint8ArrayFromBase64(this.approvalProgram), uint8ArrayFromBase64(this.clearProgram), numLocalInts, numLocalByteSlices, numGlobalInts, numGlobalByteSlices)],
            [0]
        )

        const { txId } = await client.sendRawTransaction(signedTx).do()
        const completedTx = await waitForConfirmation(client, txId, 2)

        return completedTx['application-index']
    }

    constructor(client: Algodv2, appID: number, sender: string, signer: TransactionSigner) {
        this.client = client
        this.appID = appID
        this.sender = sender
        this.signer = signer
    }

    private async _methodCallParams(signature: string) {
        const sp = await this.client.getTransactionParams().do()
        return {
            appID: this.appID,
            method: ABIMethod.fromSignature(signature),
            methodArgs: [],
            sender: this.sender,
            suggestedParams: sp,
            signer: this.signer,
        }
    }

    async inc() {
        const composer = new AtomicTransactionComposer()
        composer.addMethodCall(await this._methodCallParams('inc()uint64'))

        const result = await composer.execute(this.client, 2)
        const { methodResults: [{returnValue}] } = result
        return returnValue as bigint
    }

    async dec() {
        const composer = new AtomicTransactionComposer()
        composer.addMethodCall(await this._methodCallParams('dec()uint64'))

        const result = await composer.execute(this.client, 2)
        const { methodResults: [{returnValue}] } = result
        return returnValue as bigint
    }
}
