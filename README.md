# Qwen2.5-Coder 3B agent experiments

A small, local coding agent built around a small, local model, running on an old Mac.

The question behind this project is simple: **how much can tools, tests and a tight feedback loop make up for a weak model?** A 3B model can't be taught to reason better by wrapping it in Python. But the wrapper decides what the model can see, what it can do, and whether its work gets checked, and that is something I can build and measure myself.

## Background

### The machine

| | |
|---|---|
| Hardware | 2013/14 MacBook, Intel i5-4258U (2 cores, 4 threads), 8 GB RAM |
| Acceleration | None. Inference is CPU-only; the integrated GPU isn't used |
| Runtime | Ollama (llama.cpp underneath) |
| Model | Qwen2.5-Coder 3B Instruct, Q4_K_M, 1.79 GiB on disk |

The constraints are the point. There is no room here to hide an inefficient design behind a lot of memory bandwidth. If an agent works acceptably on this machine, I'll know why it works, and I can later run the same thing on Apple Silicon and see exactly what better hardware buys.

### Baseline measurements

Taken from the Ollama server logs during the first sessions.

**Memory**

| Allocation | Size |
|---|---|
| Model buffer | 569 MiB |
| Repacked model buffer | 1,266 MiB |
| KV cache (4,096 tokens) | 144 MiB |
| Compute buffer | 85 MiB |
| **Total** | **≈ 2.0 GiB** |

The model was trained for a 32K context but Ollama runs it at 4K. The KV cache is cheap because of grouped-query attention (16 attention heads sharing 2 KV heads), so 8K would cost roughly 288 MiB and 16K roughly 576 MiB. The real cost of a longer context on this CPU is attention compute, not memory.

**Speed**

| | Short context | Long context (~3K tokens) |
|---|---|---|
| Generation | ~5.5 tok/s | ~3.5–4 tok/s |
| Prompt processing | ~12 tok/s | ~14–16 tok/s |

A few examples that show where the time goes:

- An 871-token prompt took **55 s** just to read.
- A 2,727-token prompt with no cache hit took **194 s** to read, then 56 s to generate 157 tokens.
- A follow-up on a 2,902-token conversation that matched 2,883 tokens of cached prefix took **12 s** in total.

**Other things the logs confirmed**

- llama.cpp uses 2 of the 4 logical threads by default.
- Sampling is ordinary: temperature 0.8, top-k 40, top-p 0.9, no mirostat, no DRY.
- There is no hidden "thinking" mode and no speculative decoding. What comes out is a plain completion.

### The failure that started this

I asked the model to review a function against an exact specification. It reported no problems. The function had no `return` statement.

That is a more useful result than "the code was mediocre". The model can't reliably check its own work, but a test runner can. If the agent runs the test and hands back `AssertionError: expected list, got None`, the model no longer has to notice the bug by itself. It only has to respond to the evidence.

## Design principles

These come straight out of the numbers above.

1. **Let the environment do the checking.** The model proposes; the interpreter, the tests and `git diff` decide. Correctness moves out of the network and into deterministic machinery.
2. **Keep prompts small and stable.** Reading context is slow, and a cache miss can cost minutes. A fixed system prompt at the front, with tool results appended at the end, keeps the shared prefix cached.
3. **Keep output short.** At 4 tok/s, a 500-token explanation costs two minutes. The model should emit actions, not narration.
4. **Let the model ask for things.** Don't dump the repository into the prompt. Give it a way to request a file when it needs one.
5. **Start almost absurdly small.** No embeddings, no vector store, no RAG framework, no multi-agent setup. A filesystem and a Python interpreter are enough for a first version.
6. **Keep it on a leash.** The agent works inside a sandboxed project directory, with a git checkpoint before every edit.

## The loop

```
TASK → MODEL → ACTION → EXECUTE → OBSERVATION → MODEL → … → TESTS PASS
```

Each turn, the model sees only:

- the system instructions
- the current task
- the file(s) it has asked for
- the latest tool result
- a short summary of prior state

Actions are structured tool calls, for example:

```json
{ "tool": "run_command", "command": "python3 -m pytest" }
```

## Roadmap

### Phase 0: Know the machine

Before writing any agent code, find out what the hardware can actually do.

- [ ] Benchmark 1, 2 and 4 threads on an identical prompt. More isn't always better with hyperthreading.
- [ ] Compare 4K and 8K context: memory use, prompt speed, generation speed.
- [ ] Try temperature 0.2–0.4 against the default 0.8 for editing tasks.
- [ ] Write a small script that pulls tokens/sec and cache hits out of the Ollama logs, so every later run is measured the same way.
- [ ] Keep the raw logs from the first sessions as the reference baseline.

### Phase 1: The smallest agent that works

About 150–300 lines of Python, with four tools and nothing else:

- `read_file`
- `write_file` (or `patch_file`)
- `run_command`
- `git_diff`

Plus a loop, a turn limit, and a git commit before every edit so that any bad change can be rolled back.

**Done when** the agent can take the missing-`return` function from above, run its test, read the failure, fix it and stop on a pass.

### Phase 2: A benchmark of small, deliberately broken programs

A set of tiny tasks aimed squarely at the model's weak spots:

- a missing `return`
- off-by-one errors
- a wrong comparison or boundary condition
- an ambiguous bug where the test is the only real specification
- a failing test that needs changes in two places

Each task is a directory holding the broken code, the tests and a short task description.

### Phase 3: Bare model vs. agent

Run every task twice: once as a single prompt to the bare model, once through the agent. For each run, record:

- pass or fail
- model turns
- tool calls
- tokens read and generated
- wall-clock time

This gives a rough measure of *effective capability per parameter*. A model that needs four corrective rounds but reliably reaches a passing test is more useful than one that writes a polished answer that doesn't run.

### Phase 4: Only add what the results ask for

Each of these is added only if Phase 3 shows it helps, and each is measured on its own:

- More tools: `list_directory`, `grep`, `git_status`, `run_tests`
- A small `.agent/` state directory (`task.md`, `plan.md`, `state.md`) so a long task can survive a reset of the context
- An explicit plan → act → critique step
- Sampling several candidate fixes, testing each, and keeping the best
- Trimming and summarising tool output so prompts stay short

### Phase 5: Move to better hardware

Run the same agent and the same benchmark on an Apple Silicon machine. Compare memory, prompt speed, generation speed and task success against the Intel baseline, then try larger models in the same harness.

### Not planned for now

- Fine-tuning or LoRA training. This machine can't do meaningful training on a 3B model, and it isn't where the interesting questions are yet.
- Copying Claude Code feature by feature. The aim is to understand each piece, not to rebuild a product.

## What I expect to learn

Where the line sits between weaknesses that tooling can make up for and weaknesses that belong to the model itself. A small model on slow hardware is a good way to find that line, because every bottleneck is out in the open.
