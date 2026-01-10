# A2A Agent for CrypticReasoner task

This repo builds an [A2A (Agent-to-Agent)](https://a2a-protocol.org/latest/) green agent compatible with the [AgentBeats](https://agentbeats.dev) platform.


## Project Structure

```
src/
├─ server.py      # Server setup and agent card configuration
├─ executor.py    # A2A request handling
├─ agent.py       # CrypticReasoner green agent implementation
└─ messenger.py   # A2A messaging utilities
└─ setup.sh       # Download of Cryptonite dataset, dictionary data, and embedding generation
tests/
└─ test_agent.py  # Agent tests
Dockerfile        # Docker configuration
pyproject.toml    # Python dependencies
.github/
└─ workflows/
   └─ test-and-publish.yml # CI workflow
```


## Running Locally

```bash
# Install dependencies
uv sync

pushd src
./setup.sh
popd

# Run the server
uv run src/server.py
```

## Running with Docker

```bash
# Build the image
docker build -t cryptic-reasoner_setter .

# Run the container
docker run -p 9009:9009 cryptic-reasoner_setter
```


## Check that something is happening...

Using the [A2A inspector](https://github.com/a2aproject/a2a-inspector), 
installed in `../a2a-inspector/` (i.e. as a sibling to this repo - 
anticipating the purple-agent will also be a sibling)

```bash
# Run both frontend and backend (of the A2A inspector) with a single command
bash scripts/run.sh
```


## Testing

Run A2A conformance tests against the agent.

```bash
# Install test dependencies
uv sync --extra test

# Start your agent (uv or docker; see above)

# Run tests against your running agent URL
uv run pytest --agent-url http://localhost:9009
```

