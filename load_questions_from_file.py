import os
import random


def get_questions_and_answers_from_file(folder_path):
    questions = []
    answers = []

    random_file = os.path.join(
        folder_path,
        random.choice(os.listdir(folder_path))
        )

    with open(random_file, 'r', encoding='KOI8-R') as file:
        for line in file.read().split('\n\n'):
            if line.startswith('Вопрос'):
                question = ' '.join(line.split('\n')[1:]).lstrip()
                questions.append(question)
            elif line.startswith('Ответ'):
                answer = ' '.join(line.split('\n')[1:])
                answers.append(answer)

    return dict(zip(questions, answers))


if __name__ == '__main__':
    get_questions_and_answers_from_file()
