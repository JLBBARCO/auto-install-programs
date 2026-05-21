from program.lib import system
from program.lib import log, screen_primary

theme = "system"
operational_system = system.nameSO()
system_title = f'{operational_system} Programs Manager'

try:
    primary_screen = screen_primary.ScreenPrimary(operational_system, theme)
    primary_screen.mainloop()
    primary_array = primary_screen.array_json
except Exception as e:
    log.log(f"An error occurred: {e}", level="ERROR")