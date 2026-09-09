# NWN Logger
This is a simple logger for the game Neverwinter Nights for users who are on Linux with systemd. I repeatedly forgot to save my chat logs from RP sessions so I wanted a logger I set and forget. This is that logger.

## How it works
Once it's installed it waits for the game to open, when it does open it'll wait for it to close and when it does, it'll save the logs to either the default place in your home directory here: `~/NWN Logs` or in whatever directory you specify. It makes a timestamped folder so nothing gets overwritten. 

## Requirements 
- Linux with systemd. 
- Python 3.9+
- pipx
- Neverwinter Nights installed. 

## Install
```sh
git clone https://github.com/ErvinSabic/NWN-Logger.git
cd NWN-Logger
pipx install .
# Don't forget the dot it's very important ^
```

Once you've installed, you should be able to verify with 
```sh
which nwnlogger
```

### Configuring the Systemd service 
```sh
# In case this doesn't already exist from something else you've installed.
mkdir -p ~/.config/systemd/user
cp nwnlogger.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now nwnlogger
# Will probably say something about a symlink being created once you run that.
```

### Verify your setup
```sh
# Should say that it's running
systemctl --user status nwnlogger
# Logs that will show when certain files are saved.
journalctl --user -u nwnlogger -f 
```

## Configuring the logger
If you want to change where the logs are moved outside of the default `~/NWN Logs`, you can copy the example configuration into your own here like so: 

```sh
# -p flag on mkdir will create parent directories if they don't already exist.
mkdir -p ~/.config/nwnlogger
cp config.env.example ~/.config/nwnlogger/config.env
```

Then make your changes to that file. 

Here are all of the options:
| Variable     | What it does                              | Default                                    |
| ------------ | ----------------------------------------- | ------------------------------------------ |
| `PROC_NAME`  | Process name to watch for                 | `nwmain-linux`                             |
| `LOG_SOURCE` | Where NWN writes its logs                 | `~/.local/share/Neverwinter Nights/logs`   |
| `LOG_OUTPUT` | Where archived logs are saved             | `~/NWN Logs`                               |
| `COOLDOWN`   | Seconds between "is it running?" checks   | `120`                                      |

### Applying your changes
Once you're done making your changes to your configuration file, you just restart the systemd service by doing:
```sh
systemctl --user restart nwnlogger
```

You should be ready to go from here! Happy RPing!

---

## Uninstalling
```sh
# Squashing the logging service  
systemctl --user disable --now nwnlogger
rm ~/.config/systemd/user/nwnlogger.service

# Getting rid of the logger
pipx uninstall nwnlogger
```