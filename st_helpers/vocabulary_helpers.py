from database.db_helpers_dashboard import most_practiced_levels

""" Available modes for vocabulary exercises - individual levels """
available_modes = {
    "Level: A1 Set: 1": "a1.1",
    "Level: A1 Set: 2": "a1.2",
    "Level: A2 Set: 1": "a2.1",
    "Level: A2 Set: 2": "a2.2",
    "Level: B1 Set: 1": "b1.1",
    "Level: B1 Set: 2": "b1.2",
    "Level: B2 Set: 1": "b2.1",
    "Level: B2 Set: 2": "b2.2",
    "Level: C1 Set: 1": "c1.1",
    "Level: C1 Set: 2": "c1.2"
}
available_modes_r = {v: k for k, v in available_modes.items()}

# Full ordered list for all modes
ordered_levels = [
    "a1.1", "a1.2",
    "a2.1", "a2.2",
    "b1.1", "b1.2",
    "b2.1", "b2.2",
    "c1.1", "c1.2"
]

def return_chart_levels():
    practiced_levels = most_practiced_levels()
    practiced = [lvl.lower() for (lvl,) in practiced_levels]

    # Fill up to 4 by checking neighbors
    i = 0
    while len(practiced) < 4 and i < len(practiced):
        try:
            idx = ordered_levels.index(practiced[i])
        except ValueError:
            i += 1
            continue
        neighbors = []
        if idx > 0:
            neighbors.append(ordered_levels[idx - 1])
        if idx < len(ordered_levels) - 1:
            neighbors.append(ordered_levels[idx + 1])
        for n in neighbors:
            if n not in practiced:
                practiced.append(n)
            if len(practiced) == 4:
                break
        i += 1

    # If still not 4, just fill from the top
    for lvl in ordered_levels:
        if lvl not in practiced:
            practiced.append(lvl)
        if len(practiced) == 4:
            break

    return practiced
