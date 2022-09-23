## Algorand - Counter Frontend

A frontend for creating new counter applications and interacting with existing ones.

## Requirements

- Node >= 18 installed, e.g. using the [node version manager](https://github.com/nvm-sh/nvm)

## Project Layout

- `public`, contains the public resources that'll be bundled into the final app distribution
- `src`, contains the React / TypeScript application 
- `contract.json`, hard-codes the compiled approval and clear programs used for creating new application instances and verifying compatibility between frontend and application

## Setup

```bash
npm i
```

## Development

```bash
npm start
```
