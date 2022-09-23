import {useState} from "react";
import {Backdrop, CircularProgress} from "@mui/material";

export function uint8ArrayFromBase64(e: string): Uint8Array {
    return new Uint8Array(Buffer.from(e, "base64"))
}

export function usePendingState(): [boolean, (f: () => Promise<void>) => (() => Promise<void>)] {
    const [pending, setPending] = useState(false)

    const withPending = (f: () => Promise<void>) => {
        return async () => {
            setPending(true)
            try {
                return await f()
            } catch (e) {
                throw e
            } finally {
                setPending(false)
            }
        }
    }

    return [pending, withPending]
}

export function Pending({pending, children}: any) {
    return <>
        <Backdrop sx={{ color: '#fff', 'zIndex': (theme) => theme.zIndex.drawer + 1 }} open={pending}>
            <CircularProgress color="inherit" />
        </Backdrop>
        {children}
    </>
}
