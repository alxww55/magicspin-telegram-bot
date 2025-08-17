import random

emojis_list = ["🦆", "🐳", "🦅", "🐘", "🐈", "⭐", "🌗", "🌚", "🦈", "🥨", "🍓", "🍔", "🌎", "🍏", "🎮", "🧁", "🦋", "🎱"]

def choose_control_emoji(emojis_list) -> str:
    return random.choice(emojis_list)

def generate_captcha_items(correct_emoji: str) -> list:
    emojis_list.remove(correct_emoji)
    generated_items = random.sample(emojis_list, 3) + [correct_emoji]
    random.shuffle(generated_items)
    return generated_items