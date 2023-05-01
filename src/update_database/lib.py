import shutil

# Get the terminal size
terminal_size = shutil.get_terminal_size().columns
# Create a string of "-" characters with the same length as the terminal width
kugiri = lambda x: str(x) * (terminal_size//len(str(x)))