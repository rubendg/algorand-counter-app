import {ABIMethod, Algodv2, AtomicTransactionComposer, TransactionSigner} from "algosdk";

export class CounterContract {
    static approvalProgram = 'BiACAAEmAgdjb3VudGVyBBUffHUxGyISQABJNhoAgAQvqvaGEkAAJTYaAIAE/p+WaxJAAAEAMRkiEjEYIhMQRIgAgzUBKTQBFlCwI0MxGSISMRgiExBEiABcNQApNAAWULAjQzEZIhJAACUxGYEEEkAAEzEZgQUSQAABADEYIhNEiAAeI0MxGCITRIgAICNDMRgiEkSIAAIjQygiZ4kyCRKJMQCI//dEI0MyCRKJMQCI//dEI0MoZCINQQAGKChkIwlnKGSJKGSB////////////AQxBAAYoKGQjCGcoZIk='
    static clearProgram = 'BoEAQw=='

    client: Algodv2
    appID: number
    sender: string
    signer: TransactionSigner

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

export class UnexpectedApplication extends Error {}

export async function fetchApplicationInfo(client: Algodv2, appID: number) {
    const { params: { creator, 'global-state': globalState, 'approval-program': approvalProgram, 'clear-state-program': clearProgram  } } = await client.getApplicationByID(appID).do()

    if (approvalProgram !== CounterContract.approvalProgram || clearProgram !== CounterContract.clearProgram) {
        throw new UnexpectedApplication()
    }

    return {appID, count: globalState[0].value.uint, creator }
}
