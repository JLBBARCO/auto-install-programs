from typing import Any

from lib import system, log, screen_primary, screen_secondary, updates, install, web

theme = "system"
operational_system = system.nameSO()
system_title = f'{operational_system} Programs Manager'


try:
    primary_screen = screen_primary.ScreenPrimary(operational_system, theme, system_title)
    primary_screen.mainloop()
    primary_array = primary_screen.return_array() or []

    secondary_screen = screen_secondary.ScreenSecondary(operational_system, theme, system_title, primary_array)
    secondary_screen.mainloop()
    secondary_result: Any = secondary_screen.ScreenSecondaryReturn()

    install_list = []
    uninstall_list = []
    function_list = []

    if isinstance(secondary_result, dict):
        install_list.extend(item for item in secondary_result.get('install', []) if isinstance(item, dict))
        uninstall_list.extend(item for item in secondary_result.get('uninstall', []) if isinstance(item, dict))
        function_list.extend(item for item in secondary_result.get('function', []) if isinstance(item, dict))
    elif isinstance(secondary_result, list):
        for programs in secondary_result:
            if not isinstance(programs, dict):
                continue

            entry_type = str(programs.get('type', '')).strip().lower()
            if entry_type == 'install':
                install_list.append(programs)
            elif entry_type == 'uninstall':
                uninstall_list.append(programs)
            elif entry_type == 'function':
                function_list.append(programs)


    log.log('Start System', level='INFO')
    web.start_shared_log_server()


    updates.update_package_manager(operational_system, log.log)
    install.install(install_list, operational_system)

    log.log('End System', level='INFO')

except Exception as e:
    log.log(f"An error occurred: {e}", level="ERROR")

finally:
    web.stop_shared_log_server()

