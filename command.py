import subprocess

def run_commands():
    commands = [
        "python3 static_fields_covered_absolute_interclass.py input.csv",
        "python3 random_reverse_fail_all_detection.py input.csv"
    ]

    for command in commands:
        try:
            print(f"Running command: {command}")
            # Set a timeout for each command if needed
            process = subprocess.run(command, shell=True, timeout=300)  # Timeout set to 300 seconds (5 minutes)
            if process.returncode != 0:
                print(f"Command failed: {command}")
            else:
                print(f"Command succeeded: {command}")
        except subprocess.TimeoutExpired:
            print(f"Command timed out: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Command raised an error: {command}\nError: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while running: {command}\nError: {e}")

if __name__ == "__main__":
    run_commands()
