# 2026 FIFA World Cup Win Probability Model

## Overview

This project predicts each of the 48 qualified teams' chances of winning the 2026 FIFA World Cup using real historical international football match data. It builds an Elo rating for every team from years of past results, then uses that Elo rating to determine who advances out of the group stage and who's most likely to win the entire tournament. The program compares Elo ratings directly and applies probability formulas to go straight from "how strong is this team, historically?" to "what are their odds of winning it all?" The model in the program is fully deterministic, meaning that running it multiple times on the same data will always produce the same result as there is no simulation happening.

## Files

- `wc2026_win_probability.py`: the entire program (reads match history, builds Elo ratings, applies tournament-specific adjustments, determines group qualification, prints each team's win probability, and identifies which team has the highest chance of winning the World Cup).
- `results.csv`: Kaggle dataset of international football match results since 1872, with one row per match (it includes the following columns: `date`, `home_team`, `away_team`, `home_score`, `away_score`, `tournament`, `city`, `country`, and `neutral`). Source: https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017.
- `README.md`: project documentation and setup instructions.

## Dataset

The `results.csv` dataset contains data about international football matches since November 30, 1872, but the program only uses results since January 4, 2002 (using `START_DATE`), since I believe that recent matches are more predictive of current strength than decades-old results. This January 4, 2002 date, however, still covers roughly 24 years of international football matches and the last 6 World Cups (from the 2002 FIFA World Cup to the 2022 FIFA World Cup), enough for every qualified team in the 2026 FIFA World Cup to have an established and accurate Elo rating.

## Modeling Approach

### Elo Rating System

Every single team's strength is measured using the Elo rating system. Each team starts at a baseline Elo rating (called `STARTING_ELO`) and shifts up or down after each match based on how surprising the result was. This is done with a formula (in the `expected_score()` function) that estimates the home team's win probability from both teams' current ratings before a match. The real result is then compared against that prediction. This means that beating a stronger team results in a team gaining more Elo than beating a weaker one.

### K-Factor Weighting

Not every match is weighted equally when calculating a team's Elo. For example, a World Cup match result or a Euro match result matters more than a Friendly match result. To accomplish this, each match is assigned a K-Factor, which is a multiplier controlling how much that result can move a rating, based on the tournament it was played in. These K-Factors are adjustable. In this program there are 8 tiers of K-Factors (ranked from most to least important):
1. FIFA World Cup
2. UEFA Euro
3. Copa América
4. Africa Cup of Nations
5. AFC Asian Cup
6. Gold Cup
7. Qualifiers
8. Other (including Friendlies)

### Host and Debutant Adjustments

Elo adjustments have been made for this tournament's predictions in order for the outputted results to be as accurate as possible. Host nations (which includes Canada, Mexico, and the United States) have received an Elo bonus for having home advantage, as that is a crucial advantage in large football tournaments like this, while debutant nations (which includes Cape Verde, Curaçao, Jordan, and Uzbekistan) have received an Elo penalty as they lack experience at this level. It's important to note that this doesn't change a team's real historical Elo rating as these adjustments affect the results for predicting the winning percentages for the 2026 FIFA World Cup only.

### Group Qualification

There are 12 groups in the 2026 FIFA World Cup (from Group A to Group L). Each group's 4 teams are sorted by adjusted Elo. The top 2 teams in each group advance automatically based on their Elo rating, while the 12 3rd-place finishers in each group are compared against each other, also using their Elo rating, with the best 8 of the 12 advancing, leaving us with 32 teams left to compare to determine their winning percentages.

### Bradley-Terry Model

The Elo ratings of the 32 advancing teams are converted into a percentage chance of winning the tournament using the Bradley-Terry model, which is a paired-comparison ranking method that extends Elo's two-team formula to rank many (32) competitors at once.

Formula:

$$
\text{strength}_i = 10^{\text{elo}_i / 400}
$$
$$
P(\text{team } i \text{ wins}) = \frac{\text{strength}_i}{\sum_j \text{strength}_j}
$$

Implementation in `compute_win_probabilities()`:

```
def compute_win_probabilities(ratings_by_team):
    strengths = {}
    for team, rating in ratings_by_team.items():
        strengths[team] = 10 ** (rating / 400)

    total = sum(strengths.values())

    probabilities = {}
    for team, s in strengths.items():
        probabilities[team] = s / total
    return probabilities
```

It's important to note that this model is applied only to the 32 advancing teams, so their probabilities sum to 100% among themselves, with the 16 eliminated teams excluded entirely rather than being shown at 0%

## Design Decisions and Limitations

1. The starting Elo, home advantage bonus, host and debutant adjustments, and K-Factor tiers are estimates that I chose based on research, not values calculated directly from this dataset.
2. There is no knockout bracket simulation, as win probabilities for the 32 advancing teams are calculated directly from their Elo ratings using the Bradley-Terry model, rather than by simulating individual matches.
3. Because Elo is cumulative, results are only as reliable as the completeness of the match history behind them, meaning that teams with a shorter international record will have ratings that are less stable than teams with a long history of matches.

## Running the Project

To run the project you will need to have `wc2026_win_probability.py` and `results.csv` in the same directory. You will then need to run the following command:

```
python wc2026_win_probability.py
```

Once run, the program will print all 48 teams ranked by adjusted Elo, each group's qualification results, the 32 advancing teams' win probabilities, and the predicted winner/champion of the 2026 FIFA World Cup.
