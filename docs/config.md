# Config

Floodgate can be configured with a YAML file at `floodgate/config.yml`.
[floodgate/config_example.yml](../floodgate/config_example.yml) contains
default values and can be used as a template. `bot_token` is the only required
field.

## Config Fields

### (root)

Fields in the root YAML object.

| Key                    | Value                                                                                     |
|------------------------|-------------------------------------------------------------------------------------------|
| `bot_token` *(string)* | Your [Discord bot's](https://discord.com/developers/docs/topics/oauth2#bots) access token |
