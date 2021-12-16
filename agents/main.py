import os
import sys


import game
import glob

num_games = 1
model_paths = '/home/olof/Desktop/hanabi-hcai/agents/imitator_models/rainbow.save/best.h5'

print('in main')

agents = glob.glob(model_paths)
print(agents)

for agent0 in agents:
    print('in first for')
    print(agent0)
    for agent1 in agents:
        print('in second for')
        print(agent1)
        game.game(num_games, agent0, agent1).runGame()