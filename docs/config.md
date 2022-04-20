# Config

Floodgate can be configured with a JSON file at `floodgate/config.json`.
[floodgate/config_example.json](../floodgate/config_example.json) contains
default values and can be used as a template. `bot_token` is the only required
field.

## Config Fields

### (root)

Fields in the root JSON object.

| Key                    | Value                                                                                     |
|------------------------|-------------------------------------------------------------------------------------------|
| `bot_token` *(string)* | Your [Discord bot's](https://discord.com/developers/docs/topics/oauth2#bots) access token |
