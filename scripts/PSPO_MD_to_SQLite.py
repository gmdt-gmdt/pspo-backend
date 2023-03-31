import os.path
import re
import sqlite3
from sqlite3 import Error

db = "ExoQuizz.sqlite"
inputMd = "290 questions PSD I.md"
quizz_id = 3

class Question:
    title:str = ''
    nbAnswers:int = 0
    explanation = ''
    answers = []

class Answer:
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
    cur.executescript("""CREATE TABLE IF NOT EXISTS Quizz (
id	INTEGER NOT NULL UNIQUE,
Type	TEXT NOT NULL UNIQUE,
Description	TEXT,
Image	BLOB,
PRIMARY KEY(id AUTOINCREMENT)
);
""")
    try:
        cur.execute("""INSERT INTO Quizz (Type, Description)
VALUES 
    (1, "PSPO I"),
    (2, "PSM I"),
    (3, "PSP I");
""")
    except Error as e:
        # allready initialized
        pass

    cur.executescript("""CREATE TABLE IF NOT EXISTS Questions (
id	INTEGER NOT NULL UNIQUE,
IdQuizz	INTEGER DEFAULT 0,
Title	TEXT NOT NULL,
NbAnswers	INTEGER NOT NULL DEFAULT 1,
Explanations	TEXT,
PRIMARY KEY(id AUTOINCREMENT),
FOREIGN KEY(IdQuizz) REFERENCES Quizz("id")
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
    conn.commit()
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
AND IqQuizz = ?
ORDER BY IdQuestion""", ('%'+title+'%',), quizz_id)
    rows = cur.fetchall()
    return rows

def insert_question(conn, q):
    cur = conn.cursor()
    cur.execute("""INSERT INTO Questions (IdQuizz, NbAnswers, Title, Explanations) 
VALUES(?,?,?,?)""", (quizz_id, q.nbAnswers, q.title, q.explanation))
    return cur.lastrowid

def insert_answer(conn, id_question, a):
    cur = conn.cursor()
    cur.execute("""INSERT INTO Answers (IdQuestion, Valid, Text) 
VALUES(?,?,?)""", (id_question, a.valid, a.text))
    return cur.lastrowid

def load_md():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    md_path = os.path.join(BASE_DIR, inputMd)
    print("Ouverture du fichier Markdown : " + md_path)
    with open(md_path) as file:
        file_content = file.read()
    return file_content

def extract(input):
    questions = []
    splited = input.split("**")
    
    for s in splited:
        q = Question()
        q.nbAnswers = 0
        q.answers = []
        lignes = s.split("\n")
        for l in lignes:
            if (l == ""):
                continue

            #question
            if l.startswith("### "):
                q.title = l.removeprefix("### ")

            #answer valid
            elif l.startswith("- [x] "):
                a = Answer()
                a.text = l.removeprefix("- [x] ")
                a.valid = 1
                q.answers.append(a)
                q.nbAnswers = q.nbAnswers + 1

            #answer invalid
            elif l.startswith("- [ ] "):
                a = Answer()
                a.text = l.removeprefix("- [ ] ")
                a.valid = 0
                q.answers.append(a)

            #suite de la question
            elif len(q.answers) == 0:
                q.title = q.title + "\n" + l

            #other ??
            else:
                print("ERROR !")

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
            i += 1
    return i

def main():
    print("\n\nHello")

    # load MarkDown
    questions = extract(load_md())
    print(str(len(questions)) + " questions found")

    #insert DB
    nb = insert_database(questions)
    print(str(nb) + " new questions inserted !")

    print("Bye")


if __name__ == '__main__':
    main()