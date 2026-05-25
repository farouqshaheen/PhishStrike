import os
import sys
import time
import random
import re

# ANSI colors – Cyber Dashboard Bold Theme
LIGHT1 = "\033[1;38;2;0;255;255m"  # Neon Cyan (Bold)
LIGHT2 = "\033[1;38;2;30;144;255m"  # Electric Blue (Bold)
MEDIUM = "\033[1;38;2;0;102;204m"  # Deep Azure (Bold)
PURPLE = "\033[1;38;2;157;0;255m"  # Neon Purple (Bold)
DARK = "\033[1;38;2;80;80;80m"  # Graphite (Bold)
PINK = "\033[1;38;2;255;45;170m"  # Neon Pink (Bold)
RED = "\033[1;38;2;255;50;50m"  # Cyber Red (Bold)
RESET = "\033[0m"
WHITE = "\033[1;97m"  # Pure White (Bold)
BOLD = "\033[1m"

# RGB Tuples for Gradients
RGB_CYAN = (0, 255, 255)
RGB_BLUE = (30, 144, 255)
RGB_AZURE = (0, 102, 204)
RGB_PURPLE = (157, 0, 255)
RGB_PINK = (255, 45, 170)
RGB_RED = (255, 50, 50)
RGB_WHITE = (255, 255, 255)


def strip_ansi(text):
    """Removes ANSI escape sequences from a string."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def get_gradient_rgb(start_rgb, end_rgb, steps):
    if steps <= 1:
        yield start_rgb
        return
    for i in range(steps):
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (steps - 1))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (steps - 1))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (steps - 1))
        yield (r, g, b)


def gradient_text(text, start_rgb, end_rgb):
    """Returns text with a linear RGB gradient applied to its characters."""
    text = strip_ansi(text)
    steps = len(text)
    if steps == 0:
        return ""
    result = ""
    for i, rgb in enumerate(get_gradient_rgb(start_rgb, end_rgb, steps)):
        result += f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text[i]}"
    return result + RESET


def slow_type(text, speed=0.01, start_rgb=RGB_WHITE, end_rgb=RGB_WHITE, end="\n"):
    """Prints text slowly with a gradient."""
    text = strip_ansi(text)
    steps = len(text)
    if steps == 0:
        return
    for i, rgb in enumerate(get_gradient_rgb(start_rgb, end_rgb, steps)):
        sys.stdout.write(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text[i]}")
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write(RESET + end)
    sys.stdout.flush()


def slow_input(prompt, speed=0.01, start_rgb=RGB_WHITE, end_rgb=RGB_CYAN):
    """Replacement for input() that uses slow_type for the prompt with custom user input color."""
    slow_type(prompt, speed=speed, start_rgb=start_rgb, end_rgb=end_rgb, end="")
    # Set color for user input to a vibrant Cyan/Azure
    sys.stdout.write(f"\033[1;38;2;0;255;255m")
    sys.stdout.flush()
    res = input()
    sys.stdout.write(RESET)
    sys.stdout.flush()
    return res


def glitch_print(text, duration=0.4, start_rgb=RGB_CYAN, end_rgb=RGB_WHITE):
    """Simulates a digital glitch before showing the final text."""
    chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
    end_time = time.time() + duration
    while time.time() < end_time:
        glitched = "".join(
            c if random.random() > 0.3 or c == " " else random.choice(chars)
            for c in text
        )
        sys.stdout.write(f"\r    {gradient_text(glitched, start_rgb, end_rgb)}")
        sys.stdout.flush()
        time.sleep(0.04)
    sys.stdout.write(f"\r    {gradient_text(text, start_rgb, end_rgb)}\n")


def dynamic_border(length=66, char="━"):
    """Prints a border that flows with colors."""
    line = char * length
    print("    " + gradient_text(line, RGB_PURPLE, RGB_PINK))


def reset_color():
    sys.stdout.write(RESET + "\n")
    sys.stdout.flush()


def loading_animation(duration=5, message="Loading"):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        # Move the gradient over time for a flowing effect
        colors_cycle = [RGB_PURPLE, RGB_BLUE, RGB_CYAN, RGB_PINK]
        start_c = colors_cycle[i % len(colors_cycle)]
        end_c = colors_cycle[(i + 1) % len(colors_cycle)]

        char = chars[i % len(chars)]
        # Applying gradient to the message itself
        grad_msg = gradient_text(f"{message}... ", start_c, end_c)

        sys.stdout.write(f"\r    {DARK}\x5b{WHITE}{char}{DARK}\x5d {grad_msg} ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 80 + "\r")


def banner():
    os.system("cls" if os.name == "nt" else "clear")
    art = [
        " ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗███████╗████████╗██████╗ ██╗██╗  ██╗███████╗",
        " ██╔══██╗██║  ██║██║██╔════╝██║  ██║██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝██╔════╝",
        " ██████╔╝███████║██║███████╗███████║███████╗   ██║   ██████╔╝██║█████╔╝ █████╗  ",
        " ██╔═══╝ ██╔══██║██║╚════██║██╔══██║╚════██║   ██║   ██╔══██╗██║██╔═██╗ ██╔══╝  ",
        " ██║     ██║  ██║██║███████║██║  ██║███████║   ██║   ██║  ██║██║██║  ██╗███████╗",
        " ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝",
    ]

    colors = [RGB_PURPLE, RGB_BLUE, RGB_CYAN, RGB_PINK, RGB_AZURE]

    # Neon Flow Animation
    for frame in range(12):
        sys.stdout.write("\033[H")  # Move cursor to top-left
        start_c = colors[frame % len(colors)]
        mid_c = colors[(frame + 1) % len(colors)]
        end_c = colors[(frame + 2) % len(colors)]

        print("\n\n")
        for line in art:
            # Shift the gradient each frame
            print("    " + gradient_text(line, start_c, end_c))

        print(
            "    "
            + gradient_text(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                start_c,
                mid_c,
            )
        )
        dev_text = " [!] Cyber Security Dashboard | Developed by Farouq Shaheen & Lujain Ghatasheh "
        print("    " + gradient_text(dev_text, mid_c, end_c))
        print(
            "    "
            + gradient_text(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                end_c,
                start_c,
            )
        )
        sys.stdout.flush()
        time.sleep(0.06)

    # Final settle
    sys.stdout.write("\033[H")
    print("\n\n")
    for line in art:
        print("    " + gradient_text(line, RGB_PURPLE, RGB_CYAN))
    dynamic_border(74, "━")
    dev_text = " [!] Cyber Security Dashboard | Developed by Farouq Shaheen & Lujain Ghatasheh "
    glitch_print(dev_text, duration=0.4, start_rgb=RGB_CYAN, end_rgb=RGB_WHITE)
    dynamic_border(74, "━")


def banner_small():
    line = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print("    " + gradient_text(line, RGB_PURPLE, RGB_PINK))
    title = " [ P H I S H S T R I K E ] | PHISH STRIKE DASHBOARD "
    glitch_print(title, duration=0.3, start_rgb=RGB_CYAN, end_rgb=RGB_WHITE)
    print("    " + gradient_text(line, RGB_PINK, RGB_PURPLE))


def msg_exit():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    glitch_print(
        " [!] SHUTTING DOWN PHISHSTRIKE SYSTEMS... ",
        duration=0.6,
        start_rgb=RGB_PINK,
        end_rgb=RGB_WHITE,
    )
    print("\n")
    slow_type(
        " Thank you for using this tool. Have a good day. ",
        speed=0.03,
        start_rgb=RGB_CYAN,
        end_rgb=RGB_PURPLE,
    )
    slow_type(
        " [!] Stay Safe & Happy Hacking! ",
        speed=0.02,
        start_rgb=RGB_PURPLE,
        end_rgb=RGB_PINK,
    )
    print()
    reset_color()
    sys.exit(0)


def about(main_menu_callback=None):
    os.system("cls" if os.name == "nt" else "clear")
    banner()

    box1_top = " ╭─── [ Farouq Shaheen ] ───────────────────────────────────────"
    print(gradient_text(box1_top, RGB_PURPLE, RGB_BLUE))
    print(f"{PURPLE} │ {LIGHT2}Github {DARK}: {LIGHT1}https://github.com/farouqshaheen")
    print(
        f"{PURPLE} │ {LIGHT2}Social {DARK}: {LIGHT1}https://www.linkedin.com/in/farouq-shaheen-667b24305/"
    )
    box1_bottom = " ╰───────────────────────────────────────────────────────────"
    print(gradient_text(box1_bottom, RGB_BLUE, RGB_PURPLE))
    print()

    box2_top = " ╭─── [ Lujain Ghatasheh ] ─────────────────────────────────────"
    print(gradient_text(box2_top, RGB_PURPLE, RGB_BLUE))
    print(
        f"{PURPLE} │ {LIGHT2}Github {DARK}: {LIGHT1}https://github.com/LujainGhatasheh"
    )
    print(
        f"{PURPLE} │ {LIGHT2}Social {DARK}: {LIGHT1}https://www.linkedin.com/in/lujain-ghatasheh-7a25a5344/"
    )
    box2_bottom = " ╰───────────────────────────────────────────────────────────"
    print(gradient_text(box2_bottom, RGB_BLUE, RGB_PURPLE))

    print()
    slow_type(f" [!] Warning:", speed=0.01, start_rgb=RGB_RED, end_rgb=RGB_WHITE)
    slow_type(
        f"  This Tool is made for educational purpose only!",
        speed=0.01,
        start_rgb=RGB_RED,
        end_rgb=RGB_WHITE,
    )
    slow_type(
        f"  Authors will not be responsible for any misuse!",
        speed=0.01,
        start_rgb=RGB_RED,
        end_rgb=RGB_WHITE,
    )
    print("\n")
    slow_type(
        f"    [00] Main Menu     [99] Exit",
        speed=0.01,
        start_rgb=RGB_AZURE,
        end_rgb=RGB_CYAN,
    )
    print()

    reply = slow_input(
        f"    {DARK}\x5b{WHITE}-{DARK}\x5d{PURPLE} Select an option : {MEDIUM}{BOLD} ",
        start_rgb=RGB_WHITE,
        end_rgb=RGB_CYAN,
    )
    if reply in ["99"]:
        msg_exit()
    elif reply in ["0", "00"]:
        slow_type(
            f"    [+] Synchronizing Core... Returning to Main Menu.",
            speed=0.01,
            start_rgb=RGB_WHITE,
            end_rgb=RGB_PURPLE,
        )
        time.sleep(1)
        if main_menu_callback:
            main_menu_callback()
    else:
        print(f"\n{DARK}[{WHITE}!{DARK}]{DARK} Invalid Option, Try Again...")
        time.sleep(1)
        about(main_menu_callback)
