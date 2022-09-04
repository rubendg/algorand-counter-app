import {Button, FormControl, MenuItem, Select, Stack} from "@mui/material";
import {Network} from "./Algod";

interface Props {
    network: Network,
    onChangeNetwork: (network: Network) => void
    onConnect: () => void
}

export function ConnectAccount({ network, onChangeNetwork, onConnect }: Props) {
    const changeNetwork = (e: any) => {
        e.preventDefault()
        onChangeNetwork(e.target.value)
    }

    return (
        <Stack direction="column" justifyContent="center"
               alignItems="center"
               spacing={2}>
            <FormControl fullWidth>
                <Select displayEmpty value={network} onChange={changeNetwork} inputProps={{ 'aria-label': 'Without label' }}>
                    <MenuItem value="">
                        <em>Select Network</em>
                    </MenuItem>
                    <MenuItem value={Network.MainNet}>Mainnet</MenuItem>
                    <MenuItem value={Network.TestNet}>Testnet</MenuItem>
                    <MenuItem value={Network.LocalNet}>Localnet</MenuItem>
                </Select>
            </FormControl>
            <Button style={{width:'100%'}} variant="outlined" onClick={onConnect}>Connect Wallet</Button>
        </Stack>
    )
}