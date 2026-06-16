import random
import pycountry

FLAGS = []

for c in pycountry.countries:
    FLAGS.append({
        "name": c.name,
        "code": c.alpha_2.lower()
    })


def get_question():
    correct = random.choice(FLAGS)

    wrong = random.sample(
        [f for f in FLAGS if f["name"] != correct["name"]],
        3
    )

    answers = wrong + [correct]
    random.shuffle(answers)

    return {
        "flag_url": f"https://flagcdn.com/w320/{correct['code']}.png",
        "correct": correct["name"],
        "answers": [a["name"] for a in answers]
    }