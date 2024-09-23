import random
import time

# noinspection PyMethodMayBeStatic
class faces:
    def __init__(self):
        pass

    def main(self, user_cmd:str, options:dict):
        time_to_sleep = options["kwargs"].get("time_to_wait", None)
        custom_face = options["kwargs"].get("face", None)
        # Enter "faces time_to_wait=5" into the CLI to see this happen
        if time_to_sleep is not None:
            time.sleep(int(time_to_sleep))

        do_rave = "rave" in options["args"]
        do_crab = "crab" in options["args"]

        # Enter "faces crab" into the CLI to see this happen or "faces crab rave" for a crab rave
        if do_crab:
            for i in range(100 if not do_rave else 20):
                print("🦀" * 10)
                if not do_rave:
                    print("CRAB RAVE! :3")
                else:
                    # rainbowify the text
                    rainbow = [
                        "\033[31m",
                        "\033[91m",
                        "\033[93m",
                        "\033[32m",
                        "\033[34m",
                        "\033[36m",
                        "\033[35m",
                        "\033[95m",
                        "\033[94m",
                        "\033[96m",
                    ]
                    for a in range(3):
                        print(f"{random.choice(rainbow)}CRAB RAVE! :3")
                        print("🦀🌈" * 5)
                        time.sleep(0.2)
                        if random.randint(0, 4) == 2:
                            print("WOAHUWHU!!!! x3")
                time.sleep(0.2)

        if len(options.get('args')) >= 1:
            request = options.get('args')[0]  # "faces :3c time_to_wait=5" triggers this and demonstrates use of a kwarg and arg
        else:
            request = user_cmd

        if custom_face:
            print(custom_face if not do_rave else f"RAVEEEEEEEE!!! {custom_face}")
            return True

        # Example use of `do_pass_cmd=True` in config.
        # Whatever the user typed to init a command, you get the EXACT thing they typed. Spaces and all.
        if request == ':3' or user_cmd == ':3':
            print(f">-< {'Rave scawwy' if do_rave else ''}")
        elif user_cmd == ":3 3:":
            print(f":D {'RAVEEEEEEEE!!!' if do_rave else ''} D:")
        elif request == ':3c' or user_cmd == ':3c':
            print(f"^-^ {'ya like raves?' if do_rave else ''}")
        elif user_cmd == 'cutesy' or request == 'cutesy':
            faces = [":3", ":D", ":3c", "^-^", "UwU", "OwO", "X3", "UvU", "T3T", "T-T"]
            print(f"{'RAVEEEEEE!!!!' if do_rave else ''}{random.choice(faces)} Cutie Patootie fr!")
        else:
            print(f"All around me are familiar faces{' in the rave~' if do_rave else ''}~~")

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
