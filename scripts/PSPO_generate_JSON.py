import os.path
import json

inputJson = "Exam-Bertrand.json"

class question:
    title = ''
    nbAnswers = 0
    explanation = ''
    original_id = 0
    answers = []
    user_answer = []

class answer:
    original_id = ''
    text = ''
    valid = 0


def load_json():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(BASE_DIR, inputJson)
    print("Ouverture du fichier JSON : " + json_path)
    with open(json_path) as file:
        file_content = file.read()
    input = json.loads(file_content)
    return input

def deserialize_json(input):
    questions = []
    for pages in input['result']['test_sections'][0]['pages']:
        for quest in pages['contents']:
            idq = quest['id']
            #question_feedbacks = input['result']['question_feedbacks'][str(idq)]
            q = question()
            q.title = quest['question']
            #q.explanation = question_feedbacks['feedback']
            q.original_id = quest['id']
            q.user_answer = []

            if (len(quest['user_answer']) == 32):
                q.user_answer.append(quest['user_answer'])
            else :
                for ua in quest['user_answer']:
                    q.user_answer.append(ua)
            #q.nbAnswers = len(question_feedbacks['correct_answer'])
            #when is array, le count is OK. otherwise it's a string with 32 char
            #if q.nbAnswers == 32:
            #    q.nbAnswers = 1
            q.answers = []
            for answ in quest['options']:
                a = answer()
                a.original_id = answ['id']
                a.text = answ['content']                
                a.valid = 0 #answ['id'] in question_feedbacks['correct_answer']
                q.answers.append(a)
            
            questions.append(q)
    return questions

def print_json(questions):
    print("   \"question_feedbacks\": {")
    for q in questions:
        print("      \"" + str(q.original_id) + "\": {")
        print("        \"question_id\": " + str(q.original_id) + ",")
        print("        \"feedback\": null,")
        print("        \"correct_answer\": [")
        for a in q.answers:
            print("          //\"" + str(a.original_id) + "\",")
        print("        ],")
        print("      },")
    print("   }")    
    return

def print_question(questions):
    i = 1
    print("-----------")
    for q in questions:
        print("[Question " + str(i) + "] " + str(q.original_id))
        print(q.title)
        for a in q.answers:
            print("\t" + str(a.original_id)+ "\t" + str(a.text))
        print("Bertrand answer :")
        for ua in q.user_answer:
            print("\t" + ua)
        print("-------------------------------------------------------\n\n")
        i = i + 1
    return

def main():
    print("\n\nHello")

    # load json
    questions = deserialize_json(load_json())
    print(str(len(questions)) + " questions found")

    #generate JSON answer
    #print_json(questions)
    print_question(questions)

    print("Bye")


if __name__ == '__main__':
    main()