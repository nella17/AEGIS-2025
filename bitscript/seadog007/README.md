# Aegis Query Sender

Script to send queries to OpenAI API using the `responses.create` endpoint.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your-api-key-here
```

Or create a `.env` file (if using dotenv) or modify the script directly.

## Usage

Run the script:
```bash
node send_query.js
```

Or:
```bash
npm start
```

## Note

The script reads content from `defender.txt` and `attacker.txt` files and sends them as part of the query to the OpenAI API.


