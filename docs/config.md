# Config

Floodgate can be configured with a YAML file at `floodgate/config.yml`.
[floodgate/config_example.yml](../floodgate/config_example.yml) contains
default values and can be used as a template. You need to set your bot token
and also set up one or more floodgate channels.

## Basic config fields

### (root)

Fields in the root YAML object.

| Key                    | Description                                                                               |
|------------------------|-------------------------------------------------------------------------------------------|
| `bot_token` *(string)* | Your [Discord bot's](https://discord.com/developers/docs/topics/oauth2#bots) access token |

### bot

Basic bot stuff.

| Key                         | Description                              |
|-----------------------------|------------------------------------------|
| `command_prefix` *(string)* | The prefix used for calling bot commands |
| `description` *(string)*    | The bot's description                    |

### bot.modules.floodgate

You can configure multiple floodgates for different channels. Each floodgate
will open once a day.

| Key                                                              | Description                                                                                                                                                             |
|------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `channels` *(dict\[int, [FloodgateChannel](#floodgatechannel)])* | A dict of configurations for each channel that should have a floodgate. The dict keys are channel IDs and the values are [FloodgateChannel](#floodgatechannel) objects. |

#### FloodgateChannel

Each floodgate can either open at a specific time or be randomly selected
between a range of times. The `time` field specifies a specific time, and the
`time_window_start/end` fields specify a random range. These two groups of
fields cannot both be specified in the same floodgate.

| Key                                            | Description                                          |
|------------------------------------------------|------------------------------------------------------|
| `gate_open.timezone` *string*                  | Timezone to interpret times in                       |
| `gate_open.time` *string or null*              | Open the gate at a specific time                     |
| `gate_open.time_window_start` *string or null* | Open the gate at a random time starting at this time |
| `gate_open.time_window_end` *string or null*   | Open the gate at a random time ending at this time   |
| `gate_open.duration` *string*                  | How long to keep the gate open for                   |
| `messages.open` *string*                       | Message to send on gate opening                      |
| `messages.close` *string*                      | Message to send on gate closing                      |

### logging

See Python's [TimedRotatingFileHandler](https://docs.python.org/3.9/library/logging.handlers.html#logging.handlers.TimedRotatingFileHandler)
for more info about these fields.

| Key                                | Description                                                                                                                              |
|------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| `floodgate_logging_level` *string* | Floodgate logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)                                                                |                                
| `discord_logging_level` *string*   | Discord library logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)                                                          |                             
| `output_file` *string*             | Path to write log files to (can be relative to the floodgate Python module)                                                              |                
| `when` *string*                    | When to create a new log file (a unit of time or midnight) (`S`, `M`, `H`, `D`, `midnight`)                                              |                            
| `interval` *integer*               | Number of `when` intervals to write a new log file                                                                                       |                                   
| `backup_count` *integer*           | Max number of log files to keep                                                                                                          |                                   
| `format` *string*                  | The logging format string. See Python's [LogRecord documentation](https://docs.python.org/3.9/library/logging.html#logrecord-attributes) |
