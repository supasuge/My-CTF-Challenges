import sys
from tabulate import tabulate
from colorama import init, Fore, Style

init(autoreset=True)  # Initialize colorama

def interpret_permission(octal_digit):
    """Interprets a single octal digit into rwx permissions."""
    octal_digit = int(octal_digit)
    return {
        'read': (octal_digit & 4) != 0,
        'write': (octal_digit & 2) != 0,
        'execute': (octal_digit & 1) != 0
    }

def colorize_permission(has_perm):
    """Returns a colorized 'Yes' or 'No' based on the permission."""
    return f"{Fore.GREEN}Yes{Style.RESET_ALL}" if has_perm else f"{Fore.RED}No{Style.RESET_ALL}"

def get_permissions_table(permissions, entity):
    """Creates a table of permissions for a given entity."""
    return [
        [f"{Fore.CYAN}{entity}{Style.RESET_ALL}", "Read", "Write", "Execute"],
        ["", colorize_permission(permissions['read']),
         colorize_permission(permissions['write']),
         colorize_permission(permissions['execute'])]
    ]

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or len(sys.argv[1]) != 3:
        print(f"{Fore.YELLOW}Usage: python3 permissions_calculator.py <3-digit-octal-permissions>{Style.RESET_ALL}")
        sys.exit(1)
    
    octal_permissions = sys.argv[1]
    entities = ["Owner", "Group", "Public"]
    
    all_tables = []
    for i, entity in enumerate(entities):
        permissions = interpret_permission(octal_permissions[i])
        all_tables.extend(get_permissions_table(permissions, entity))
        if i < len(entities) - 1:
            all_tables.append([])  # Add an empty row between tables
    
    print(f"\n{Fore.MAGENTA}File Permissions for {octal_permissions}:{Style.RESET_ALL}")
    print(tabulate(all_tables, headers="firstrow", tablefmt="fancy_grid"))