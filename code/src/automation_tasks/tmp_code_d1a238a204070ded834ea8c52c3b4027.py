import shutil

# Source path
src = r'E:\final hackathon\gaipl-ai-agents\inbound\appname.txt'

# Destination path
dst = r'E:\final hackathon\gaipl-ai-agents\outbound'

try:
    shutil.copy(src, dst)
    print("File copied successfully!")
except FileNotFoundError:
    print("The source file does not exist.")
except PermissionError:
    print("Permission denied. Ensure you have the right permissions.")
except Exception as e:
    print(f"An error occurred: {e}")