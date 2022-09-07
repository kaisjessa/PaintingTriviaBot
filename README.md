# PaintingTriviaBot
Discord bot for painting trivia

# .start [artist/title] [optional crop] [optional hard/extreme] [optional startyear-endyear]
Examples: .start title crop 1800-1900, .start artist extreme
.end to end your game
.skip to skip questions (in cropped)

# .multiplayer [artist/title] [optional hard/extreme] [optional num-questions]
Examples: .multiplayer artist hard, .multiplayer title 20
If not specified, num-questions is 10 by default
.pause to pause the game
.skip to skip a question
.end to end the game (can only be done by the player who started it)

# Settings:
artist/title: guess the artist or title of each artwork
default/crop: see the entire artwork at once, or see progressively larger fragments
default/hard/extreme: default dataset has been manually curated, hard dataset has ~28000 artworks by ~250 artists, extreme dataset has ~86000 artworks by ~3400 artists
startyear-endyear: only shows you artworks created within the specified date range
