

def _is_exposed(state, planet):
    for fleet in state.enemy_fleets():
        if fleet.destination_planet != planet.ID:
            continue

        projected_defense = planet.num_ships + planet.growth_rate * max(0, fleet.turns_remaining - 1)
        if fleet.num_ships > projected_defense:
            return True
    return False

# this condition checker checks if any of the player's planets are under threat from an enemy fleet that can take it over. 
# It returns True if there is a defensive threat, and False otherwise.
def if_defensive_threat(state):
    for fleet in state.enemy_fleets():
        target_planet = state.planets[fleet.destination_planet]
        if target_planet.owner != 1:
            continue

        # projected defense is calculated by taking the current number of ships on the planet 
        # and adding the growth rate multiplied by the number of turns remaining for the enemy fleet to arrive
        projected_defense = target_planet.num_ships + target_planet.growth_rate * max(0, fleet.turns_remaining - 1) 
        safety_margin = max(2, target_planet.growth_rate + 1)
        if fleet.num_ships > projected_defense + safety_margin:
            return True
    return False


# this condition checker checks if there is an opportunity to snipe an enemy fleet that is attempting to capture a neutral planet, preventing it from growing further and become harder to capture
def if_snipe_opportunity_available(state):
    for fleet in state.enemy_fleets():
        target_planet = state.planets[fleet.destination_planet]
        if target_planet.owner != 0:
            continue

        remaining_strength = abs(fleet.num_ships - target_planet.num_ships)
        if remaining_strength > 10:
            continue

        for source_planet in state.my_planets():
            my_distance = state.distance(source_planet.ID, target_planet.ID)
            delay = my_distance - fleet.turns_remaining
            if 1 <= delay <= 5: # we only want to snipe if we can arrive within a reasonable time frame, so we check if the delay is between 1 and 5 turns
                expected_defenders = remaining_strength + target_planet.growth_rate * delay
                ships_needed = expected_defenders + 3
                if source_planet.num_ships > ships_needed:
                    return True
    return False


# this condition checker checks if there is a good neutral planet available for expansion 
# A good neutral planet is defined as one can be captured with a reasonable # of ships from one of the player's planets
def if_good_neutral_available(state):
    if not state.my_planets() or not state.neutral_planets():
        return False

    for neutral in state.neutral_planets():
        for source_planet in state.my_planets():
            distance = state.distance(source_planet.ID, neutral.ID)
            cost_to_take = neutral.num_ships + 1
            if source_planet.num_ships <= cost_to_take:
                continue

            # a score is necessary to determine if the neutral planet is worth expanding to. 
            # it is calculated by taking the growth rate of the neutral planet and dividing it by the cost to take it plus the distance from the source planet
            score = neutral.growth_rate / float(cost_to_take + distance + 1)
            if score >= 0.1:
                return True
    return False

# this condition checker checks if there is an offensive target available for attack, 
# we define an offensive target as an enemy planet that can be captured with a reasonable number of ships from one of the our planets
def if_offensive_target_available(state):
    if not state.my_planets() or not state.enemy_planets():
        return False

    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if not strongest_planet:
        return False

    for enemy in state.enemy_planets():
        distance = state.distance(strongest_planet.ID, enemy.ID)
        estimated_cost = enemy.num_ships + enemy.growth_rate * distance + 2
        if strongest_planet.num_ships > estimated_cost:
            return True
    return False


def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())
