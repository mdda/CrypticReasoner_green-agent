import logging
from typing import Any
from pydantic import BaseModel, HttpUrl, ValidationError
from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart, DataPart
from a2a.utils import get_message_text, new_agent_text_message

from messenger import Messenger


import sys, time, json
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


ANSWER_ACTION_NAME = "answer"
SEARCH_ACTION_NAME = "dictionary_search"


# Do these loads globally, since they are static (don't depend on Agent launches)
print("Loading Cryptic Crossword data")

t0=time.time()
vector_embedder = cryptic_corpora.VectorEmbedder(model_file="./src/cc.en.100.bin")
print(f"Loaded Vector Embedding model in {(time.time()-t0):.2f}sec")

t0=time.time()
crossword_dictionary = cryptic_corpora.CrosswordDictionary(
    vector_embedder, crossword_dictionary_file='./src/UKACD.txt', strip_header=False)
print(f"Loaded Dictionary in {(time.time()-t0):.2f}sec")


def tidy_up_answer(ans):
    ans = ''.join([a for a in ans.upper() if 'A' <= a <= 'Z'])
    return ans


class Agent:
    # Fill in: list of required participant roles, e.g. ["pro_debater", "con_debater"]
    required_roles: list[str] = ["cryptic_solver"]
    # Fill in: list of required config keys, e.g. ["topic", "num_rounds"]
    required_config_keys: list[str] = []  # We have fall-back values for each of these

    def __init__(self):
        self.messenger = Messenger()

        # Initialize other state here

        # Main dictionary / embedding model are loaded globally (above)


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

        agent_url = str(request.participants["cryptic_solver"])
        logger.info(f"Running {len(self.task_indices)} tasks")

        await updater.update_status(
            TaskState.working, 
            new_agent_text_message(f"Starting evaluation of {len(self.task_indices)} tasks")
        )

        # Iterate through each task
        try: 
            preamble=f"""Cryptic Crossword clue answering

You may use both reasoning and the following dictionary tool to answer the given clues:

{json.dumps({
    "type": "function",
    "function": {
        "name": SEARCH_ACTION_NAME,
        "description": "Look up nearest matches to a given definition, given constraints.",
        "parameters": {
            "properties": {
                "definition": {
                    "description": "The search term, which the responses will be close to.",
                    "title": "Definition",
                    "type": "string"
                },
                "pattern": {
                    "description": "The format required for each response in standard notation - e.g. (8) for eight-letter responses.",
                    "title": "Pattern",
                    "type": "string"
                },
                "substrings": {
                    "description": "A comma-separated list of strings that must be included in each response.",
                    "title": "Substrings",
                    "type": "string"
                }
            },
            "required": ["definition"],
            "title": "parameters",
            "type": "object"
        }
    }
}, indent=2)}

The final answer should be returned using the following tool call:

{json.dumps({
    "type": "function",
    "function": {
        "name": ANSWER_ACTION_NAME,
        "description": "Respond directly to the user with a message instead of calling a tool.",
        "parameters": {
            "properties": {
                "answer": {
                    "description": "The final answer to the cryptic crossword clue - a single string, no explanation.",
                    "title": "Answer",
                    "type": "string"
                }
            },
            "required": ["answer"],
            "title": "parameters",
            "type": "object"
        }
    }
}, indent=2)}


Please respond in JSON format.
The JSON should contain:
- "name": the tool call function name.
- "arguments": the arguments for the tool call.

You should only use one tool at a time!
You cannot respond to user and use a tool at the same time!

Examples of responses (for the clue "Initially, babies are naked (4)")
<json>
{json.dumps({"name": "dictionary_search", "arguments": {"definition": "naked", "pattern": "(4)", "substrings": "B"}}, indent=2)}
</json>

the tool call response is a list of the 10 closest words obeying the constraints given.

<json>
{json.dumps({"name": ANSWER_ACTION_NAME, "arguments": {"answer": "BARE"}}, indent=2)}
</json>

---

"""

            result_arr=[]
            for task_idx in self.task_indices:
                logger.info(f"Running task {task_idx}...")
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(f"Running task {task_idx}...")
                )
                result = self.run_single_task(agent_url, self.dataset[task_idx], preamble)
                result_arr.append(result)

                preamble=""  # Use for just the first task


        
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text="The agent completed the tasks.")),
                    Part(root=DataPart(data={
                        # structured assessment results
                        "results": result_arr,
                    }))
                ],
                name="Result",
            )

        finally:
            self._tool_provider.reset()


    async def run_single_task(self, agent_url, data_item, preamble="", max_turns=20):
        #print(data_item)
        async def agent_turn(prompt: str) -> str:
            response = await self.messenger.talk_to_agent(
                prompt, agent_url, new_conversation=False
            )
            logger.info(f"{agent_url}: {response}")
            #debate[role].append(response)
            await updater.update_status(
                TaskState.working, new_agent_text_message(f"{agent_url}: {response}")
            )
            return response

        # Opening with the question

        # {'publisher': 'Telegraph', 'date': 1212710400000, 'author': None, 
        # 'number': '27', 'orientation': 'across', 
        # 'clue': 'little bird to dart across sill (10)', 'answer': 'fledgeling', 
        # 'enumeration': '(10)', 
        # 'quick': False, 'sub_publisher': None, 'idx_orig': 8116, 'idx_shuffled': 0}
        orientation = ''
        if 'orientation' in data_item:
            orientation = data_item['orientation']+' '
        response = await agent_turn(
            preamble+f"Cryptic Crossword {orientation}clue: {data_item['clue']}"
        )
        answer_setter = tidy_up_answer(data_item['answer'])

        turn, score = 0, 0
        while turn<max_turns:
            try:
                action_dict = json.loads(response)

                if action_dict["name"] == ANSWER_ACTION_NAME:
                    answer_solver = action_dict["arguments"]["answer"]
                    answer_solver = tidy_up_answer(answer_solver)
                    if answer_solver == answer_setter:
                        score = 1  # Success!
                    break

                if action_dict["name"] == SEARCH_ACTION_NAME:
                    definition = action_dict["arguments"]["definition"]
                    pattern = action_dict["arguments"].get("pattern", None)
                    substrings = action_dict["arguments"].get("substrings", "").split(',')

                    nearest_matches = crossword_dictionary.find_nearest_words(
                        definition, k=10, pattern=pattern, substrings=substrings)
                    
                    # How do we return the tool call result?
                    response = await agent_turn(f"""
<json>
{json.dumps({"nearest_matches": nearest_matches}, indent=2)}
</json>
""".trim())

                # Otherwise, just swallow the bad tool call... 

            except (json.JSONDecodeError, KeyError) as e:
                # If parsing fails, treat the response as plain text to user
                logger.warning(f"Failed to parse agent response as JSON: {e}")

            turn+=1

        return dict(
            score=score, critique="",
        )

