def get_questions_and_answers_from_file():
    questions = []
    answers = []

    with open('quiz-questions/plehan17.txt', 'r', encoding='KOI8-R') as file:
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
