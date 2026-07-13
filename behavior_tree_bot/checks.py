

def if_defensive_threat(state):
    for fleet in state.enemy_fleets():
        target_planet = state.planets[fleet.destination_planet]
        if target_planet.owner != 1:
            continue

        projected_defense = target_planet.num_ships + target_planet.growth_rate * max(0, fleet.turns_remaining - 1)
        if fleet.num_ships > projected_defense:
            return True
    return False


def if_snipe_opportunity_available(state):
    for fleet in state.enemy_fleets():
        target_planet = state.planets[fleet.destination_planet]
        if target_planet.owner != 0:
            continue

        remaining_strength = abs(fleet.num_ships - target_planet.num_ships)
        if remaining_strength <= 10:
            for source_planet in state.my_planets():
                my_distance = state.distance(source_planet.ID, target_planet.ID)
                delay = my_distance - fleet.turns_remaining
                if 1 <= delay <= 5 and source_planet.num_ships > (remaining_strength + target_planet.growth_rate * delay):
                    return True
    return False


def if_good_neutral_available(state):
    if not state.my_planets() or not state.neutral_planets():
        return False

    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if not strongest_planet:
        return False

    for neutral in state.neutral_planets():
        cost_to_take = neutral.num_ships + 2
        if strongest_planet.num_ships > cost_to_take and neutral.growth_rate >= 1:
            return True
    return False


def if_offensive_target_available(state):
    if not state.my_planets() or not state.enemy_planets() or state.my_fleets():
        return False

    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    for enemy in state.enemy_planets():
        if strongest_planet.num_ships > enemy.num_ships + enemy.growth_rate * state.distance(strongest_planet.ID, enemy.ID):
            return True
    return False


def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())
