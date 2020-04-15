# AnimeKiller

AnimeKiller is a bot that allows you to delete Anime from your Discord server, using Google cloud vision.

## Instructions

This instructions should help you getting the bot up and running:

- Create a Google cloud account.
- Follow [this](https://cloud.google.com/vision/docs/auth) instructions by Google to generate a JSON file.
- Export your enviroment variables, like this:

**Bot token**:
```bash
export TOKEN=(token of your bot)
```
**Google cloud credentials**:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="[PATH TO JSON FILE]"
```

- Satisfy the requirements by running `pip3 -r install requirements.txt`
- Run `python3 run_bot.py`
- Enjoy an anime free life
