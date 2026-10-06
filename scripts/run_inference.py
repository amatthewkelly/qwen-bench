#!/usr/bin/env python3

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:3b"

def generate(prompt, threads):
    payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "keep_alive": 0,
            "options": {
                "num_thread": threads,
            }
    }

    request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request) as response:
        return json.load(response)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--raw-dir", default="results/experiment-001-thread-scaling/raw")
    args= parser.parse_args()

    prompt = sys.stdin.read()
    result = generate(prompt, args.threads)

    raw_dir = args.raw_dir
    os.makedirs(raw_dir, exist_ok=True)

    raw_path = os.path.join(raw_dir, f"{args.run_id}.json")
    runs_path = os.path.join(
            os.path.dirname(raw_dir), 
            "runs.jsonl",
    )

    observation = {
        "run_id": args.run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": result["model"],
        "threads": args.threads,
        "prompt_eval_count": result.get("prompt_eval_count"),
        "cache_valid": result.get("prompt_eval_cached_count") == 0,
        "prompt_eval_cached_count": result.get("prompt_eval_cached_count"),
        "prompt_eval_duration_ns": result.get("prompt_eval_duration"),
        "eval_count": result.get("eval_count"),
        "eval_duration_ns": result.get("eval_duration"),
        "load_duration_ns": result.get("load_duration"),
        "total_duration_ns": result.get("total_duration"),
        "response": result.get("response"),
    }

    with open(raw_path, "w") as f:
        json.dump(
            {
                "observation": observation,
                "raw_response": result,
            },
            f,
            indent=2,
        )

    with open(runs_path, "a") as f: 
        json.dump(observation, f)
        f.write("\n")

    prompt_duration = result.get("prompt_eval_duration", 0) / 1e9
    eval_duration = result.get("eval_duration", 0) / 1e9

    prompt_tok_s = (
        result["prompt_eval_count"] / prompt_duration
        if prompt_duration
        else None
    )

    generation_tok_s = (
        result["eval_count"] / eval_duration
        if eval_duration
        else None
    )
    
    if result.get("prompt_eval_cached_count") != 0:
        print("WARNING: prompt cache was used; this run is invalid.")

    print(f"run:              {args.run_id}")
    print(f"threads:           {args.threads}")
    print(f"prompt tokens:     {result.get('prompt_eval_count')}")
    print(f"cached tokens:     {result.get('prompt_eval_cached_count')}")
    print(f"output tokens:     {result.get('eval_count')}")
    print(f"prompt tok/s:      {prompt_tok_s:.2f}")
    print(f"generation tok/s:  {generation_tok_s:.2f}")
    print(f"load time:         {result.get('load_duration', 0) / 1e9:.2f}s")
    print(f"raw result:        {raw_path}")
if __name__ == "__main__":
    main()
