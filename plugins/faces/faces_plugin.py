import random
import time

# noinspection PyMethodMayBeStatic
class faces:
    def __init__(self):
        pass

    def main(self, user_cmd:str, options:dict):
        time_to_sleep = options["kwargs"].get("time_to_wait", None)
        # Enter "faces time_to_wait=5" into the CLI to see this happen
        if time_to_sleep is not None:
            time.sleep(int(time_to_sleep))

        if len(options.get('args')) >= 1:
            request = options.get('args')[0]  # "faces :3c time_to_wait=5" triggers this and demonstrates use of a kwarg and arg
        else:
            request = user_cmd

        # Example use of `do_pass_cmd=True` in config.
        # Whatever the user typed to init a command, you get the EXACT thing they typed. Spaces and all.
        if request == ':3' or user_cmd == ':3':
            print(">-<")
        elif user_cmd == ":3 3:":
            print(":D D:")
        elif request == ':3c' or user_cmd == ':3c':
            print("^-^")
        elif user_cmd == 'cutesy' or request == 'cutesy':
            faces = [":3", ":D", ":3c", "^-^", "UwU", "OwO", "X3", "UvU", "T3T", "T-T"]
            print(f"{random.choice(faces)} Cutie Patootie fr!")
        else:
            print("All around me are familiar faces~~")

        return True

    def help(self):
        print(
            "An example plugin called 'Faces' to display cute faces! :3\n"
            "We have a command called 'cutesy'! Try it out!"
        )
        return True

    # This function would run every set amount of seconds IF the appropriate argument was set to an integer.
    def automatic(self):
        # Disabled in plugin.cf by "auto_task_timer=-1"
        print("WOAHUWHU!!!! :3")
