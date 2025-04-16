# HypnoBot config package
import os
import sys
from pathlib import Path

# Add paths for proper importing
current_path = Path(__file__).resolve().parent
hypnobot_path = current_path.parent
project_path = hypnobot_path.parent.parent

# Add paths to sys.path if they're not there
if str(hypnobot_path) not in sys.path:
    sys.path.append(str(hypnobot_path))
if str(project_path) not in sys.path:
    sys.path.append(str(project_path))

# Print path diagnostics for debugging
print(f"Config path: {current_path}")
print(f"Hypnobot path: {hypnobot_path}")
print(f"Project path: {project_path}")
print(f"sys.path: {sys.path}") 