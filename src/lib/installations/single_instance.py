"""
Single Instance Control Module
This module ensures only one installation process runs at a time.
When a new installation starts, it cancels any previous installation.
"""

import os
import sys
import subprocess
import importlib

# Import psutil with automatic installation fallback
try:
    import psutil
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"])
    try:
        psutil = importlib.import_module('psutil')
    except Exception:
        sys.exit("psutil is required. Install dependencies and run again.")

try:
    from src.lib import log
except ModuleNotFoundError:
    from lib import log

# Lock file path - stores the PID of the currently running installation
LOCK_FILE = os.path.join(os.path.expanduser('~'), '.auto_install_programs.lock')


def _read_lock_file():
    """Read PID from lock file if it exists."""
    if not os.path.exists(LOCK_FILE):
        return None
    
    try:
        with open(LOCK_FILE, 'r') as f:
            return int(f.read().strip())
    except (ValueError, IOError) as e:
        log.log(f'Error reading lock file: {e}', level="WARNING")
        return None


def _write_lock_file(pid):
    """Write current PID to lock file."""
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(pid))
        log.log(f'Lock file created with PID {pid}', level="INFO")
    except IOError as e:
        log.log(f'Error writing lock file: {e}', level="ERROR")


def _remove_lock_file():
    """Remove the lock file."""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            log.log('Lock file removed', level="INFO")
    except IOError as e:
        log.log(f'Error removing lock file: {e}', level="WARNING")


def _kill_process_tree(pid):
    """Kill a process and all its children."""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Kill all children first
        for child in children:
            try:
                child.terminate()
                log.log(f'Terminated child process {child.pid}', level="INFO")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Wait for children to terminate
        gone, alive = psutil.wait_procs(children, timeout=3)
        
        # Force kill any processes that didn't terminate
        for p in alive:
            try:
                p.kill()
                log.log(f'Force killed process {p.pid}', level="WARNING")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Kill parent process
        try:
            parent.terminate()
            parent.wait(timeout=3)
            log.log(f'Terminated parent process {pid}', level="INFO")
        except psutil.TimeoutExpired:
            parent.kill()
            log.log(f'Force killed parent process {pid}', level="WARNING")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        return True
        
    except psutil.NoSuchProcess:
        log.log(f'Process {pid} no longer exists', level="INFO")
        return True
    except psutil.AccessDenied:
        log.log(f'Access denied when trying to kill process {pid}', level="ERROR")
        return False
    except Exception as e:
        log.log(f'Error killing process {pid}: {e}', level="ERROR")
        return False


def acquire_installation_lock():
    """
    Acquire the installation lock for the current process.
    If another installation is running, it will be terminated.
    Returns True if lock was successfully acquired.
    """
    current_pid = os.getpid()
    log.log(f'Current process PID: {current_pid}', level="INFO")
    
    # Check if there's an existing lock
    existing_pid = _read_lock_file()
    
    if existing_pid and existing_pid != current_pid:
        log.log(f'Found existing installation with PID {existing_pid}', level="WARNING")
        
        # Check if process is still running
        try:
            if psutil.pid_exists(existing_pid):
                log.log(f'Terminating previous installation (PID {existing_pid})', level="WARNING")
                if _kill_process_tree(existing_pid):
                    log.log(f'Successfully terminated previous installation', level="INFO")
                else:
                    log.log(f'Failed to terminate previous installation', level="ERROR")
            else:
                log.log(f'Previous installation (PID {existing_pid}) is not running', level="INFO")
        except Exception as e:
            log.log(f'Error checking previous installation: {e}', level="ERROR")
    
    # Write new lock file with current PID
    _write_lock_file(current_pid)
    return True


def release_installation_lock():
    """Release the installation lock when installation completes."""
    current_pid = os.getpid()
    existing_pid = _read_lock_file()
    
    # Only remove lock if it belongs to this process
    if existing_pid == current_pid:
        _remove_lock_file()
        log.log('Installation lock released', level="INFO")
    else:
        log.log(f'Lock file belongs to different process (PID {existing_pid}), not removing', level="WARNING")


def is_installation_cancelled():
    """
    Check if this installation has been cancelled by a newer one.
    Returns True if the lock file has been taken over by another process.
    """
    current_pid = os.getpid()
    existing_pid = _read_lock_file()
    
    # If lock file doesn't exist or belongs to another process, we've been cancelled
    if existing_pid != current_pid:
        log.log(f'Installation cancelled: lock taken by PID {existing_pid}', level="WARNING")
        return True
    
    return False
