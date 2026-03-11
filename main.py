
import subprocess
import sys

if __name__ == "__main__":
	# Prépare la commande pour lancer client.py avec les arguments éventuels
	cmd = [sys.executable, "view/client.py"] + sys.argv[1:]
	subprocess.run(cmd)


