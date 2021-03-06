import random
import math
import os

import numpy as np
import pandas as pd

from collections import deque

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

## import tags, which equate to 
## labels for unit names, and thier 
## ids didn't want to have all those
## assignments in the bot file
#from tags import *

## given two arrays of coords returns number of pixels per unit.
from countUnits import count_units

from pysc2.lib import actions
from pysc2.lib import features

_NOT_QUEUED = [0]
_QUEUED = [1]
_SELECT_ALL = [2]

_PLAYER_SELF = 1
_PLAYER_HOSTILE = 4
_ARMY_SUPPLY = 5

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index
_PLAYER_ID = features.SCREEN_FEATURES.player_id.index

_BUILD_ARMORY = actions.FUNCTIONS.Build_Armory_screen.id
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_BUILD_COMMAND_CENTER = actions.FUNCTIONS.Build_CommandCenter_screen.id
_BUILD_ENGINEERING_BAY = actions.FUNCTIONS.Build_EngineeringBay_screen.id
_BUILD_FACTORY = actions.FUNCTIONS.Build_Factory_screen.id
_BUILD_FUSION_CORE = actions.FUNCTIONS.Build_FusionCore_screen.id
_BUILD_GHOST_ACADEMY = actions.FUNCTIONS.Build_GhostAcademy_screen.id
_BUILD_REFINERY = actions.FUNCTIONS.Build_Refinery_screen.id
_BUILD_STARPORT = actions.FUNCTIONS.Build_Starport_screen.id
_BUILD_SUPPLY_DEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
## techlab is an add-on to barracks, factory, or starport
## used to create (marauders, ghosts), (Seige Tanks, Thors),
## (Ravens, banshees, and battlecruisers) respectively
## figuring out which to add on to is key... (not sure whether to use screen or quick)
_BUILD_TECHLAB = actions.FUNCTIONS.Build_TechLab_screen.id
_BUILD_TECHLAB_BARRACKS = actions.FUNCTIONS.Build_TechLab_Barracks_quick.id
_BUILD_TECHLAB_FACTORY = actions.FUNCTIONS.Build_TechLab_Factory_quick.id
_BUILD_TECHLAB_STARPORT = actions.FUNCTIONS.Build_TechLab_Starport_quick.id
## same idea as a techlab 
_BUILD_REACTOR = actions.FUNCTIONS.Build_Reactor_screen.id
_BUILD_REACTOR_BARRACKS = actions.FUNCTIONS.Build_Reactor_Barracks_quick.id
_BUILD_REACTOR_FACTORY = actions.FUNCTIONS.Build_Reactor_Factory_quick.id
_BUILD_REACTOR_STARPORT = actions.FUNCTIONS.Build_Reactor_Starport_quick.id

_TRAIN_BANSHEE = actions.FUNCTIONS.Train_Banshee_quick.id
_TRAIN_BATTLE_CRUISER = actions.FUNCTIONS.Train_Battlecruiser_quick.id
_TRAIN_CYCLONE = actions.FUNCTIONS.Train_Cyclone_quick.id
_TRAIN_GHOST = actions.FUNCTIONS.Train_Ghost_quick.id
_TRAIN_HELLION = actions.FUNCTIONS.Train_Hellion_quick.id
_TRAIN_LIBERATOR = actions.FUNCTIONS.Train_Liberator_quick.id
_TRAIN_MARAUDER = actions.FUNCTIONS.Train_Marauder_quick.id
_TRAIN_MARINE = actions.FUNCTIONS.Train_Marine_quick.id
_TRAIN_MEDIVAC = actions.FUNCTIONS.Train_Medivac_quick.id
_TRAIN_RAVEN = actions.FUNCTIONS.Train_Raven_quick.id
_TRAIN_REAPER = actions.FUNCTIONS.Train_Reaper_quick.id
_TRAIN_SCV = actions.FUNCTIONS.Train_SCV_quick.id
_TRAIN_SIEGE_TANK = actions.FUNCTIONS.Train_SiegeTank_quick.id
_TRAIN_VIKING = actions.FUNCTIONS.Train_VikingFighter_quick.id
_TRAIN_THOR = actions.FUNCTIONS.Train_Thor_quick.id

_NO_OP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id
_HARVEST_GATHER = actions.FUNCTIONS.Harvest_Gather_screen.id

_NEUTRAL_VESPENE_GEYSER = 342
_NEUTRAL_MINERAL_FIELD = 341

_ARMORY = 29
_BARRACKS = 21
_FACTORY = 27
_FUSION_CORE = 30
_GHOST_ACADEMY = 26
_STARPORT = 28
_COMMAND_CENTER = 18
_ENGINEERING_BAY = 22
_REFINERY = 20
_SUPPLY_DEPOT = 19
_TECHLAB = 5
_BANSHEE = 55
_BATTLE_CRUISER = 57
_CYCLONE = 692
_GHOST = 50
_HELLION = 53
_LIBERATOR = 689
_MARAUDER = 51
_MARINE = 48
_MEDIVAC = 54
_RAVEN = 56
_REAPER = 49
_SIEGE_TANK = 33
_THOR = 52
## viking can transform to
## ASSAULT mode (34)
_VIKING = 35
_SCV = 45
_REACTOR = 6

## there seems to be a bug with pysc2
## where building reactors and techlabs
## to specific buildings is not available
## must check how to build these units in
## the desired building. Might fist implement
## something like selecting the building first
## then make the general build command for each
_REACTOR_BARRACKS = 38
_REACTOR_FACTORY = 40
_REACTOR_STARPORT = 42
_TECHLAB_BARRACKS = 37
_TECHLAB_FACTORY = 39
_TECHLAB_STARPORT = 41

DATA_FILE = 'refined_agent_data'

ACTION_DO_NOTHING = 'donothing'
ACTION_ATTACK = 'attack'
ACTION_RETREAT = 'retreat'

ACTION_T_BANSHEE = 't_banshee'
ACTION_T_BATTLECRUISER = 't_battlecruiser'
ACTION_T_CYCLONE = 't_cyclone'
ACTION_T_GHOST = 't_ghost'
ACTION_T_HELLION = 't_hellion'
ACTION_T_LIBERATOR = 't_liberator'
ACTION_T_MARAUDER = 't_marauder'
ACTION_T_MARINE = 't_marine'
ACTION_T_MEDIVAC = 't_medivac'
ACTION_T_RAVEN = 't_raven'
ACTION_T_REAPER = 't_reaper'
ACTION_T_SIEGETANK = 't_siegetank'
ACTION_T_SCV = 't_scv'
ACTION_T_VIKING = 't_viking'
ACTION_T_THOR = 't_thor'

ACTION_B_ARMORY = 'b_armory'
ACTION_B_BARRACKS = 'b_barracks'
ACTION_B_COMMANDCENTER = 'b_commandcenter'
ACTION_B_ENGINEERINGBAY = 'b_engineeringbay'
ACTION_B_FACTORY = 'b_factory'
ACTION_B_FUSIONCORE ='b_fusioncore'
ACTION_B_GHOSTACADEMY = 'b_ghostacademy'
ACTION_B_REFINERY = 'b_refinery'
ACTION_B_STARPORT = 'b_starport'
ACTION_B_SUPPLYDEPOT = 'b_supplydepot'
ACTION_B_TECHLAB_BARRACKS = 'b_techlab_barracks'
ACTION_B_TECHLAB_STARPORT = 'b_techlab_starport'
ACTION_B_TECHLAB_FACTORY = 'b_techlab_factory'
ACTION_B_REACTOR_BARRACKS = 'b_reactor_barracks'
ACTION_B_REACTOR_STARPORT = 'b_reactor_starport'
ACTION_B_REACTOR_FACTORY = 'b_reactor_factory'

units_capable_of_attacking = [
	'banshee',		'battlecruiser',
	'cyclone',		'ghost',
	'hellion',		'liberator',
	'marauder',		'marine',
	'medivac',		'raven',
	'reaper', 		'siegetank',
	'scv',	'viking',	'thor'
]


unit_dict = {
	'banshee': _BANSHEE,
	'battlecruiser': _BATTLE_CRUISER,
	'cyclone': _CYCLONE,
	'ghost': _GHOST,
	'hellion': _HELLION,
	'liberator': _LIBERATOR,
	'marauder': _MARAUDER,
	'marine': _MARINE,
	'medivac': _MEDIVAC,
	'raven': _RAVEN,
	'reaper': _REAPER,
	'siegetank': _SIEGE_TANK,
	'scv': _SCV,
	'viking': _VIKING,
	'thor': _THOR,
	'techlab': _TECHLAB,
	'supplydepot': _SUPPLY_DEPOT, 
	'starport': _STARPORT,
	'refinery': _REFINERY,
	'ghostacademy': _GHOST_ACADEMY,
	'fusioncore': _FUSION_CORE,
	'factory': _FACTORY,
	'engineeringbay': _ENGINEERING_BAY,
	'commandcenter': _COMMAND_CENTER,
	'barracks': _BARRACKS,
	'armory': _ARMORY,
	'reactor': _REACTOR
}

build_to_action = {'barracks':_BUILD_BARRACKS, 'supplydepot':_BUILD_SUPPLY_DEPOT, 'commandcenter':_BUILD_COMMAND_CENTER, 'refinery':_REFINERY,
				'ghostacademy':_BUILD_GHOST_ACADEMY, 'factory':_BUILD_FACTORY, 'armory':_BUILD_ARMORY, 'starport':_BUILD_STARPORT, 
				'fusioncore':_BUILD_FUSION_CORE, 'techlab': _BUILD_TECHLAB, 'reactor':_BUILD_REACTOR}

unit_to_action = {'banshee':_TRAIN_BANSHEE,
'battlecruiser':_TRAIN_BATTLE_CRUISER,
'cyclone':_TRAIN_CYCLONE,
'ghost':_TRAIN_GHOST,
'hellion':_TRAIN_HELLION,
'liberator':_TRAIN_LIBERATOR,
'marauder':_TRAIN_MARAUDER,
'marine':_TRAIN_MARINE,
'medivac':_TRAIN_MEDIVAC,
'raven':_TRAIN_RAVEN,
'reaper':_TRAIN_REAPER,
'scv':_TRAIN_SCV,
'siegetank':_TRAIN_SIEGE_TANK,
'viking':_TRAIN_VIKING,
'thor':_TRAIN_THOR
}

build_with_SCV = ['barracks', 'supplydepot', 'commandcenter', 'refinery',
				'ghostacademy', 'factory', 'armory', 'starport', 'fusioncore']

starport_units = ['banshee', 'battlecruiser', 'liberator', 'medivac', 'raven', 'viking']

barracks_units = ['ghost', 'marauder', 'marine', 'reaper']

factory_units = ['cyclone', 'hellion', 'siegetank', 'thor']

Buildings = [_BARRACKS, _ARMORY, _REACTOR, _COMMAND_CENTER, _ENGINEERING_BAY, _FACTORY,
			_FUSION_CORE, _GHOST_ACADEMY, _REFINERY, _STARPORT, _SUPPLY_DEPOT, _TECHLAB, 
			_NEUTRAL_MINERAL_FIELD, _NEUTRAL_VESPENE_GEYSER]

smart_actions = [	
	ACTION_DO_NOTHING, 			ACTION_T_BANSHEE,			ACTION_RETREAT,
	ACTION_T_BATTLECRUISER, 	ACTION_T_CYCLONE, 			ACTION_T_GHOST,
	ACTION_T_HELLION, 			ACTION_T_LIBERATOR, 		ACTION_T_MARAUDER,
	ACTION_T_MARINE, 			ACTION_T_MEDIVAC,			ACTION_T_RAVEN,
	ACTION_T_REAPER,			ACTION_T_SIEGETANK, 		ACTION_T_SCV,
	ACTION_T_VIKING,			ACTION_T_THOR,				ACTION_B_ARMORY,
	ACTION_B_BARRACKS,			ACTION_B_COMMANDCENTER,		ACTION_B_ENGINEERINGBAY,
	ACTION_B_FACTORY,			ACTION_B_GHOSTACADEMY,		
	ACTION_B_REFINERY,			ACTION_B_STARPORT,			ACTION_B_SUPPLYDEPOT,
	ACTION_B_TECHLAB_FACTORY, 	ACTION_B_TECHLAB_STARPORT, 	ACTION_B_TECHLAB_BARRACKS,
	ACTION_B_REACTOR_FACTORY, 	ACTION_B_REACTOR_STARPORT, 	ACTION_B_REACTOR_BARRACKS
]

## adds attack <which> quadrant actions and with <which> attacking unit
for mm_x in range(0, 64):
	for mm_y in range(0, 64):
		##for u in units_capable_of_attacking:
		##	if (mm_x + 1) % 32 == 0 and (mm_y + 1) % 32 == 0:
		##		smart_actions.append(ACTION_ATTACK + '_' + str(mm_x - 16) + '_' + str(mm_y - 16) + u)
		if (mm_x + 1) % 32 == 0 and (mm_y + 1) % 32 == 0:
			smart_actions.append(ACTION_ATTACK + '_' + str(mm_x - 16) + '_' + str(mm_y - 16))

class QLearningTable:
	def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
		self.round = 0
		self.actions = actions
		self.lr = learning_rate
		self.gamma = reward_decay
		self.epsilon = e_greedy
		self.q_table = pd.DataFrame(columns=self.actions)
		
		
		accum = open("acc_qtable.csv", "w+")
		name = "qtable.csv"
		if os.path.exists(name):
			self.q_table = pd.DataFrame(columns=self.actions).from_csv(name)
			#self.printTable()
		else:
			self.q_table = pd.DataFrame(columns=self.actions)


	def save_csv(self, name):
		self.round += 1
		self.q_table.to_csv(name)
		print("Saving")
		accum_f = open("acc_qtable.csv", "w")
		accum_f.write(str(self.q_table)+"\n")
		accum_f.write("Round: "+str(self.round)+"\n")



	def choose_action(self, observation):
		self.check_state_exist(observation)
		
		if np.random.uniform() < self.epsilon:
			# choose best action
			state_action = self.q_table.ix[observation, :]
			
			# some actions have the same value
			state_action = state_action.reindex(np.random.permutation(state_action.index))
			
			action = state_action.max()
		else:
			# choose random action
			action = np.random.choice(self.actions)
		return int(action)

	def printTable(self):
		print(self.q_table)
		
	def learn(self, s, a, r, s_):
		self.check_state_exist(s_)
		self.check_state_exist(s)

		q_predict = self.q_table.ix[s, a]
		#q_target = r + self.gamma * self.q_table.ix[s_, :].max()
		
		# update
		#self.q_table.ix[s, a] += self.lr * (q_target - q_predict)
		if s_ != 'terminal':
			q_target = r + self.gamma * self.q_table.ix[s_, :].max()
		else:
			q_target = r
		
		## update 
		self.q_table.ix[s, a] += self.lr * (q_target - q_predict)

	def check_state_exist(self, state):
		if state not in self.q_table.index:
			# append new state to q table

			self.q_table = self.q_table.append(pd.Series([0] * len(self.actions), index=self.q_table.columns, name=state))
			

"""
	Main Agent Class:
		This bot specifically focuses on build order prediction. From a Qtable it will obtain 
		the action with most probability to be done at a given state in the game. Currently, we are
		trying to implement the build order for mobile, air, and ground units. (this including buildings,
		workers, and attacking units). We hard-code the actions but the agent chooses what action to take
		at each given state. Our first approach is simply to get the bot running using the qtable alone. 
		as inplemented by: 
			https://github.com/skjb/pysc2-tutorial/blob/master/Refining%20the%20Sparse%20Reward%20Agent/refined_agent.py
		The code implements certain aspects of the agent differently from the one by 'skjb'. but not a huge difference. Just 
		a broader application for more actions, also facilitates the addition of newer actions to th smart actions array.  
		The second part after the Qtable implementation is completed is to use the current states that we had been passing 
		to the Qtable as indexes as actual inputs to a Recurrent Neural Network, so that the agent can learn from a sequence
		of moves that it has done throughout periods of or the entirety of the game. The current state is being defined by
		unit counts and global state evealuation of economy at the moment, we are also thinking of adding enemy info when 
		visible, in order to learn better and adapt to enemy strategies.
"""
class SwarmbotAgent(base_agent.BaseAgent):
	def __init__(self):
		super(SwarmbotAgent, self).__init__()
		self.round = 0 ## round number (games)
		self.rewardFile = open('rewards.csv', 'a+')
		self.rewardTotal = 0 # uhm... a reward win or loss, [1, 0]
		self.qlearn = QLearningTable(actions=list(range(len(smart_actions))))
		self.move_number = 0 ## what move in the smart action are we on
		self.unit_sizes = {} ## pixel sizes of each unit used to compute counts
		self.unit_coords = {} ## (x, y) coordinates for locating units
		self.unit_counts = {} ## counts of every unit , for state evaluation
		self.unit_types = None ## updated after every step with all units in the screen
		self.base_top_left = None ## location of self
		self.action_queue = deque() ## if an action has requirements, queue it for later
		self.actions_taken = [(-1, [-1, -1])] ## actions that were returned to the base agent
		self.states_happened = [] ## states that yielded an action at a certain step 
		self.wait_2_count = deque() ## queues those units that require to be counted
		self.point_selected = (None, None) ## point in the screen currently selected. 
		self.depot_x = 5 ## starting x position used for finding locations for buildings
		self.depot_y = 5 ## starting y position used for finding locations for buildings
		self.death = 0

	def get_current_state(self, obs, hot_squares):
		score_cumulative = list(obs.observation['score_cumulative'])
		player_info = list(obs.observation['player'])
		player_info = player_info[1:9] ## since we dont need player id or warpgate and larva counts 
		temp = score_cumulative + player_info
		for unit in list(unit_dict.values()):
			if unit in self.unit_counts:
				temp.append(self.unit_counts[unit])
			else:
				temp.append(0)
		reversed_actions_taken = [self.actions_taken[i*-1][0] for i in range(1, len(self.actions_taken))]
		if len(reversed_actions_taken) < 15: 
			reversed_actions_taken = [0]*(15 - len(reversed_actions_taken)) + reversed_actions_taken
		else:
			reversed_actions_taken = reversed_actions_taken[:15]
		temp = temp + reversed_actions_taken
		temp.append(self.base_top_left)
		temp = temp + list(hot_squares)
		return temp



	def reset(self):
		super(SwarmbotAgent, self).reset()
		self.round += 1
		self.rewardFile = open("rewards.csv", "a+")
		self.rewardFile.write(str(self.round)+","+str(self.rewardTotal)+"\n")
		self.qlearn.save_csv("qtable.csv")
		#self.qlearn.printTable()
		#                      self.hold = 0

	def transfromDistance(self, x, x_distance, y, y_distance):
		"""
			converts a distance based on your location
		"""
		if not self.base_top_left:
			return [x - x_distance, y - y_distance]
		return [x + x_distance, y + y_distance]

	def transformLocation(self, x, y):
		"""
			converts a location based on your location
		"""
		if not self.base_top_left:
			return [64 - x, 64 - y]
		return [x, y]

	def splitAction(self, action_id):
		"""
			splits action for location needed for selecting and attack location
			can also split to whether we are training or building a unit
		"""
		action = smart_actions[action_id]
		if 'attack' in action: ## if its an attack
			splitted = action.split('_')
			if len(splitted) == 4: ## unit specific attack
				print('---->', action) 
				action, x, y, unit = splitted
				return (action, x, y, unit, None)
			else:
				print('---->', action)
				action, x, y = splitted
				return (action, x, y, None, None) ## attack with all units
		elif 'reactor' in action or 'techlab' in action: ## two main add-ons
			print('---->', action)
			action, unit, attachment = action.split('_')
			return (action, None, None, unit, attachment)
		else:	## regular action (either build or train a unit)
			if action == 'donothing' or action == 'retreat':
				return (None, None, None, None, None)
			else:
				print('---->', action)
				action, unit = action.split('_')
				return (action, None, None, unit, None)

	## lent from https://github.com/jlboes/Starcraft-II-learning-bot/blob/master/src/scagent.py
	## credit to the creator, before using, update the self.unit_types
	def findLocationForBuilding(self, size, distance=6, chance=10):
		## start from mineral fields 
		mf_y, mf_x = (self.unit_types == _NEUTRAL_MINERAL_FIELD).nonzero()
		## obtain map limits 
		max_x, max_y = self.unit_types.shape
		while True:
			print(self.death)
			self.death += 1
			## selects random points where to place the building predetermined within radious of (5,5)
			s_target_x = int(self.depot_x + np.random.choice([-1,0,1], 1) * distance)
			s_target_y = int(self.depot_y + np.random.choice([-1,0,1], 1) * distance)
			## if the point fits in the screen 
			within_map = (0 < s_target_x < max_x - size) and (0 < s_target_y < max_y - size)
			## checks to see if there is space available for the building in between other buildings
			area = self.unit_types[s_target_y : s_target_y + 6][s_target_x : s_target_x + 6]
			space_available = not any(x in area for x in Buildings)
			## if the mineral fields are not in the way... idk if vespene geysers might need to be included as well
			within_mineral_field = (min(mf_y) < s_target_y < max(mf_y)) and (min(mf_x) < s_target_x < max(mf_x))
			chance += -1 
			## once you know that the building is within the map area
			## once you know that there is space available to place it in
			## and once you know that they're out of the mineral fields
			if within_map and space_available and not within_mineral_field:
				self.depot_y = s_target_y
				self.depot_x = s_target_x
				s_target = [s_target_x, s_target_y]
				break
			## increase the distance between
			## buildings after every 10 chances 
			## to find a place to put the building 
			if chance == 0:
				distance += 1
				chance = 10
			## wasnt sure if it could at somepoint 
			## stay in an infinite loop in case it 
			## never found a location
			if distance > 20:
				s_target = [-1, -1]
				break
		return s_target


	def apply_counts(self, unit_name=None):
		"""
			applies the count to units as they are created. 
			main part of this is to check if sizes of units 
			have been seen, otherwise these will be updated 
			later. 
		"""
		## this if is only supposed to be done at the beginning of every game
		if not self.unit_counts:
			## locates all unit types that are command centers in the form x, y
			cc_y, cc_x = (self.unit_types == _COMMAND_CENTER).nonzero()
			self.unit_sizes[_COMMAND_CENTER] = len(cc_x)
			self.unit_coords[_COMMAND_CENTER] = [cc_x, cc_y]
			self.unit_counts[_COMMAND_CENTER] = 1 if cc_y.any() else 0
			
			## loactes all unit types that are vespene geysers in the form x, y
			vg_y, vg_x = (self.unit_types == _NEUTRAL_VESPENE_GEYSER).nonzero()
			self.unit_sizes[_NEUTRAL_VESPENE_GEYSER] = len(vg_x)/2 ## two geysers
			self.unit_coords[_NEUTRAL_VESPENE_GEYSER] = [vg_x, vg_y]
			self.unit_counts[_NEUTRAL_VESPENE_GEYSER] = 2 if vg_y.any() else 0

			## locates all unit types that are mineral fields in the form x, y
			mf_y, mf_x = (self.unit_types == _NEUTRAL_MINERAL_FIELD).nonzero()
			self.unit_sizes[_NEUTRAL_MINERAL_FIELD] = 1 ## doesnt matter for now
			self.unit_coords[_NEUTRAL_MINERAL_FIELD] = [vg_x, vg_y]
			self.unit_counts[_NEUTRAL_MINERAL_FIELD] = 1 if vg_y.any() else 0
		## either queues a count for the update step or it increases the count of a unit
		if unit_name is not None:
			unit_y, unit_x = (self.unit_types == unit_dict[unit_name]).nonzero()
			## if we still dont know the size of the unit place it in a queue to count later
			if unit_y.any() is None or unit_dict[unit_name] not in self.unit_sizes:
				self.wait_2_count.append(unit_name)
			else:
				## increases the count by one for every action to train or build
				## in some situations, we might be training more than 1 unit at a
				## time, but for now we will leave it like so. When we do a full 
				## count this will be fixed by itself
				self.unit_counts[unit_dict[unit_name]] += 1
		

	def update_counts(self):
		"""
			Updates counts at the end of every step of the game if necessary. It would update counts
			only if we had just completed a battle. meaning we are counting our loses and the remaining
			units we have now. 
			The first while loop gets the sies for newly seen and created units so that we can count later on
		"""
		## first we need to create the counts, sizes and coords for the queued units
		not_yet_built = deque()
		while(len(self.wait_2_count) != 0):
			unit_name = self.wait_2_count.popLeft()
			unit_x, unit_y = (self.unit_types == unit_dict[unit_name]).nonzero()
			if unit_y.any():
				## gets the pixel size of every unit in the waiting queue
				self.unit_sizes[unit_dict[unit_name]] = count_units(unit_x, unit_y)
				self.unit_counts[unit_dict[unit_name]] = int(math.ceil(len(unit_y) / self.unit_sizes[unit_dict[unit_name]]))
			else: ## those that were just popped out will bw placed back since they havent been built
				not_yet_built.append(unit_name)
		self.wait_2_count = deque(not_yet_built)
		## after we have been in a battle only
		if _ATTACK_MINIMAP == self.actions_taken[-1][0]:
			for unit_id in self.unit_sizes:
				unit_y, _ = (self.unit_types == unit_id).nonzero()
				if unit_y.any():
					self.unit_counts[unit_id] = int(math.ceil(len(unit_y) / self.unit_sizes[unit_id]))
				else:
					self.unit_counts[unit_id] = 0

	def step(self, obs):
		super(SwarmbotAgent, self).step(obs)

		## begins by obtaining all the unit types available on the screen
		self.unit_types = obs.observation['screen'][_UNIT_TYPE]
		## updates counts if necessary for the unit types that are visible
		self.update_counts()

		if obs.last():
			self.reward = obs.reward
			self.qlearn.learn(str(self.prev_state), self.prev_action, self.reward, 'terminal')
			self.reset()
			self.prev_action = None
			self.prev_state = None
			self.move_number = 0
			self.action_queue.clear()

			## in states happened the 3 is terminal. 
			self.states_happened.append((self.prev_state, 3))
			self.actions_taken.append((_NO_OP, []))
			return actions.FunctionCall(_NO_OP, [])

		if obs.first():
			## obtains player location in the map
			player_y, player_x = (obs.observation['minimap'][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
			self.base_top_left = 1 if player_y.any() and player_y.mean() <= 31 else 0	
			## applies initial counts and locations to command centers, vespene geysers and mineral fields
			self.apply_counts()
			self.prev_state = None
			self.prev_action = None

			self.current_state = []

		if self.move_number == 0:
			self.move_number += 1

			## obtains locations at which the enemy would appear. 
			hot_squares = np.zeros(4)
			enemy_y, enemy_x = (obs.observation['minimap'][_PLAYER_RELATIVE] == _PLAYER_HOSTILE).nonzero()
			for i in range(0, len(enemy_y)):
				y = int(math.ceil((enemy_y[i] + 1) / 32))
				x = int(math.ceil((enemy_x[i] + 1) / 32))
				hot_squares[((y-1)*2) + (x - 1)] = 1

			## inverts the map or not based on your location
			if not self.base_top_left:
				hot_squares = hot_squares[::-1]

			## from obs and counts obtain the current state to be used in the qtable
			self.current_state = self.get_current_state(obs, hot_squares)

			## use q table to learn previous action and to choose an action.
			new_action = self.qlearn.choose_action(str(self.current_state))

			self.prev_state = self.current_state 
			self.prev_action = new_action 

			action, x, y, unit, attachment = self.splitAction(self.prev_action)

			self.point_selected = (None, None)

			## Building creation ::

			if action == 'b' and unit in build_with_SCV: ## make barracks
				unit_y, unit_x = (self.unit_types == _SCV).nonzero()
				if unit_y.any():
					i = random.randint(0, len(unit_y) - 1)
					target = [unit_x[i], unit_y[i]]
					self.point_selected = (target, 'scv')
					self.states_happened.append((self.prev_state, self.move_number))
					self.actions_taken.append((_SELECT_POINT, [_NOT_QUEUED, target]))
					return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

			elif action == 'b' and (unit == 'techlab' or unit == 'reactor'):
				unit_y, unit_x = (self.unit_types == unit_dict[attachment]).nonzero()
				if unit_y.any():
					i = random.randint(0, len(unit_y) - 1)
					target = [unit_x[i], unit_y[i]]
					self.point_selected = (target, attachment)
					self.states_happened.append((self.prev_state, self.move_number))
					self.actions_taken.append((_SELECT_POINT, [_NOT_QUEUED, target]))
					return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

			## Training units ::

			elif action == 't' and unit == 'scv':
				unit_y, unit_x = (self.unit_types == _COMMAND_CENTER).nonzero()
				if unit_y.any():
					i = random.randint(0, len(unit_y) - 1)
					target = [unit_x[i], unit_y[i]]
					self.point_selected = (target, 'commandcenter')
					self.states_happened.append((self.prev_state, self.move_number))
					self.actions_taken.append((_SELECT_POINT, [_NOT_QUEUED, target]))
					return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

			elif action == 't' and unit in starport_units:
				unit_y, unit_x = (self.unit_types == _STARPORT).nonzero()
				if unit_y.any():
					i = random.randint(0, len(unit_y) - 1)
					target = [unit_x[i], unit_y[i]]
					self.point_selected = (target, 'starport')
					self.states_happened.append((self.prev_state, self.move_number))
					self.actions_taken.append((_SELECT_POINT, [_NOT_QUEUED, target]))
					return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])


			elif action == 't' and unit in barracks_units:
				unit_y, unit_x = (self.unit_types == _BARRACKS).nonzero()
				if unit_y.any():
					i = random.randint(0, len(unit_y) - 1)
					target = [unit_x[i], unit_y[i]]
					self.point_selected = (target, 'barracks')
					self.states_happened.append((self.prev_state, self.move_number))
					self.actions_taken.append((_SELECT_POINT, [_NOT_QUEUED, target]))
					return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])


			elif action == 't' and unit in factory_units:
				unit_y, unit_x = (self.unit_types == _FACTORY).nonzero()
				if unit_y.any():
					i = random.randint(0, len(unit_y) - 1)
					target = [unit_x[i], unit_y[i]]
					self.point_selected = (target, 'factory')
					self.states_happened.append((self.prev_state, self.move_number))
					self.actions_taken.append((_SELECT_POINT, [_NOT_QUEUED, target]))
					return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

			## send out attack... might add unit specific

			elif action == 'attack' and _SELECT_ARMY in obs.observation['available_actions']:
				self.states_happened.append((self.prev_state, self.move_number))
				self.actions_taken.append((_SELECT_ARMY, [_NOT_QUEUED]))
				return actions.FunctionCall(_SELECT_ARMY, )


		elif self.move_number == 1:
			self.move_number += 1

			action, x, y, unit, attachment = self.splitAction(self.prev_action)

			if action == 'b' and unit == 'refinery' and build_to_action[unit] in obs.observation['available_actions']: ## make refinery 
				unit_y, unit_x = (self.unit_types == _NEUTRAL_VESPENE_GEYSER).nonzero()
				if unit_y.any():
					i = random.randint(0, len(unit_y) - 1)
					target = [unit_x[i], unit_y[i]]
					self.states_happened.append((self.prev_state, self.move_number))
					self.actions_taken.append((_BUILD_REFINERY, [_NOT_QUEUED, target]))
					return actions.FunctionCall(_BUILD_REFINERY, [_NOT_QUEUED, target])

			elif action == 'b' and (unit == 'techlab' or unit == 'reactor')  and build_to_action[unit] in obs.observation['available_actions']: ## place add-on
				unit_y, unit_x = (self.unit_types == _SCV).nonzero()
				if self.point_selected is not (None, None):
					target = self.point_selected[0]
					if self.point_selected[1] != 'scv':
						## if we ppreviously didnt select scvs
						self.point_selected = (None, None)
						self.states_happened.append((self.prev_state, self.move_number))
						self.actions_taken.append((_BUILD_TECHLAB, [_NOT_QUEUED, target]))
						return actions.FunctionCall(_BUILD_TECHLAB, [_NOT_QUEUED, target])

			## will compress later
			elif action == 'b' and (unit in build_with_SCV and unit != 'refinery')  and build_to_action[unit] in obs.observation['available_actions']: ## make barracks
				
				if unit == 'armory':
					if unit_dict[unit] in self.unit_counts:
						count = self.unit_counts[unit_dict[unit]]
						if count < 2:
							size = int(math.ceil(math.sqrt(self.unit_sizes[unit_dict[unit]])))
							target = self.findLocationForBuilding(size)
							if target is not [-1, -1]:
								self.apply_counts(unit)
								self.states_happened.append((self.prev_state, self.move_number))
								self.actions_taken.append((_BUILD_ARMORY, [_NOT_QUEUED, target]))
								return actions.FunctionCall(_BUILD_ARMORY, [_NOT_QUEUED, target])
					else:
						guess = 150
						target = self.findLocationForBuilding(guess)
						if target is not [-1, -1]:
							self.apply_counts(unit)
							self.states_happened.append((self.prev_state, self.move_number))
							self.actions_taken.append((_BUILD_ARMORY, [_NOT_QUEUED, target]))
							return actions.FunctionCall(_BUILD_ARMORY, [_NOT_QUEUED, target])


				elif unit == 'barracks':
					if unit_dict[unit] in self.unit_counts:
						count = self.unit_counts[unit_dict[unit]]
						if count < 4:
							size = int(math.ceil(math.sqrt(self.unit_sizes[unit_dict[unit]])))
							target = self.findLocationForBuilding(size)
							if target is not [-1, -1]:
								self.apply_counts(unit)
								self.states_happened.append((self.prev_state, self.move_number))
								self.actions_taken.append((_BUILD_BARRACKS, [_NOT_QUEUED, target]))
								return actions.FunctionCall(_BUILD_BARRACKS, [_NOT_QUEUED, target])
					else:
						guess = 150
						target = self.findLocationForBuilding(guess)
						if target is not [-1, -1]:
							self.apply_counts(unit)
							self.states_happened.append((self.prev_state, self.move_number))
							self.actions_taken.append((_BUILD_BARRACKS, [_NOT_QUEUED, target]))
							return actions.FunctionCall(_BUILD_BARRACKS, [_NOT_QUEUED, target])

				elif unit == 'factory': 
					if unit_dict[unit] in self.unit_counts:
						count = self.unit_counts[unit_dict[unit]]
						if count < 2:
							size = int(math.ceil(math.sqrt(self.unit_sizes[unit_dict[unit]])))
							target = self.findLocationForBuilding(size)
							if target is not [-1, -1]:
								self.apply_counts(unit)
								self.states_happened.append((self.prev_state, self.move_number))
								self.actions_taken.append((_BUILD_FACTORY, [_NOT_QUEUED, target]))
								return actions.FunctionCall(_BUILD_FACTORY, [_NOT_QUEUED, target])
					else:
						guess = 150
						target = self.findLocationForBuilding(guess)
						if target is not [-1, -1]:
							self.apply_counts(unit)
							self.states_happened.append((self.prev_state, self.move_number))
							self.actions_taken.append((_BUILD_FACTORY, [_NOT_QUEUED, target]))
							return actions.FunctionCall(_BUILD_FACTORY, [_NOT_QUEUED, target])

				elif unit == 'fusioncore':
					if unit_dict[unit] in self.unit_counts:
						count = self.unit_counts[unit_dict[unit]]
						if count < 2:
							size = int(math.ceil(math.sqrt(self.unit_sizes[unit_dict[unit]])))
							target = self.findLocationForBuilding(size)
							if target is not [-1, -1]:
								self.apply_counts(unit)
								self.states_happened.append((self.prev_state, self.move_number))
								self.actions_taken.append((_BUILD_FUSION_CORE, [_NOT_QUEUED, target]))
								return actions.FunctionCall(_BUILD_FUSION_CORE, [_NOT_QUEUED, target])
					else:
						guess = 150
						target = self.findLocationForBuilding(guess)
						if target is not [-1, -1]:
							self.apply_counts(unit)
							self.states_happened.append((self.prev_state, self.move_number))
							self.actions_taken.append((_BUILD_FUSION_CORE, [_NOT_QUEUED, target]))
							return actions.FunctionCall(_BUILD_FUSION_CORE, [_NOT_QUEUED, target])

				elif unit == 'ghostacademy':
					if unit_dict[unit] in self.unit_counts:
						count = self.unit_counts[unit_dict[unit]]
						if count < 2:
							size = int(math.ceil(math.sqrt(self.unit_sizes[unit_dict[unit]])))
							target = self.findLocationForBuilding(size)
							if target is not [-1, -1]:
								self.apply_counts(unit)
								self.states_happened.append((self.prev_state, self.move_number))
								self.actions_taken.append((_BUILD_GHOST_ACADEMY, [_NOT_QUEUED, target]))
								return actions.FunctionCall(_BUILD_GHOST_ACADEMY, [_NOT_QUEUED, target])
					else:
						guess = 150
						target = self.findLocationForBuilding(guess)
						if target is not [-1, -1]:
							self.apply_counts(unit)
							self.states_happened.append((self.prev_state, self.move_number))
							self.actions_taken.append((_BUILD_GHOST_ACADEMY, [_NOT_QUEUED, target]))
							return actions.FunctionCall(_BUILD_GHOST_ACADEMY, [_NOT_QUEUED, target])

				elif unit == 'starport':
					if unit_dict[unit] in self.unit_counts:
						count = self.unit_counts[unit_dict[unit]]
						if count < 2:
							size = int(math.ceil(math.sqrt(self.unit_sizes[unit_dict[unit]])))
							target = self.findLocationForBuilding(size)
							if target is not [-1, -1]:
								self.apply_counts(unit)
								self.states_happened.append((self.prev_state, self.move_number))
								self.actions_taken.append((_BUILD_STARPORT, [_NOT_QUEUED, target]))
								return actions.FunctionCall(_BUILD_STARPORT, [_NOT_QUEUED, target])
					else:
						guess = 150
						target = self.findLocationForBuilding(guess)
						if target is not [-1, -1]:
							self.apply_counts(unit)
							self.states_happened.append((self.prev_state, self.move_number))
							self.actions_taken.append((_BUILD_STARPORT, [_NOT_QUEUED, target]))
							return actions.FunctionCall(_BUILD_STARPORT, [_NOT_QUEUED, target])

				elif unit == 'supplydepot':
					if unit_dict[unit] in self.unit_counts:
						count = self.unit_counts[unit_dict[unit]]
						if count < 5:
							size = int(math.ceil(math.sqrt(self.unit_sizes[unit_dict[unit]])))
							target = self.findLocationForBuilding(size)
							if target is not [-1, -1]:
								self.apply_counts(unit)
								self.states_happened.append((self.prev_state, self.move_number))
								self.actions_taken.append((_BUILD_SUPPLY_DEPOT, [_NOT_QUEUED, target]))
								return actions.FunctionCall(_BUILD_SUPPLY_DEPOT, [_NOT_QUEUED, target])
					else:
						guess = 150
						target = self.findLocationForBuilding(guess)
						if target is not [-1, -1]:
							self.apply_counts(unit)
							self.states_happened.append((self.prev_state, self.move_number))
							self.actions_taken.append((_BUILD_SUPPLY_DEPOT, [_NOT_QUEUED, target]))
							return actions.FunctionCall(_BUILD_SUPPLY_DEPOT, [_NOT_QUEUED, target])

				## elif unit == 'commandcenter': ## will not be implemented yet 

			## traing  units ::

			## might expand idk yet
			elif action == 't' and self.point_selected is not (None, None) and unit_to_action[unit] in obs.observation['available_actions']:
				self.states_happened.append((self.prev_state, self.move_number))
				self.actions_taken.append((unit_to_action[unit], [_QUEUED]))
				return actions.FunctionCall(unit_to_action[unit], [_QUEUED])

			## actually attack

			elif action == 'attack':
				do_it = True
				
				if len(obs.observation['single_select']) > 0 and obs.observation['single_select'][0][0] == _SCV:
					do_it = False
				
				if len(obs.observation['multi_select']) > 0 and obs.observation['multi_select'][0][0] == _SCV:
					do_it = False
				
				if do_it and _ATTACK_MINIMAP in obs.observation["available_actions"]:
					x_offset = random.randint(-1, 1)
					y_offset = random.randint(-1, 1)
					
					return actions.FunctionCall(_ATTACK_MINIMAP, [_NOT_QUEUED, self.transformLocation(int(x) + (x_offset * 8), int(y) + (y_offset * 8))])
				

		elif self.move_number == 2:
			self.move_number = 0

			action, x, y, unit, attachment = self.splitAction(self.prev_action)

			## returns idle scvs to mineral harvesting 
			if action == 'b' and unit in build_with_SCV:
				if _HARVEST_GATHER in obs.observation['available_actions']:
					unit_y, unit_x = (self.unit_types == _NEUTRAL_MINERAL_FIELD).nonzero()
					if unit_y.any():
						i = random.randint(0, len(unit_y) - 1)
						target = [int(unit_x[i]), int(unit_y[i])]
						self.states_happened.append((self.prev_state, self.move_number))
						self.actions_taken.append((_HARVEST_GATHER, [_NOT_QUEUED, target]))
						return actions.FunctionCall(_HARVEST_GATHER, [_QUEUED, target])

			## at this point you can also add research actions... 

		self.states_happened.append((self.prev_state, self.move_number))
		self.actions_taken.append((_NO_OP, []))
		return actions.FunctionCall(_NO_OP, [])
