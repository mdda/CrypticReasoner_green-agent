import argparse
import uvicorn
#from dotenv import load_dotenv
#load_dotenv()

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from a2a.types import (
    AgentCapabilities,
    AgentCard,
)

def main():
    parser = argparse.ArgumentParser(description="Run the CrypticReasoner_solver agent.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9019, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="External URL to provide in the agent card")
    args = parser.parse_args()

    root_agent = Agent(
        name="crypticreasoner_solver",
        model="gemini-2.0-flash",
        #model="gemini-2.5-flash",   # 'THINKING' makes this too slow
        description="Attempts to solve Cryptic Crossword puzzles.",
        instruction="Solve the Cryptic Crossword clues given, using the functions provided.",
    )

    agent_card = AgentCard(
        name="crypticreasoner_solver",
        description='Attempts to solve Cryptic Crossword puzzles.',
        url=args.card_url or f'http://{args.host}:{args.port}/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[],
    )

    a2a_app = to_a2a(root_agent, agent_card=agent_card)
    uvicorn.run(a2a_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()