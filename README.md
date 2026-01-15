# A2A Agent for CrypticReasoner task

Code for the [A2A (Agent-to-Agent)](https://a2a-protocol.org/latest/) 
CrypticReasoner evaluation green agents compatible 
with the [AgentBeats](https://agentbeats.dev) platform.

## Abstract

Cryptic crossword clues are challenging language tasks for which new test sets 
are released daily by major newspapers on a global basis. Each cryptic clue contains 
both the definition of the answer to be placed in the crossword grid (in common with regular crosswords), 
and 'wordplay' that proves that the answer is correct 
(i.e. a human solver can be confident that an answer is correct without needing crossing words as confirmation). 

This green (evaluation) agent (for the AgentBeats platform) provides a test-bed for 
evaluation of Cryptic Crossword solver agents.  In addition to providing the questions 
(from the [Cryptonite Dataset](https://github.com/aviaefrat/cryptonite) of 
Times/Telegraph cryptic crossword clues/answers), this green agent also provides a 
`dictionary_search` tool, that allows purple (solver) agents to look up potential answers,
subject to constraints (definition, word-length(s) and substrings).  This makes the 
task more approachable by LLMs, since (even today) they have significant problems with
counting letters, and doing anagrams.

Even with the `dictionary_search` tool, however, these Cryptic Crossword puzzles are
tough : simply searching for the `definition` word will often not include the actual answer
within the top 10 returned results - using the `wordplay` to suggest substrings will narrow the 
search substantially.  This requires some reasoning...


## Project Structure

```
src/
├─ setup.sh       # Download of Cryptonite dataset, dictionary data, and embedding generation
├─ server.py      # Server setup and agent card configuration
├─ executor.py    # A2A request handling
├─ agent.py       # CrypticReasoner green agent (cryptic puzzle setter) implementation
├─ messenger.py   # A2A messaging utilities
└─ purple_agent_gemini-flash.py  # Basic purple (cryptic puzzle solver) implementation
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

# Run the server
uv run src/server.py
```

### Running the basic Purple agent

There's a simple Gemini-Flash-2.0 based purple agent 
(`cryptic-reasoner_solver`) in the `./src` directory.

This can be run locally with:
```bash
GOOGLE_API_KEY="YOUR-API-KEY-FROM-AISTUDIO" uv run src/purple_agent_gemini-flash.py 
```

There will be plenty of debugging output in the green agent (evaluator) console.


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
anticipating the final purple-agent(s) will also be a sibling)

```bash
# Run both frontend and backend with a single command
# within the ./a2a-inspector repo's directory
bash scripts/run.sh
```

Use a browser to go to `http://127.0.0.1:5001/` to see the A2A inspector interface:
* Enter the address of the evaluator (green) agent (eg: `http://127.0.0.1:9009 `)
* Click on 'Connect' to connect to the running evaluator
* Copy-Paste the following into the final message box, and press 'Send' to do an evaluation

```json
{
   "participants": {
      "cryptic_solver": "http://localhost:9019"
   },
   "config": {
      "dataset": "cryptonite",
      "split": "val",
      "num_tasks": 2,
      "seed": 42
   }
}
```



## Testing

Run A2A conformance tests against your agent.

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



## Citing this work

The Cryptic Crossword utilities, etc, are derived from the codebase associated from this work:

```bibtex
@inproceedings{andrews-cryptic-reasoning-2025,
  title={A Reasoning-Based Approach to {Cryptic Crossword} Clue Solving},
  author={Martin Andrews and Sam Witteveen},
  booktitle={Forty-second International Conference on Machine Learning},
  year={2025},
  url={https://openreview.net/forum?id=kBTgizDiCq},
  url_arxiv={http://arxiv.org/abs/2506.04824}
}
```

## Acknowledgements

Support for this research was provided by the Google AI Developer Programs team, including access to the Gemini models and GPUs on Google Cloud Platform.  

In addition, we were generously supplied credits by [Lambda AI](https://lambda.ai/) which will 
be valuable when constructing (purple) Agents that solve the Cryptic Reasoning task effectively.

