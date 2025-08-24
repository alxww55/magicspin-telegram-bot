"""
Captcha generator for user authorization

This module does following:
- Chooses control emoji for verification
- Generates random emoji keyboard from emoji-base
"""

import random

emojis_list = ["🦆", "🐳", "🦅", "🐘", "🐈", "⭐", "🌗", "🌚", "🦈", "🥨", "🍓", "🍔", "🌎", "🍏", "🎮", "🧁", "🦋", "🎱"]

def choose_control_emoji(emojis_list) -> str:
    """
    Select a random emoji as the control emoji for captcha.

    Args:
        emojis_list (list): List of emoji strings.

    Returns:
        str: The randomly chosen control emoji.
    """
    return random.choice(emojis_list)

def generate_captcha_items(correct_emoji: str) -> list:
    """
    Generate a list of 4 captcha emojis including the correct one in random order.

    Args:
        correct_emoji (str): The emoji that the user must click to pass the captcha.

    Returns:
        list: List of 4 emojis (3 random + 1 correct), shuffled.
    """
    emojis_list.remove(correct_emoji)
    generated_items = random.sample(emojis_list, 3) + [correct_emoji]
    random.shuffle(generated_items)
    return generated_items