# # Solving the pay for prediction challenge
# 
# This document is a collaboratively developed IPython Notebook to solve the ["Pay for prediction" challenge][PFPC].
# 
# ###### Hit Esc to see an overview of the pages
# 
# [PFPC]: http://www.climatecentre.org/site/paying-for-predictions

# ## Outline
# 
# - Overview of the challenge
# - The simulator
# - The solutions

# ### Overview
# 
# [from the competition website]
# 
# #### Strategy competition
# 
# What is the best strategy to reduce the risk of disaster as a humanitarian worker? Red Cross Red Crescent workers must balance their time and resources between long-term programming such as hygiene promotion, preparing right before a disaster happens, and responding to disasters when they happen. Fortunately, there are many tools to help with this, including science-based forecasts that can help people anticipate a disaster. While forecasts can be confusing, making a strategy for how to act based on a forecast can help humanitarian workers best manage their time and resources.
#  
# The Red Cross Red Crescent Climate Centre is launching a competition to find the best strategy for how to manage disaster risk in the game Paying for Predictions. This game demonstrates the many responsibilities of a humanitarian worker, from long-term preparedness to short-term anticipation of a disaster. In this global competition, we would like you to submit a strategy which you think will make a player win this game more often than other strategies.
# 
# 

# #### How does this work?
# 
# You submit your strategy by Thursday, February 28th, 2013.
# 
# A computer programme will use your strategy as if you were a person playing this game against other people over and over again. After many games are played, the programme will show which strategy wins most often.
# 
# We will announce the winners in March 2013. 

# #### Competition rules
# 
# [Origin of the rules](http://www.climatecentre.org/downloads/File/Games/Competition%20Rules.pdf)
# 
# Game License: http://creativecommons.org/licenses/by-nc/3.0/
# 
# The basic parameters of how the game will be simulated by computers for this competition:
# 
# - 10 teams of 3 people are playing this game (30 people total)
# - Players are unable to communicate with each other, but they are able to see what other players 
# on their team are doing. They are not able to see what players are doing who are not on their 
# team.
# - There are 10 rounds in this game.

# #### Game setup
# 
# Each player receives 10 beans (resources), and one 
# six-sided die which represent the local rainfall of his/her area. 
# Each team receives a cup and one six-sided die which represents 
# the regional rainfall of their zone.
# 
# #### WINNING
# 
# - The individual WINNER is the person with the most beans.
# - The team WINNER is the team with fewest total  humanitarian crises. If there is a tie the team with most total beans combined is the team winner.
# 

# ### Simulator
# 
# The simulator is setup with some default strategies. These are for illustrative purposes.

# In[1]:
import numpy as np

n_teams = 10
n_persons_per_team = 3
n_beans = 10
n_rounds = 10
n_die_change = 7
target_rain = 10
penalty = 4

def initialize():
    beans = n_beans * np.ones((n_teams, n_persons_per_team))
    forecast_teams = np.ones((n_teams)) # receive regional forecast
    drr_teams = np.ones((n_teams))  # have disaster risk reduction
    return beans, forecast_teams, drr_teams

# In[2]:
def get_forecast_bids(beans):
    """ Defines how each person or team will bid for regional forecast

    Example
    -------

    return np.random.randint(0, np.max(beans) * .4, size=beans.shape)
    """
    return np.ones(beans.shape)

def get_drr_bids(beans):
    """ Defines how each person or team will bid for disaster risk reduction

    Example
    -------

    bids = np.zeros(beans.shape)
    for i in range(beans.shape[0]):
        for j in range(beans.shape[1]):
            bids[i, j] = np.random.randint(0, beans[i, j] * .2)
    """
    bids = np.ones(beans.shape)
    return bids


# ##### Gameplay: Stage 1 perform bids

# In[3]:
beans, forecast_teams, drr_teams = initialize()

# perform forecast bids
forecast_bids = get_forecast_bids(beans)
forecast_team_bids = np.sum(forecast_bids, axis=1)
sort_index = np.argsort(forecast_team_bids)
forecast_teams[sort_index[:n_teams/2]] = 0

# Winning teams pay their beans
beans = beans - (forecast_teams[:, None] * forecast_bids)
print beans.T
print forecast_teams

# Out[3]:
#     [[ 10.  10.  10.  10.  10.   9.   9.   9.   9.   9.]
#      [ 10.  10.  10.  10.  10.   9.   9.   9.   9.   9.]
#      [ 10.  10.  10.  10.  10.   9.   9.   9.   9.   9.]]
#     [ 0.  0.  0.  0.  0.  1.  1.  1.  1.  1.]
# 
# In[4]:
# perform drr bids
drr_bids = get_drr_bids(beans)
drr_team_bids = np.sum(drr_bids, axis=1)
sort_index = np.argsort(drr_team_bids)
drr_teams[sort_index[:-2]] = 0

# Winning teams pay their beans
beans = beans - (drr_teams[:, None] * drr_bids)
print beans.T
print forecast_teams
print drr_teams

# Out[4]:
#     [[ 10.  10.  10.  10.  10.   9.   9.   9.   8.   8.]
#      [ 10.  10.  10.  10.  10.   9.   9.   9.   8.   8.]
#      [ 10.  10.  10.  10.  10.   9.   9.   9.   8.   8.]]
#     [ 0.  0.  0.  0.  0.  1.  1.  1.  1.  1.]
#     [ 0.  0.  0.  0.  0.  0.  0.  0.  1.  1.]
# 
# #### Round

# In[5]:
def get_insurance_payments(regional_predictions, drr_teams, beans, round_idx):
    # determine the likelihood of a flood
    likelihood = (7 - (target_rain - regional_predictions)) / 6
    # if likelihood > .2 pay, or if you didn't have a prediction pay one bean
    payments = ((likelihood > .2) + (regional_predictions < 1))[:, None] * np.ones(beans.shape)
    return (payments * (beans > 0)).astype(int)

# In[6]:
def generate_rainfall(n_sides):
    regional_rainfall = np.random.randint(1, n_sides, size=(n_teams))
    local_rainfall = np.random.randint(1, 7, size=(n_teams, n_persons_per_team))
    total_rainfall = local_rainfall + regional_rainfall[:, None]
    flooded = (total_rainfall >= target_rain).astype(np.int)
    return regional_rainfall, flooded

def adjust_beans(beans, payments, flooded, round_idx, drr_teams):
    if round_idx < 3:
        drr_penalty = 4
    else:
        drr_penalty = 2
    penalized = np.maximum(flooded - payments, 0)
    beans_to_remove = drr_penalty * penalized * (drr_teams[:, None] == 1) + penalty * penalized * (drr_teams[:, None] == 0)
    already_in_crisis = beans * (beans < 0)
    beans[already_in_crisis < 0] = 0
    beans = beans - payments - beans_to_remove
    beans_joining_crisis = beans < 0 
    beans = beans * (beans > 0)
    in_crisis = already_in_crisis - beans_joining_crisis
    return beans + in_crisis

# #### Simulate

# In[7]:
print beans.T
for turn in range(n_rounds):
    n_sides = 6
    if turn == 6: # 7th round
        n_sides = 8
    regional_rainfall, flooded = generate_rainfall(n_sides=n_sides)
    payments = get_insurance_payments(regional_rainfall * forecast_teams, drr_teams, beans, turn + 1)
    beans = adjust_beans(beans.copy(), payments, flooded, turn + 1, drr_teams)
    if turn % 2 == 0:
        print turn + 1, flooded.T - payments.T
print beans.T

# Out[7]:
#     [[ 10.  10.  10.  10.  10.   9.   9.   9.   8.   8.]
#      [ 10.  10.  10.  10.  10.   9.   9.   9.   8.   8.]
#      [ 10.  10.  10.  10.  10.   9.   9.   9.   8.   8.]]
#     1 [[-1 -1 -1  0 -1  0  0  0  0  0]
#      [-1 -1 -1  0 -1  0  0  0 -1  0]
#      [-1 -1  0 -1 -1  0  0  0 -1  0]]
#     3 [[-1 -1 -1  0 -1  0 -1  0  0  0]
#      [-1 -1 -1  0 -1  0 -1  0  0  0]
#      [-1  0 -1  0 -1  0 -1  0  0  0]]
#     5 [[-1 -1 -1 -1  0  0  0  0  0 -1]
#      [-1 -1 -1  0  0  0 -1  0  0 -1]
#      [-1 -1 -1 -1 -1  0  0  0  1  0]]
#     7 [[-1 -1 -1  0 -1  0  0  0 -1  0]
#      [-1 -1 -1  0 -1  0  0  0  0  1]
#      [-1 -1 -1  0  0  0  0  0 -1  0]]
#     9 [[-1 -1  0 -1  0  0  0  0  0  0]
#      [-1 -1 -1 -1 -1  0  0  0  0  0]
#      [-1 -1  0 -1 -1  0  0  0  0  0]]
#     [[ 0.  0.  0.  0.  0.  8.  2.  7.  3.  5.]
#      [ 0.  0.  0.  0.  0.  4.  2.  7.  5.  3.]
#      [ 0.  0.  0.  0.  0.  8.  2.  7.  3.  5.]]
# 
# ### Solutions
# 
# Example from challenge guidelines
# 
#     # This is a complete example submission for the "Paying for Predictions" game.
#     # Blank lines or lines beginning with "#" are ignored.
#     # Bids:
#     Bid 1 for the forecast.
#     Bid 3 beans for DRR.
#     # Conditions:
#     If I won the forecast and the dice is less than 5 and the beans remaining are more than 7, then take 
#     early action.
#     If I have forecast and the dice rolls more than the number of rounds remaining, then take early 
#     action.
#     If I don't have DRR and the dice rolls more than 5 and the rounds played are more than 6, then take 
#     early action.
#     Else, take no early action.
# 

# #### Solution from the strategies chosen for the simulation
# 
#     # This is a complete example submission for the "Paying for Predictions" game.
#     # Blank lines or lines beginning with "#" are ignored.
#     # Bids:
#     Bid 1 for the forecast.
#     Bid 1 beans for DRR.
#     # Conditions:
#     If I have forecast and the rolled dice is more than 4 then take early action.
#     If I don't have forecast then take early action.
#     By default take no action.
# 

# In[8]:
!/software/challenges/nbconvert/nbconvert.py -f reveal /software/challenges/payforpredictions/payforpredictions.ipynb
