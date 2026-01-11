import logging
from typing import Any
from pydantic import BaseModel, HttpUrl, ValidationError
from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart, DataPart
from a2a.utils import get_message_text, new_agent_text_message

from messenger import Messenger


import sys, time
cryptic_repo="./src/cryptic-crossword-reasoning-verifier"
sys.path.append(cryptic_repo)
from solver import corpora as cryptic_corpora
from solver import dataset as cryptic_dataset


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cryptic_setter")

class EvalRequest(BaseModel):
    """Request format sent by the AgentBeats platform to green agents."""
    participants: dict[str, HttpUrl] # role -> agent URL
    config: dict[str, Any]
    

class CrypticScore(BaseModel):
    used_tool: bool = False
    answer_in_search: bool = False
    answer_correct: bool = False



class Agent:
    # Fill in: list of required participant roles, e.g. ["pro_debater", "con_debater"]
    required_roles: list[str] = ["cryptic_solver"]
    # Fill in: list of required config keys, e.g. ["topic", "num_rounds"]
    required_config_keys: list[str] = []  # We have fall-back values for each of these

    def __init__(self):
        self.messenger = Messenger()

        # Initialize other state here

        print("Loading Cryptic Crossword data")

        t0=time.time()
        self.embedder = cryptic_corpora.VectorEmbedder(model_file="./src/cc.en.100.bin")
        print(f"Loaded Vector Embedding model in {(time.time()-t0):.2f}sec")

        t0=time.time()
        self.crossword_dictionary = cryptic_corpora.CrosswordDictionary(
            self.embedder, crossword_dictionary_file='./src/UKACD.txt', strip_header=False)
        print(f"Loaded Dictionary in {(time.time()-t0):.2f}sec")


    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        missing_roles = set(self.required_roles) - set(request.participants.keys())
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"

        missing_config_keys = set(self.required_config_keys) - set(request.config.keys())
        if missing_config_keys:
            return False, f"Missing config keys: {missing_config_keys}"

        ## Add additional request validation here

        # Load the dataset and tasks specified in the config...
        dataset = request.config.get("dataset", "cryptonite")
        split   = request.config.get("split", "validation")

        if dataset=='cryptonite':
            if split not in 'train|val|test':
              return False, f"Only train, val, and test splits available for cryptonite"
        else:
            return False, f"Only cryptonite available at present"
        
        self.dataset = cryptic_dataset.load_cryptonite_dataset(split, dataset_path="./src/cryptonite")

        try:
            num_tasks = int( request.config.get("num_tasks", "10") )
            assert 0<num_tasks<len(self.dataset)
        except:
            return False, f"num_tasks must be an integer in [1..{len(self.dataset)})"

        try:
            seed = int( request.config.get("seed", "42") )
        except:
            return False, f"seed must be an integer"

        # This ensures a stable order for shuffled dataset
        shuffled_idx = cryptic_dataset.get_shuffled_idx(self.dataset, seed=seed)
        self.task_indices = shuffled_idx[:num_tasks]  

        return True, "ok"


    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """Implement your agent logic here.

        Args:
            message: The incoming message
            updater: Report progress (update_status) and results (add_artifact)

        Use self.messenger.talk_to_agent(message, url) to call other agents.
        """
        print(f"Agent.run launch! {message=}")  # NOT CALLED YET...

        input_text = get_message_text(message)

        try:
            request: EvalRequest = EvalRequest.model_validate_json(input_text)
            ok, msg = self.validate_request(request)
            if not ok:
                await updater.reject(new_agent_text_message(msg))
                return
        except ValidationError as e:
            await updater.reject(new_agent_text_message(f"Invalid request: {e}"))
            return

        ## At this point, the Green Agent (evaluator) is "running", with configuration 'request.config'

        # Replace example code below with your agent logic
        # Use request.participants to get participant agent URLs by role
        # Use request.config for assessment parameters

        await updater.update_status(
            TaskState.working, new_agent_text_message("Thinking...")
        )

        # Iterate through each task
        for task_idx in self.task_indices:
            self.run_single_task(self.dataset[task_idx])
        
        await updater.add_artifact(
            parts=[
                Part(root=TextPart(text="The agent completed the tasks.")),
                Part(root=DataPart(data={
                    # structured assessment results
                }))
            ],
            name="Result",
        )

    def run_single_task(self, data_item):
        print(data_item)

