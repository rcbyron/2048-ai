# 2048 Artificial Intelligence

![2048-ai](client/assets/banner.png?raw=true "2048 ai")

Artificial intelligence used to solve the popular game "2048"

Currently achieves 2048 tile about 10% to 20% of the time.

This project is still a work-in-progress.

### Heuristics:
- monotonicity of rows/columns
- number of adjacent tiles
- number of empty tiles
- loss penalty

### Algorithm:
- Recursively simulate all moves (up/down/right/left) for around 3 to 5 turns
- Pick the depth 0 move with the highest score tree
