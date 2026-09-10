"""
2026 FIFA World Cup Win Probability Model

Builds Elo ratings for all 48 teams from historical match results (2002-present),
applies small host-nation/debutant adjustments, determines group qualification by
Elo, then converts the 32 advancing teams' Elo ratings into tournament winning percentages
using the Bradley-Terry model.
"""

import csv
from collections import defaultdict

# path to Kaggle dataset containing international soccer/football matches from 1872-11-30 to 2026-06-10
RESULTS_CSV_PATH = "results.csv"
# starting Elo for all teams (this is the rating assigned to any team with no match history yet)
STARTING_ELO = 1000.0
# Elo bonus for the home team in a non-neutral match
HOME_ADVANTAGE = 50

# only matches from this date onward are used to build a team's Elo
# 2002-01-04 covers the last 24 years and the last 6 World Cups (2002 to 2022)
START_DATE = "2002-01-04"

# host nations get an Elo bonus due to host advantage
# debutants get an Elo penalty for lacking experience at this level
# Elo bonus and Elo penalty are applied only to this tournament's predictions, not the real historical ratings
HOST_TEAMS = ["Canada", "Mexico", "United States"]
HOST_ADVANTAGE = 10
DEBUTANT_TEAMS = ["Cape Verde", "Curaçao", "Jordan", "Uzbekistan"]
DEBUTANT_PENALTY = 20

# the 48 teams that are competing in the 2026 FIFA World Cup, organized into their 12 groups (A-L)
GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# flattens GROUPS into one plain list of all 48 team names
# used later wherever we need all 48 teams without caring which group they're in
ALL_WC_TEAMS = []
for group in GROUPS.values():
    for team in group:
        ALL_WC_TEAMS.append(team)

# K-Factors: how much a single result can move a team's rating
# scaled by tournament importance (ex. World Cup wins are more important than Friendly wins)
K_WORLD_CUP = 50
K_EURO = 45
K_COPA_AMERICA = 40
K_AFRICA_CUP = 30
K_ASIAN_CUP = 25
K_GOLD_CUP = 15
K_QUALIFIER = 10
K_OTHER = 5


# returns the K-Factor for a match based on its 'tournament' column
def get_k_factor(tournament_name):
    if tournament_name == "FIFA World Cup":
        return K_WORLD_CUP
    if tournament_name == "UEFA Euro":
        return K_EURO
    if tournament_name == "Copa América":
        return K_COPA_AMERICA
    if tournament_name == "African Cup of Nations":
        return K_AFRICA_CUP
    if tournament_name == "AFC Asian Cup":
        return K_ASIAN_CUP
    if tournament_name == "Gold Cup":
        return K_GOLD_CUP
    if tournament_name == "FIFA World Cup qualification" or tournament_name == "UEFA Euro qualification" or tournament_name == "Copa América qualification" or tournament_name == "African Cup of Nations qualification" or tournament_name == "AFC Asian Cup qualification" or tournament_name == "Gold Cup qualification":
        return K_QUALIFIER
    return K_OTHER


# Standard Elo Formula: probability that TEAM A beats TEAM B
# a draw counts as half a win
def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


# reads match history in chronological order, updating both teams' Elo after every match
# returns {team_name: final_rating}
def build_elo_ratings(csv_path):
    elo: dict[str, float] = defaultdict(lambda: STARTING_ELO)

    with open(csv_path, newline="", encoding="utf-8") as f:
        matches = list(csv.DictReader(f))

    for row in matches:
        # ignores all matches older than START_DATE
        if row["date"] < START_DATE:
            continue

        home = row["home_team"]
        away = row["away_team"]

        home_score = int(row["home_score"])
        away_score = int(row["away_score"])

        is_neutral = row["neutral"] == "TRUE"

        home_rating = elo[home]
        away_rating = elo[away]

        # home advantage is only applied at a non-neutral match
        if is_neutral:
            adjusted_home_rating = home_rating
        else:
            adjusted_home_rating = home_rating + HOME_ADVANTAGE

        expected_home = expected_score(adjusted_home_rating, away_rating)

        # actual result as an Elo score (win = 1, draw = 0.5, loss = 0)
        # gets compared against expected_home to measure how surprising this result was
        if home_score > away_score:
            actual_home = 1.0
        elif home_score < away_score:
            actual_home = 0.0
        else:
            actual_home = 0.5

        k = get_k_factor(row["tournament"])

        # move each rating toward the actual result, scaled by K
        elo[home] = home_rating + k * (actual_home - expected_home)
        elo[away] = away_rating + k * ((1 - actual_home) - (1 - expected_home))

    return elo


# returns a copy of elo_ratings with the host bonus and debutant penalty applied
# it is only used for predicting this tournament (the original Elos stay the same)
def apply_adjustments(elo_ratings):
    adjusted = dict(elo_ratings)

    for team in HOST_TEAMS:
        adjusted[team] += HOST_ADVANTAGE

    for team in DEBUTANT_TEAMS:
        adjusted[team] -= DEBUTANT_PENALTY

    return adjusted


# prints all 48 teams ranked 1-48 by adjusted Elo
# indicates which teams got the host bonus and debutant penalty
def print_all_48_table(adjusted_ratings):
    print("=" * 70)
    print("ELO ADJUSTMENTS FOR HOST NATIONS AND DEBUTANTS")
    print("=" * 70)

    print()

    print("HOST NATIONS:")
    for team in HOST_TEAMS:
        print(team)
    print(f"WILL HAVE A +{HOST_ADVANTAGE} ELO BOOST BECAUSE THEY'RE HOSTING THE WORLD CUP")

    print()

    print("DEBUTANTS:")
    for team in DEBUTANT_TEAMS:
        print(team)
    print(f"WILL HAVE A -{DEBUTANT_PENALTY} ELO PENALTY BECAUSE THIS IS THEIR FIRST WORLD CUP")

    print()

    print("=" * 70)
    print("ALL 48 TEAMS RANKED BY ELO")
    print("=" * 70)

    print()

    ranked = sorted(ALL_WC_TEAMS, key=lambda team: adjusted_ratings[team], reverse=True)

    for rank, team in enumerate(ranked, start=1):
        print(f"{rank:>2}. {team:<25} ELO: {adjusted_ratings[team]:.1f}")


# sorts each group's 4 teams by adjusted Elo (strongest to weakest)
# returns {group_letter: [team1, team2, team3, team4]}
def rank_teams_within_groups(adjusted_ratings):
    group_orders = {}
    for group_letter, teams in GROUPS.items():
        ordered = sorted(teams, key=lambda team: adjusted_ratings[team], reverse=True)
        group_orders[group_letter] = ordered
    return group_orders


# compares all 12 third-place finishers (index 2 in each group) and returns the best 8 by Elo
def pick_best_third_place_teams(group_orders, adjusted_ratings):
    third_place_teams = []
    for order in group_orders.values():
        third_place_teams.append(order[2])
    third_place_teams.sort(key=lambda team: adjusted_ratings[team], reverse=True)
    return set(third_place_teams[:8])


# prints each group's Elo-ranked order
# indicates which teams go through based on advancing_thirds
def print_group_qualification(group_orders, adjusted_ratings, advancing_thirds):
    print()
    print("=" * 70)
    print("GROUP QUALIFICATION BASED ON ELO (WHO ADVANCES?)")
    print("=" * 70)

    for group_letter, ordered_teams in group_orders.items():
        print()
        print(f"GROUP {group_letter}:")
        for position, team in enumerate(ordered_teams, start=1):
            print(f"{position}. {team:<26} ELO: {adjusted_ratings[team]:6.1f}")

        first = ordered_teams[0]
        second = ordered_teams[1]
        third = ordered_teams[2]

        if third in advancing_thirds:
            print(f"-> {first}, {second}, AND {third} ADVANCE")
        else:
            print(f"-> {first} AND {second} ADVANCE")


# Bradley-Terry Model: turns Elo ratings directly into tournament winning percentages
# extends Elo's own head-to-head formula to many competitors at once:
# strength_i = 10^(elo_i / 400)
# P(team i wins) = strength_i / sum(strength_j for every team j)
# applied to the teams that advance from the GROUP STAGE so their percentages sum to 100% among themselves
def compute_win_probabilities(ratings_by_team):
    strengths = {}
    for team, rating in ratings_by_team.items():
        strengths[team] = 10 ** (rating / 400)

    total = sum(strengths.values())

    probabilities = {}
    for team, s in strengths.items():
        probabilities[team] = s / total
    return probabilities


# prints the ranking of the 32 advancing teams by win probability
# returns a list of this ranking that is used in main() to indicate the team with the highest chance of winning the tournament
def print_win_probabilities(win_probabilities):
    print()
    print("=" * 70)
    print("CHANCES OF WINNING THE WORLD CUP FOR THE 32 TEAMS THAT ADVANCED")
    print("=" * 70)
    print()

    ranked = sorted(win_probabilities.items(), key=lambda pair: pair[1], reverse=True)
    for rank, (team, probability) in enumerate(ranked, start=1):
        print(f"{rank:>2}. {team:<23} {100 * probability:6.2f}%")

    return ranked


def main():
    print("=" * 70)
    print("2026 FIFA WORLD CUP WIN PROBABILITY MODEL")
    print()

    elo_ratings_all_teams = build_elo_ratings(RESULTS_CSV_PATH)

    base_ratings = {}
    for team in ALL_WC_TEAMS:
        base_ratings[team] = elo_ratings_all_teams[team]
    adjusted_ratings = apply_adjustments(base_ratings)

    # print all 48 teams ranked by Elo
    print_all_48_table(adjusted_ratings)

    # print group qualification based on Elo (top 2 per group + best 8 third-place = 32 teams)
    group_orders = rank_teams_within_groups(adjusted_ratings)
    advancing_thirds = pick_best_third_place_teams(group_orders, adjusted_ratings)
    print_group_qualification(group_orders, adjusted_ratings, advancing_thirds)

    advancing_teams = []
    for ordered_teams in group_orders.values():
        advancing_teams.append(ordered_teams[0])
        advancing_teams.append(ordered_teams[1])
        if ordered_teams[2] in advancing_thirds:
            advancing_teams.append(ordered_teams[2])

    # print win probabilities renormalized across just the 32 advancing teams
    advancing_ratings = {}
    for team in advancing_teams:
        advancing_ratings[team] = adjusted_ratings[team]
    win_probabilities = compute_win_probabilities(advancing_ratings)
    ranked = print_win_probabilities(win_probabilities)

    # print the team that is most likely to win the tournament (ie. champion)
    champion, champion_probability = ranked[0]
    print()
    print(f"{champion} IS MOST LIKELY TO WIN THE 2026 FIFA WORLD CUP ({100 * champion_probability:.2f}% CHANCE)")
    print("=" * 70)


if __name__ == "__main__":
    main()
