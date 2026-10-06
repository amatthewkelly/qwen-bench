# Experiment 001: CPU Thread Scaling

## Question

How does CPU thread count affect prompt-processing throughput and generation for !wen2.5-Coder 3B on the MacBookPro11,1?

## Hypothesis

I hypothesize that increasing the thread count from 1 to 2 will deliver a detectable performance increase. Increasing from 2 to 4 may or may not provide any improvement because the cores are logical rather than physical.

## System Configuration

- Machine: MacBookPro11,1
- CPU: Intel Core i5-4258U @ 2.40 GHz
- CPU topology: 2 physical cores / 4 logical CPUs
- Memory: 8 GB
- Inference runtime: Ollama 0.34.4
- Model: qwen2.5-coder:3b
- Quantization: Q4_K_M
- Model size: approximately 3.1B parameters
- Runtime context length: 4096 tokens
- Inference device: CPU

## Method

The independent variable was CPU thread count, tested at 1, 2, and 4 threads.
Five observations were collected for each condition, for 15 formal runs total.

All runs used the same model, quantization, benchmark prompt, context length,
sampling configuration, hardware, and Ollama version.

Each observation used a cold prompt cache. The model was loaded for the run,
the benchmark prompt was evaluated and a response generated, and the model was
then unloaded using `keep_alive=0`. A run was considered cache-valid only when
Ollama reported `prompt_eval_cached_count == 0`.

Run IDs were organized as:

- `t1-r01` through `t1-r05`
- `t2-r01` through `t2-r05`
- `t4-r01` through `t4-r05`

For each observation, the harness recorded:

- prompt token count
- cached prompt token count
- prompt evaluation duration
- generated token count
- generation duration
- model load duration
- total duration
- cache validity

The complete Ollama response was also preserved for each observation in the
`raw/` directory.

Prompt-processing throughput was calculated as:

`prompt_eval_count / prompt_eval_duration_seconds`

Generation throughput was calculated as:

`eval_count / eval_duration_seconds`

## Results

All 15 formal observations passed the data-integrity checks. Each condition
contained five runs, all runs used an empty prompt cache, and the compact
records matched the preserved raw observations.

### Prompt-processing throughput

| Threads | Mean tok/s | Median tok/s | SD | Range |
|---:|---:|---:|---:|---:|
| 1 | 8.14 | 9.29 | 2.00 | 5.83–10.00 |
| 2 | 11.17 | 10.73 | 1.33 | 9.46–12.70 |
| 4 | 12.44 | 13.55 | 2.93 | 7.22–14.29 |

### Generation throughput

| Threads | Mean tok/s | Median tok/s | SD | Range |
|---:|---:|---:|---:|---:|
| 1 | 3.40 | 3.65 | 0.58 | 2.52–3.89 |
| 2 | 4.66 | 4.58 | 0.34 | 4.21–5.11 |
| 4 | 3.88 | 4.52 | 1.08 | 2.63–4.83 |

Moving from 1 to 2 threads increased mean prompt-processing throughput by
approximately 37% and mean generation throughput by approximately 37%.

Moving from 2 to 4 threads increased mean prompt-processing throughput by
approximately 11%, but decreased mean generation throughput by approximately
17%.

## Interpretation

Two threads provided the best generation performance and the most consistent generation throughput in this experiment. Compared with one thread, two threads susbstantially improved both prompt-processing and generation throughput. 

Four threads behaved differently across the two phases of inference. Typical prompt-processing throughput improved beyond the two-thread condition, but generation throughput did not. Mean generation throughput decreased, while run-to-run variability increased substantially. 

This behavior is consistent with the CPU topology of the test machine. Moving from one to two inference threads allows work to use both physical CPU cores, whereas moving from two to four threads primarily adds simultaneous multithreading on those same cores. This experiment does not establish this as the cause of the observed scaling behavior. 

For subsequent experiments on this mahine, two threads will be used as the default inference configuration unless thread count is itself the variable under investigation.

## Limitations

Each condition contained only five observations. This is sufficient for an
exploratory benchmark but limits confidence in the precise magnitude of the
observed differences.

The thread-count conditions were executed sequentially rather than randomized
or interleaved. Run order is therefore confounded with thread count. Changes
in machine state over the duration of the experiment could have influenced
the results.

CPU temperature, clock frequency, power consumption, memory pressure, and
background system load were not recorded. The experiment therefore cannot
determine the cause of the relatively large run-to-run variation observed in
some conditions, particularly at four threads.

Generated response length varied between runs. Generation throughput
normalizes for this variation, but total wall-clock duration should not be
compared directly between runs as a pure measure of inference performance.

The results apply specifically to this model, quantization, runtime
configuration, Ollama version, and hardware. They should not be generalized
to other models or systems without additional measurements.

## Artifacts

- `runs.jsonl` — compact measurement records
- `raw/` — complete per-run observations and raw Ollama responses
- `../../scripts/run_experiment_001.sh` — experiment runner
- `../../scripts/run_inference.py` — inference and measurement harness
- `../../benchmark/prompt.txt` — benchmark prompt
