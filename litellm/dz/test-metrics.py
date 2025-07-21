import asyncio
import datetime
import json
import os
import sys
import time

import litellm
from dotenv import load_dotenv
from litellm import acompletion


def get_latency(input_string: str) -> int:
    """
    Splits a string by the last colon (':') and convert the last part to an integer.
    wit default return 0 in case of any failure.
    """
    head, separator, tail = input_string.rpartition(':')

    if not separator:
        return 0
    else:
        try:
            return int(tail.strip())
        except ValueError:
            return 0


async def single(file_name: str, model: str, region: str) -> None:
    with open(file_name) as f:
        request = f.read()

    messages_dict = json.loads(request)
    # options = {"performanceConfig": {"latency": "optimized"}}
    start = time.monotonic()
    start_utc = datetime.datetime.now(datetime.timezone.utc);

    response = await acompletion(
        model=model,
        # messages=[
        #     {"role": "user", "content": "hi"}
        # ],
        messages=messages_dict,
        aws_region_name=region,
    )
    took = int(1000 * (time.monotonic() - start))
    latency = get_latency(response.system_fingerprint)
    delta = took - latency
    print(region, model, start_utc, "Took:", took, "latency:", latency, delta)


async def main(repeat, region="us-east-1") -> None:
    load_dotenv()

    if len(sys.argv) > 1:
        region = sys.argv[1]

    # os.environ["LITELLM_SSL_VERIFY"] = "False"
    # litellm.ssl_verify = False
    # litellm.disable_token_counting = True
    # litellm.disable_end_user_cost_tracking=True
    # litellm.disable_hf_tokenizer_download=True

    # litellm._turn_on_debug()
    # litellm.set_verbose = True
    # litellm.log_raw_request_response = True

    models = [
        # "bedrock/amazon.nova-pro-v1:0",
        # "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
        # "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",
        "bedrock/anthropic.claude-3-haiku-20240307-v1:0",
    ]

    agent_ids = []

    for filename in os.listdir("."):
        if filename.endswith(".request"):
            agent_ids.append(filename)
            # break  # take on request file for now

    for model in models:
        tasks = [
            single(agent_id, model, region)
            for agent_id in agent_ids
            for _ in range(repeat)
        ]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main(1, "eu-west-1"))
    print("")
    asyncio.run(main(1, "us-east-1"))
