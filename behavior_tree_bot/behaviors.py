import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def _is_exposed(state, planet): #if a planet is exposed to an enemy fleet that can take it over, return True
    for fleet in state.enemy_fleets():
        if fleet.destination_planet != planet.ID:
            continue

        projected_defense = planet.num_ships + planet.growth_rate * max(0, fleet.turns_remaining - 1)   #variable to determine how many ships will be on the planet when the enemy fleet arrives
        if fleet.num_ships > projected_defense:
            return True
    return False


def _choose_source(state, target_id, ships_needed): #chooses the best source planet to send ships from to defend a threatened planet
    best_source = None
    best_score = None

    for source in state.my_planets():
        if source.ID == target_id or source.num_ships <= ships_needed: #if the source planet is the same as the target planet or if the source planet doesn't have enough ships to send, skip it
            continue

        exposed = 1 if _is_exposed(state, source) else 0
        distance = state.distance(source.ID, target_id)
        remaining_after = source.num_ships - ships_needed
        score = (exposed, distance, -remaining_after, -source.num_ships) #score is a tuple that prioritizes exposed planets, then distance, then remaining ships after sending, then total ships on the source planet

        if best_score is None or score < best_score:
            best_score = score
            best_source = source

    return best_source


def defend_threatened_planet(state):
    threatened_planet = None
    needed_ships = 0

    for planet in state.my_planets():   #threatened_planet is the planet that is under threat from an enemy fleet, and needed_ships is the number of ships needed to defend it
        for fleet in state.enemy_fleets():
            if fleet.destination_planet != planet.ID:
                continue

            projected_defense = planet.num_ships + planet.growth_rate * max(0, fleet.turns_remaining - 1) #calculation is used to determine how many ships will be on the planet when the enemy fleet arrives
            deficit = fleet.num_ships - projected_defense
            if deficit > needed_ships:
                needed_ships = deficit
                threatened_planet = planet

    if threatened_planet is None:
        return False

    ships_to_send = needed_ships + 1
    source = _choose_source(state, threatened_planet.ID, ships_to_send)
    if source is None:
        return False

    return issue_order(state, source.ID, threatened_planet.ID, ships_to_send)


def snipe_enemy_capture(state): #this function checks if there is an opp to snipe an enemy fleet that is trying to capture a neutral planet. If there is, it sends ships from one of the player's planets to the neutral planet to intercept the enemy fleet.
    best_plan = None

    for fleet in state.enemy_fleets(): #here, we iterate through all enemy fleets to find one that is trying to capture a neutral planet. If we find one, we check if we have a planet that can send enough ships to intercept the enemy fleet and take the neutral planet before the enemy fleet arrives.
        target_planet = state.planets[fleet.destination_planet]
        if target_planet.owner != 0:
            continue

        enemy_survivors = fleet.num_ships - target_planet.num_ships
        if enemy_survivors <= 0:
            continue

        for source_planet in state.my_planets(): #over here, we iterate through all of the player's planets to find one that can send enough ships to intercept the enemy fleet and take the neutral planet before the enemy fleet arrives.
            my_distance = state.distance(source_planet.ID, target_planet.ID)
            delay = my_distance - fleet.turns_remaining
            if delay < 1 or delay > 3:
                continue

            expected_defenders = enemy_survivors + target_planet.growth_rate * delay
            ships_to_send = expected_defenders + 3
            if source_planet.num_ships <= ships_to_send:
                continue

            score = (target_planet.growth_rate, -delay, -ships_to_send, source_planet.num_ships)
            if best_plan is None or score > best_plan[0]:
                best_plan = (score, source_planet, target_planet, ships_to_send)

    if best_plan is None:
        return False

    _, source_planet, target_planet, ships_to_send = best_plan
    return issue_order(state, source_planet.ID, target_planet.ID, ships_to_send)


def expand_to_neutral_planet(state):    #this func checks if there is a good neutral planet to expand to. If there is, it sends ships from one of the player's planets to the neutral planet to capture it.
    best_plan = None

    for neutral in state.neutral_planets(): #we iterate through all neutral planets to find one that is a good target for expansion. If we find one, we check if we have a planet that can send enough ships to capture the neutral planet before the enemy fleet arrives.
        if any(fleet.destination_planet == neutral.ID for fleet in state.enemy_fleets()):
            continue

        for source_planet in state.my_planets(): #iterates through all players planets to find one that can send enough  ships to capture the neutral planet before the enemy fleet arrives.
            ships_to_send = neutral.num_ships + 1
            if source_planet.num_ships <= ships_to_send:
                continue

            distance = state.distance(source_planet.ID, neutral.ID)
            score = neutral.growth_rate / float(ships_to_send + distance + 1)
            if best_plan is None or score > best_plan[0]:
                best_plan = (score, source_planet, neutral, ships_to_send)

    if best_plan is None:
        return False

    _, source_planet, neutral, ships_to_send = best_plan
    return issue_order(state, source_planet.ID, neutral.ID, ships_to_send)


def attack_enemy_planet(state): 
    best_plan = None

    for enemy in state.enemy_planets():
        for source_planet in state.my_planets():
            distance = state.distance(source_planet.ID, enemy.ID)
            ships_to_send = enemy.num_ships + enemy.growth_rate * distance + 1
            if source_planet.num_ships <= ships_to_send:
                continue

            score = enemy.growth_rate / float(ships_to_send + distance + 1)
            if best_plan is None or score > best_plan[0]:
                best_plan = (score, source_planet, enemy, ships_to_send)

    if best_plan is None:
        return False

    _, source_planet, enemy, ships_to_send = best_plan
    return issue_order(state, source_planet.ID, enemy.ID, ships_to_send)


def fallback_action(state):
    return False


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships // 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships // 2)
