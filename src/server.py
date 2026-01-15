import argparse
import uvicorn

import textwrap

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from executor import Executor


def main():
    parser = argparse.ArgumentParser(description="Run the CrypticReasoner-setter A2A agent.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9009, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="URL to advertise in the agent card")
    args = parser.parse_args()

    # Fill in your agent card
    # See: https://a2a-protocol.org/latest/tutorials/python/3-agent-skills-and-card/
    
    skill = AgentSkill(
        id="cryptic_setter",
        name="Cryptic Crossword Setter",
        description="Emits cryptic crossword questions, and mark answers",
        tags=["crypticreasoner"],
        # See : https://github.com/RDI-Foundation/agentbeats-tutorial/blob/main/scenarios/tau2/tau2_evaluator.py#L452
        #  Sending this JSON via the A2A inspector, launches the Green Agent ...
        examples=[textwrap.dedent("""
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
            """).strip()]
        # http://127.0.0.1:9019
        # https://cryptic-solver.example.com:443

    )

    agent_card = AgentCard(
        name="Cryptic Setter",
        description="Set a Cryptic Crossword question; allow for dictionary tool use; and finally mark the answer received",
        url=args.card_url or f"http://{args.host}:{args.port}/",
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill]
    )

    request_handler = DefaultRequestHandler(
        agent_executor=Executor(),
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    uvicorn.run(server.build(), host=args.host, port=args.port)


if __name__ == '__main__':
    main()
