

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


