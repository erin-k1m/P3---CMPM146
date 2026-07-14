#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    # offensive_plan = Sequence(name='Offensive Strategy')
    # largest_fleet_check = Check(have_largest_fleet)
    # attack = Action(attack_weakest_enemy_planet)
    # offensive_plan.child_nodes = [largest_fleet_check, attack]

    # spread_sequence = Sequence(name='Spread Strategy')
    # neutral_planet_check = Check(if_neutral_planet_available)
    # spread_action = Action(spread_to_weakest_neutral_planet)
    # spread_sequence.child_nodes = [neutral_planet_check, spread_action]

    # root.child_nodes = [offensive_plan, spread_sequence, attack.copy()]

    defense_sequence = Sequence(name='Defensive Strategy')
    defense_check = Check(if_defensive_threat)
    defense_action = Action(defend_threatened_planet)
    defense_sequence.child_nodes = [defense_check, defense_action]

    snipe_sequence = Sequence(name='Snipe Enemy Neutral Capture')
    snipe_check = Check(if_snipe_opportunity_available)
    snipe_action = Action(snipe_enemy_capture)
    snipe_sequence.child_nodes = [snipe_check, snipe_action]

    expansion_sequence = Sequence(name='Neutral Expansion')
    expansion_check = Check(if_good_neutral_available)
    expansion_action = Action(expand_to_neutral_planet)
    expansion_sequence.child_nodes = [expansion_check, expansion_action]

    offense_sequence = Sequence(name='Offensive Attack')
    offense_check = Check(if_offensive_target_available)
    offense_action = Action(attack_enemy_planet)
    offense_sequence.child_nodes = [offense_check, offense_action]

    fallback_action = Action(spread_to_weakest_neutral_planet)

    root.child_nodes = [
        defense_sequence,
        snipe_sequence,
        expansion_sequence,
        offense_sequence,
        fallback_action,
    ]

    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
