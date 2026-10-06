# Benchmark Specification

## Experiment 1: CPU Thread Scaling

### Objective

Measure the effect of CPU thread count on Qwen2.5-Coder 3B inference. 

### Configurations

- 1 thread
- 2 threads
- 4 threads

### Workload

The workload is intentionally simple so that the experiment measures inference performance rather than task-solving ability.

'''
Write a Python function named 'count_lines' that accepts a string and returns the number of newline-separated lines in the string. 

Requirements:
- The empty string has 0 lines.
- A string with no newline has 1 line. 
- Count every newline character.
- Do not print anything. 
- Return an integer. 
- Include a short docstring. 
- Output only the Python code. 
'''

### Measurements
We will use a fixed maximum output budget and record the actual generated token count. 

- prompt processing tokens/sec
- generation tokens/sec
- total elapsed time
- memory usage

Instead of averaging away the raw obserations we want:
thread_count,run,prompt_tokens,prompt_tok_s,output_tokens,generation_tok_s,elapsed_s

### Repetitions

Each thread configuration is run 5 times.

Configurations:
- 1 thread x 5
- 2 threads x 5
- 4 threads x 5

### Cache

This experiment measures fresh-context inference. Prompt-cache effects are tested separately. 

### Comparison

Compare thread configurations while keeping all other variables constant.

