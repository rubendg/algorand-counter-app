# Algorand - Counter Smart Contract

A counter maintained as a single global variable `counter`, which can be incremented or decremented by anyone.

## Requirements

- Python3 installed, e.g. using [pyenv](https://github.com/pyenv/pyenv) on MacOS: `brew install pyenv`
- [Algorand Sandbox](https://github.com/algorand/sandbox)

## Project Layout

- `contract`, contains the application written in PyTeal and a wrapper for easy use during testing and deployment.
- `build`, contains the compiled Teal code and the Application Binary Interface (ABI).
- `tests`, contains an integration tests for the application written in `pytest`.
- `tools`, contains several tools that assist with compiling and deploying the application.

## Setup

First, clone the Algorand Sandbox, which will be used to locally deploy and test the application:

```bash
git clone https://github.com/algorand/sandbox
```

Then, clone this repo:

```bash
git clone https://github.com/rubendg/algorand-counter-app
```

Initialize the project and its dependencies by running:

```bash
make setup

# activate virtual env
source venv/bin/activate
```

This should leave you with a proper Python environment:

```bash
(venv) $ python -V
Python 3.10.4
```

Then copy the `deploy.ini.example` to `deploy.ini`:

```bash
cp deploy.ini.example deploy.ini
```

This configuration file contains the information necessary to deploy the application to an Algorand node.

## Testing

After the setup steps you're ready to run the integration tests that'll connect to your locally running Algorand node,
deploy the application, and perform a set of tests against it:

```bash
$ make integration-test
scheduling tests via LoadScheduling

tests/test_counter.py::TestCounter::test_starts_at_zero
tests/test_counter.py::TestCounter::test_inc
...
...
[gw3] PASSED tests/test_counter.py::TestCounter::test_underflow
[gw1] PASSED tests/test_counter.py::TestCounter::test_inc_and_dec

====================== 10 passed in 91.26s (0:01:31) ===================
```

## Deployment

In order to deploy the application to default network (sandbox) run:

```bash
(venv) $ make deploy
Deploying backend to default@http://localhost:4001 from account:JDNCJRVYRW6MBTXE5MB6VVQEVITWKYUSO4MG6G746B4LCHOABEAXLFGHS4 ...
Application deployed on backend address:JQZFRQ2PAZ35SG5UH6JWTTDEHL3IDYASZNGWIKGPTN5VSJ2O3ODZHSZILE with app_id:444
```

After using the application it can also be removed:

```bash
(venv) $ make undeploy APP_ID=444
Removing backend:444 at default@http://localhost:4001 using account:JDNCJRVYRW6MBTXE5MB6VVQEVITWKYUSO4MG6G746B4LCHOABEAXLFGHS4 ...
Removed backend in tx_id:4O6HGJ2QIYQ2EKX4QTOPBOLFQ2UREXJX2BHS5TYEKURAJ4Q73HQA
```

Similarly, it works for other networks as well by using the `NETWORK` variable:

```bash
make deploy NETWORK=testnet-algoexplorer
make undeploy NETWORK=testnet-algoexplorer APP_ID=xxx
```

For further settings see [deploy.ini.example](application/deploy.ini.example).

## Development

For code quality, formatting, and type checking run:

```bash
make lint
```

In order to compile the PyTeal application to Teal run:

```bash
make build
```

this will output the ABI along with the Teal approval and clear program in [build](application/build).

## Debugging

https://github.com/algorand/go-algorand/blob/master/cmd/tealdbg/README.md
https://plugins.jetbrains.com/plugin/15300-algodea-algorand-integration

## Troubleshooting

The integration tests rely on funded test accounts. The funds are transferred from an account that got funded at genesis,
if the funding account runs out, you can simply reset the sandbox and start from scratch:

```bash
./sandbox clean
./sandbox up
```
