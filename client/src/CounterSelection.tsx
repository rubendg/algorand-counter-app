import React, {useState} from "react";
import {Button, Grid, Stack, TextField} from "@mui/material";

interface Props {
    onCounterSelected: (appID: number) => void
}

export function CounterSelection({onCounterSelected} : Props) {
    const [appID, setAppID] = useState<number | null>()

    const connect = async () => {
        if (!appID) return
        onCounterSelected(appID)
    }

    const updateAppID = (e: any) => {
        const n = Number(e.target.value)
        if(isNaN(n)) {
            setAppID(null)
            return
        }
        setAppID(n)
    }

    return (
        <Stack>
            <Grid container spacing={2}>
                <Grid item xs={8}>
                    <TextField style={{width:'100%'}} variant="outlined" placeholder="Fill in application id" inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                               onChange={updateAppID}></TextField>
                </Grid>
                <Grid item xs={4} display="flex">
                    <Button disabled={!appID} style={{width:'100%', alignContent: 'stretch'}} onClick={connect} variant="outlined">Connect</Button>
                </Grid>
            </Grid>
        </Stack>
    )
}