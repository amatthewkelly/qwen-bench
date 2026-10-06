

How does a small local language model perform on constrained CPU hardware, and how much can tool use and deterministic feedback compensate for model limitations?

# Baseline Configuration

## Hardware
- Machine: MacBookPro11,1
- CPU: Intel Core i5-4258U
- Physical cores: 2
- Logical CPUs: 4
- RAM: 8 GB 1600 MHz DDR3

## Software
- OS: macOS 14.8.9 Sonoma
- Ollama: 0.34.4
- Backend: llama.cpp
- Inference device: CPU
- Server: 127.0.0.1:11434
- Offline mode: enabled

## Model
- Model: Qwen2.5-Coder 3B Instruct
- Quantization: Q4_K_M
- Parameters: ~3.09B
- Model size: ~1.79 GiB
- Training context 32K
- Runtime context: 4096

## Runtime
- Threads: 2
- Flash attention: enabled
- Prompt caching: enabled
- Thinking: disabled
- Sampling: enabled

## Initial measurements
- Generation: ~3.5-4 tok/s
- Prompt processing ~14-16 tok/s
- Long uncached prompt: ~2727 tokens / ~194 s
- KV/cache at 4096 tokens: ~144 MiB

# Experiment 1: CPU thread scaling

Question: 

What is the effect of CPU thread count on Qwen2.5-Coder 3B inference on the MacBookPro11,1?

Independent variable: 
- CPU threads: 1, 2, 4

Controlled variables:
- MOdel
- Quantization
- Prompt
- Runtime context
- Sampling parameters
- Ollama/llama.cpp version
- Hardware
- OS
- Flash attention
- Prompt-cache state

Primary measurements:
- Prompt processing tokens/sec
- Generation tokens/sec
- Total wall-clock time
- Peak/observed memory usage

Hypothesis:
- 2 threads will outperform 1.
- 4 threads may or may not outperform 2 because the CPU has only 2 physical cores.

Experiment 1 cache behavior

Ollama 0.34.4 reuses the prompt cache when the same prompt is sent repeatedly while the model remains loaded. An immediate repeat of a 36-token prompt reported 35 cached tokens. Unloading the model with keep_alive=0 and then issuing the prompt produced 0 cached tokens. 

Therefore prompt_eval_cached_count must be monitored explicitly in the benchmark. Cached and uncached prompt evaluation are materially different measurements. 

Experiment 1 protocol
Every observation loads the model, evaluates the identical benchmark prompt from an empty prompt cache, generates the response, and unloads the model. Prompt-processing and generation throughput are measured from Ollama's separate timing fields; model load time is recorded but excluded from those throughput measurements.

