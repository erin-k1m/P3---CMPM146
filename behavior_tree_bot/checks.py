

def if_defensive_threat(state):
    return False


def if_snipe_opportunity_available(state):
    return False


def if_good_neutral_available(state):
    return False


def if_offensive_target_available(state):
    return False


def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())
