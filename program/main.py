from lib import system, log, screen_primary, screen_secondary

theme = "system"
operational_system = system.nameSO()
system_title = f'{operational_system} Programs Manager'


try:
    primary_screen = screen_primary.ScreenPrimary(operational_system, theme, system_title)
    primary_screen.mainloop()
    primary_array = primary_screen.return_array() or []

    secondary_screen = screen_secondary.ScreenSecondary(operational_system, theme, system_title, primary_array)
    secondary_screen.mainloop()
    secondary_array = secondary_screen.ScreenSecondaryReturn() or {}

    install_list = []
    uninstall_list = []
    function_list = []

    for programs in secondary_array.values():
        for item in programs:
            if not isinstance(item, dict):
                continue

            entry_type = str(item.get('type', '')).strip().lower()
            if entry_type == 'install':
                install_list.append(item)
            elif entry_type == 'uninstall':
                uninstall_list.append(item)
            elif entry_type == 'function':
                function_list.append(item)

    log.log(
        f"Collected selections: install={len(install_list)}, uninstall={len(uninstall_list)}, function={len(function_list)}",
        level="INFO",
    )

except Exception as e:
    log.log(f"An error occurred: {e}", level="ERROR")