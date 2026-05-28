from typing import Any

from lib import system, log, screen_primary, screen_secondary, updates, install, uninstall, web

theme = "system"
operational_system = system.nameSO()
system_title = f'{operational_system} Programs Manager'


log.log('Start System', level='INFO')

try:
    web.start_internet_monitor()
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


    web.start_shared_log_server()
    web.wait_for_internet_connection()
    web.open_programs_manager_site(web.get_shared_log_server_port())

    updates.update_package_manager(operational_system, log.log)
    if uninstall_list:
        web.wait_for_internet_connection()
        log.log('Uninstalling programs...', level='INFO')
        uninstall.uninstall(uninstall_list, operational_system)
    if install_list:
        web.wait_for_internet_connection()
        log.log('Installing programs...', level='INFO')
        install.install(install_list, operational_system)
    if function_list:
        web.wait_for_internet_connection()
        log.log('Executing functions...', level='INFO')

    log.log('End System', level='INFO')

except Exception as e:
    log.log(f"An error occurred: {e}", level="ERROR")

finally:
    web.stop_internet_monitor()
    web.stop_shared_log_server()

