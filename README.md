# 2048 Artificial Intelligence

![2048-ai](client/assets/banner.png?raw=true "2048 ai")

Artificial intelligence used to solve the popular game "2048"

Currently achieves 2048 tile about 10% to 20% of the time.

This project is still a work-in-progress.

## Project
| File          | Description                                                                                |
| ------------- | ------------------------------------------------------------------------------------------ |
| `game.py`     | provides a native OpenGL interface for playing 2048 normally (with arrow keys)             |
| `ai.py`       | contains intelligent decision logic from quickly simulating 2048 moves & outcomes          |
| `training.py` | runs the AI with quick non-graphical simulations for testing & hyperparameter optimization |

### Heuristics
- monotonicity of rows/columns
- number of adjacent tiles
- number of empty tiles
- loss penalty

### Algorithm
- Recursively simulate all moves (up/down/right/left) for around 3 to 5 turns
- Pick the depth 0 move with the highest score tree

### Install Dependencies
Currently the only dependency: `pip install pyglet`

### Run
- To play the game normally, run `python game.py`
- To test the AI, run `python training.py`
