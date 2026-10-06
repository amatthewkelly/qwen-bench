printf '\n--- git status ---\n':
git status --short

printf '\n--- experiment files ---\n'
find results/experiment-001-thread-scaling -maxdepth 2 -type f -print | sort

printf '\n--- benchmark prompt ---\n'
cat benchmark/prompt.txt

printf '\n--- runner syntax ---\n'
bash -n scripts/run_experiment_001.sh

printf '\n--- API version ---\n'
curl -s http://localhost:11434/api/version

printf '\n--- model ---\n'
ollama show qwen2.5-coder:3b | head -20
