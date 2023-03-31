import os.path
import json
import sqlite3
from sqlite3 import Error

db = "PSPO_v3.sqlite"
inputJson = "Untitled-3.json"

class question:
    title = ''
    nbAnswers = 0
    explanation = ''
    answers = []

class answer:
    original_id = ''
    text = ''
    valid = 0

def create_connection(db):
    conn = None
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, db)
        print("Ouverture du fichier sqlite : " + db_path)
        conn = sqlite3.connect(db_path)
        init_db(conn)
    except Error as e:
        print(e)
    return conn

def init_db(conn):
    cur = conn.cursor()
    cur.executescript("""CREATE TABLE IF NOT EXISTS Questions (
id	INTEGER NOT NULL UNIQUE,
Title	TEXT NOT NULL,
NbAnswers	INTEGER NOT NULL DEFAULT 1,
Explanations	TEXT,
PRIMARY KEY(id AUTOINCREMENT)
);
""")
    cur.executescript("""CREATE TABLE IF NOT EXISTS Answers (
id	INTEGER NOT NULL UNIQUE,
IdQuestion	INTEGER NOT NULL,
Valid	INTEGER NOT NULL,
Text	TEXT NOT NULL,
PRIMARY KEY(id AUTOINCREMENT),
FOREIGN KEY(IdQuestion) REFERENCES Questions (id)
);
""")
    #print("db initialized")
    return

def count_question(conn, title):
    cur = conn.cursor()
    cur.execute("""SELECT count(*) as counter from Questions
WHERE Title LIKE ?""", ('%'+title+'%',))
    rows = cur.fetchone()
    return rows[0]

def search_question(conn, title):
    cur = conn.cursor()
    cur.execute("""SELECT IdQuestion, Title, NbAnswers, Explanations, Answers.Text, Answers.Valid from Questions
INNER JOIN Answers on Questions.id = Answers.IdQuestion
WHERE Questions.Title LIKE ?
ORDER BY IdQuestion""", ('%'+title+'%',))
    rows = cur.fetchall()
    return rows

def insert_question(conn, q):
    cur = conn.cursor()
    cur.execute("""INSERT INTO Questions (NbAnswers, Title, Explanations) 
VALUES(?,?,?)""", (q.nbAnswers, q.title, q.explanation))
    return cur.lastrowid

def insert_answer(conn, id_question, a):
    cur = conn.cursor()
    cur.execute("""INSERT INTO Answers (IdQuestion, Valid, Text) 
VALUES(?,?,?)""", (id_question, a.valid, a.text))
    return cur.lastrowid

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
            question_feedbacks = input['result']['question_feedbacks'][str(idq)]
            q = question()
            q.title = quest['question']
            q.explanation = question_feedbacks['feedback']
            q.nbAnswers = len(question_feedbacks['correct_answer'])
            #when is array, le count is OK. otherwise it's a string with 32 char
            if q.nbAnswers == 32:
                q.nbAnswers = 1
            q.answers = []
            for answ in quest['options']:
                a = answer()
                a.original_id = answ['id']
                a.text = answ['content']                
                a.valid = answ['id'] in question_feedbacks['correct_answer']
                q.answers.append(a)
            questions.append(q)
    return questions


def insert_database(questions):
    conn = create_connection(db)
    i = 0
    with conn:
        for q in questions:
            #check if exist
            if count_question(conn, q.title) > 0:
                #print("question allready in db")
                continue
            print("new question with " + str(q.nbAnswers) + " answers !")

            #insert question
            last_id_question = insert_question(conn, q)
            print("insert : " + q.title)

            #insert answers
            for a in q.answers:
                insert_answer(conn, last_id_question, a)
            print("insert " + str(len(q.answers)) + " answers")
            conn.commit()
            i = i + 1
    return i

def main():
    print("\n\nHello")

    # load json
    questions = deserialize_json(load_json())
    print(str(len(questions)) + " questions found")

    #insert DB
    nb = insert_database(questions)
    print(str(nb) + " new questions inserted !")

    print("Bye")


if __name__ == '__main__':
    main()