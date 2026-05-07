#!/usr/bin/env python3
"""
Script to list all Windows startup programs
and facilitate the generation of a custom whitelist.
"""

import sys
import winreg


def normalize_startup_name(value):
    return ''.join(char for char in value.casefold() if char.isalnum())

def list_startup_programs():
    """Lista todos os programas de startup registrados no Windows"""
    
    reg_paths = {
        "HKEY_CURRENT_USER": (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        "HKEY_LOCAL_MACHINE (32-bit)": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        "HKEY_LOCAL_MACHINE (64-bit/WOW64)": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
    }
    
    all_programs = {}
    
    for label, (hkey, path) in reg_paths.items():
        print(f"\n{'='*60}")
        print(f"{label}")
        print(f"{'='*60}")
        
        all_programs[label] = []
        
        try:
            with winreg.OpenKey(hkey, path) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        all_programs[label].append(name)
                        print(f"  {name}")
                        i += 1
                    except OSError:
                        break
        except Exception as e:
            print(f"  Error reading registry: {e}")
    
    return all_programs

def generate_whitelist(programs):
    """Gera uma whitelist sugerida com nomes normalizados de chaves reais."""
    
    print(f"\n{'='*60}")
    print("WHITELIST SUGERIDA")
    print(f"{'='*60}")
    
    suggested = []
    keywords_microsoft = ['onedrive', 'edge', 'securityhealth', 'nearby', 'pc manager']
    keywords_gpu = ['nvidia', 'igfx', 'intel', 'amd', 'radeon', 'nvbackend', 'nvcontainer']
    keywords_utils = ['rainmeter', 'lively', 'discord', 'whatsapp', 'camo']
    
    all_names = []
    for region_programs in programs.values():
        all_names.extend(region_programs)
    
    all_names = list(set(all_names))
    all_names.sort()
    
    for name in all_names:
        lower_name = name.lower()
        should_suggest = False
        reason = ""
        
        for keyword in keywords_microsoft:
            if keyword in lower_name:
                should_suggest = True
                reason = "Microsoft/Sistema"
                break
        
        if not should_suggest:
            for keyword in keywords_gpu:
                if keyword in lower_name:
                    should_suggest = True
                    reason = "GPU Driver"
                    break
        
        if not should_suggest:
            for keyword in keywords_utils:
                if keyword in lower_name:
                    should_suggest = True
                    reason = "Utilidade/Comunicação"
                    break
        
        if should_suggest:
            normalized = normalize_startup_name(name)
            suggested.append(normalized)
            print(f"  {name:<40} -> {normalized:<30} ({reason})")
    
    return suggested

def save_whitelist(programs, filename="white_list_generated.txt"):
    """Salva a whitelist sugerida em um arquivo."""
    
    all_names = []
    for region_programs in programs.values():
        all_names.extend(region_programs)
    
    all_names = list(set(all_names))
    all_names.sort()
    
    suggested = []
    keywords = ['onedrive', 'teams', 'edge', 'cortana', 'defender', 'security',
                'nvidia', 'igfx', 'intel', 'amd', 'radeon', 'nvbackend',
                'rainmeter', 'lively', 'discord', 'slack', 'whatsapp']
    
    for name in all_names:
        lower_name = name.lower()
        for keyword in keywords:
            if keyword in lower_name:
                suggested.append(normalize_startup_name(name))
                break
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Nomes normalizados das chaves de inicializacao\n")
        for program in sorted(set(suggested)):
            f.write(program + '\n')
    
    print(f"\nArquivo salvo: {filename}")
    print(f"Total suggested programs: {len(set(suggested))}")

def main():
    print("="*60)
    print("Windows Startup Programs Lister")
    print("="*60)
    
    try:
        programs = list_startup_programs()
        suggested = generate_whitelist(programs)
        
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        
        total = sum(len(v) for v in programs.values())
        unique = len(set(sum(programs.values(), [])))
        
        print(f"Total entries found: {total}")
        print(f"Unique programs: {unique}")
        print(f"Suggested programs for whitelist: {len(set(suggested))}")
        
        # Perguntar se deseja salvar
        print(f"\n{'='*60}")
        response = input("Do you want to save suggested whitelist to file? (y/n): ").lower()
        
        if response == 'y':
            save_whitelist(programs)
            print("\nYou can edit the file and copy it to white_list.txt")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nRun this script as administrator!")
        sys.exit(1)

if __name__ == "__main__":
    main()
