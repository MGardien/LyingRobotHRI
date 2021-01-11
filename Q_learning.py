#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 20:34:42 2020

@author: Bram Pol s4815521
"""

# Q learning

#%% Define possible states

import itertools
import numpy as np

playermoves = ['p_rock', 'p_paper', 'p_scissors']
robotmoves =  ['r_rock', 'r_paper', 'r_scissors']
hints = ['lie', 'truth', 'silence']
onegame = [playermoves, robotmoves, hints]

firstgame = list(itertools.product(*onegame))
secondgame = list(itertools.product(*onegame))
bothgames = [firstgame, secondgame]

statespace = list(itertools.product(*bothgames))


#%% Reward calculation

# Reward function, 0 for tie, -1 for loss, 1 for win, might want to tune later
def rewardfunc(playermove, robotmove):
    if playermove == 'p_rock' and robotmove == 'r_rock':
        return 0
    if playermove == 'p_paper' and robotmove == 'r_paper':
        return 0
    if playermove == 'p_scissors' and robotmove == 'r_scissors':
        return 0
    
    if playermove == 'p_rock' and robotmove == 'r_paper':
        return 1
    if playermove == 'p_rock' and robotmove == 'r_scissors':
        return -1
    
    if playermove == 'p_paper' and robotmove == 'r_scissors':
        return 1
    if playermove == 'p_paper' and robotmove == 'r_rock':
        return -1

    if playermove == 'p_scissors' and robotmove == 'r_rock':
        return 1
    if playermove == 'p_scissors' and robotmove == 'r_paper':
        return -1
    
# Return the move that would have been the winning move considering the previous robot's choice
def trustHint(hint):
    # print('trusthint:', hint)
    if hint == 'r_rock':
        bestMove = 'p_paper'
        return bestMove
    if hint == 'r_paper':
        bestMove = 'p_scissors'
        return bestMove
    if hint == 'r_scissors':
        bestMove = 'p_rock'
        return bestMove
    else: 
        bestMove = random.choice(playermoves)
    return bestMove

def dontTrustHint(hint):
    # print('donthint:', hint)
    if hint == 'r_rock':
        bestMove = 'p_scissors'
        return bestMove
    if hint == 'r_paper':
        bestMove = 'p_rock'
        return bestMove
    if hint == 'r_scissors':
        bestMove = 'p_paper'
        return bestMove
    else: 
        bestMove = random.choice(playermoves)
    return bestMove

# Decide how the simulated player will choose an action based on the current state
def player_algorithm(state, hint, verbose=False):
    if verbose: 
        print(state)
    if 'lie' == state[0][2]:
        playermove = dontTrustHint(hint)
        if verbose:
            print('player doesn\'t trust')
        return playermove
    if 'truth' == state[0][2] and 'truth' == state[1][2]:
        playermove = trustHint(hint)
        if verbose:
            print('player trusts')
        return playermove
    if 'silence' == state[0][2]:
        playermove = trustHint('silence')
        if verbose:
            print('silence player random choice')
        return playermove
    else:
        playermove = trustHint('Nothing')
        if verbose:
            print('else condition, random choice')
        return playermove

def nextstatefunc(state, action):
    robotmove = extract_action(action)
    hint = extract_hint(action)
    playermove = player_algorithm(state, hint)

    reward = rewardfunc(playermove, robotmove)
    
    # First game in state tuple is most recent
    # Therefore first index old state becomes second index new state
    # And the current game becomes the first index of new state
    currentgame = (playermove, robotmove, hint)
    nextstate = (currentgame ,state[0])
    return nextstate, reward
      
def extract_action(action):
    return action[1]
    
def extract_hint(action):
    return action[0]

#%% Define action space
actionspace = list(itertools.product(*[hints, robotmoves]))

#%% Create the Q-matrix
qmatrix = np.zeros((len(statespace), len(actionspace)))

#%% Trainingloop
# Followed the tutorial and adapted to our situation, the link is also referenced in the report
# https://www.learndatasci.com/tutorials/reinforcement-q-learning-scratch-python-openai-gym/

import random
from IPython.display import clear_output

# Hyperparameters
alpha = 0.1
gamma = 0.6
epsilon = 0.4

# For plotting metrics
all_epochs = []
all_penalties = []


# Training loop 10000 rounds of sequences of 10 games.
for i in range(1, 10000):
    statenumber = random.randint(0,len(statespace)-1)
    
    state = statespace[statenumber]
    actionnumber = 0

    epochs, reward, = 0, 0
    done = False
    
    while epochs < 10:
        # About epsilon of cases a random action is explored
        if random.uniform(0, 1) < epsilon:
            actionnumber = random.randint(0,len(actionspace)-1)
            action = actionspace[actionnumber]
        # Otherwise action with the highest q-value in the qmatrix for the current state is chosen
        else:         
            actionnumber = np.argmax(qmatrix[statenumber])
            action = actionspace[np.argmax(qmatrix[statenumber])] # Exploit learned values

        # Generation of next state and reward calculation
        next_state, reward = nextstatefunc(state, action)        
        
        old_value = qmatrix[statenumber, actionnumber]
        
        next_index = statespace.index(next_state)
        next_max = np.max(qmatrix[next_index])

        # Update formula of the current q-value
        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        
        # Assign value to qmatrix
        qmatrix[statenumber, actionnumber] = new_value

        state = next_state
        epochs += 1
        
    if i % 100 == 0:
        clear_output(wait=True)
        print(f"Episode: {i}")

print("Training finished.\n")


#%% Hint and lie to action

def hint_and_lie_to_action(hint):
    if hint == 'r_rock':
        action = 'r_scissors'
    if hint == 'r_paper':
        action = 'r_rock'
    if hint == 'r_scissors':
        action = 'r_paper'
    return action

def getIndicationAndActionFromState(state):
    indication = actionspace[np.argmax(qmatrix[statespace.index(startingstate)])][0]
    actionspace[np.argmax(qmatrix[statespace.index(startingstate)])][1]
    return indication, action


#%% Playing simulation to test the trained qmatrix's effectiveness
totalreward = 0
wincount = 0
losecount = 0
tiecount = 0

# Random startingstate from the statespace
startingstate = statespace[random.randint(0,len(statespace)-1)]

for i in range(0, 1000):

    # Look up the best action for the robot from the Qmatrix that statespace
    indication = actionspace[np.argmax(qmatrix[statespace.index(startingstate)])][0]
    bestOption = actionspace[np.argmax(qmatrix[statespace.index(startingstate)])][1]
    
    if indication == 'lie':
        hint = hint_and_lie_to_action(bestOption)
    if indication == 'truth':
        hint = bestOption
    if indication == 'silence':
        hint = 'silence'
        
    # Determine what the simulated player will do based on the startingstate
    playermove = player_algorithm(startingstate, hint, verbose=False)

    verbose = False
    
    if verbose:
        print('hint', hint)
        print('indication', indication)
        print('playermove', playermove)
        print('robotmove', bestOption)
    
    if rewardfunc(playermove, bestOption) == 1:
        wincount+=1
    if rewardfunc(playermove, bestOption) == -1:
        losecount+=1
    if rewardfunc(playermove, bestOption) == 0:
        tiecount+=1
        
    currentgame = (playermove, bestOption, indication)

    startingstate = (currentgame, startingstate[0])
        
    totalreward = totalreward+rewardfunc(playermove, bestOption)
    
print('win: ', wincount, ', lose: ', losecount, ', tie: ', tiecount)

#%% Save to file

file = open("qmatrix", "wb")
np.save(file, qmatrix)
file.close

#%% Open file
file2 = open("qmatrix", "rb")
qmatrix2 = np.load(file2)




















