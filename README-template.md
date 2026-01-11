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


## Getting Started

1. **Create your repository** - Click "Use this template" to create your own repository from this template

2. **Implement your agent** - Add your agent logic to [`src/agent.py`](src/agent.py)

3. **Configure your agent card** - Fill in your agent's metadata (name, skills, description) in [`src/server.py`](src/server.py)

4. **Write your tests** - Add custom tests for your agent in [`tests/test_agent.py`](tests/test_agent.py)

For a concrete example of implementing a green agent using this template, see this [draft PR](https://github.com/RDI-Foundation/green-agent-template/pull/3).



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


## Testing

Run A2A conformance tests against the agent.

```bash
# Install test dependencies
uv sync --extra test

# Start your agent (uv or docker; see above)

# Run tests against your running agent URL
uv run pytest --agent-url http://localhost:9009
```


## Publishing

The repository includes a GitHub Actions workflow that automatically builds, tests, and publishes a Docker image of your agent to GitHub Container Registry.

If your agent needs API keys or other secrets, add them in Settings → Secrets and variables → Actions → Repository secrets. They'll be available as environment variables during CI tests.

- **`git push` to `main`** → publishes `latest` tag:
```
ghcr.io/<your-username>/<your-repo-name>:latest
```

If this fails, then GitHub sends an email with the Subject "[CrypticReasoner_green-agent] Run failed: Test and Publish Agent..."



- **Create a git tag** (e.g. `git tag v1.0.0 && git push origin v1.0.0`) → publishes version tags:
```
ghcr.io/<your-username>/<your-repo-name>:1.0.0
ghcr.io/<your-username>/<your-repo-name>:1
```

Once the workflow completes, find your Docker image in the Packages section (right sidebar of your repository). Configure the package visibility in package settings.

> **Note:** Organization repositories may need package write permissions enabled manually (Settings → Actions → General). Version tags must follow [semantic versioning](https://semver.org/) (e.g., `v1.0.0`).

