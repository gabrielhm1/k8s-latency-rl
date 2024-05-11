import subprocess

def delete_pod():
    bash_command = "bash /script/delete.sh"

    # Run the command
    result = subprocess.run(bash_command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    return result
