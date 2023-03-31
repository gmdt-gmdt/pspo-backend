const express = require("express");
const sqlite3 = require("sqlite3");
const bodyParser = require("body-parser");
const cors = require("cors");
const dotenv = require("dotenv");
const path = require("path");

const app = express();
dotenv.config();
const PORT = 3000;
const DEFAULT_DATA_BASE = "database/ExoQuizz.sqlite";

//middleWares
app.use(cors());
app.use(bodyParser.json());
app.use((err, req, res, next) => {
  const errorStatus = err.status || 500;
  const errorMessage = err.message || "Something went wrong!";
  return res.status(errorStatus).json({
    success: false,
    status: errorStatus,
    message: errorMessage,
    stack: err.stack,
  });
});
app.use(express.static("public"));
//index.js
app.get("/", (req, res) => {
  res.sendFile("index.html", { root: path.join(__dirname, "public") });
});

//connect to sqlite3 database
const db = new sqlite3.Database(process.env.DATA_BASE ?? DEFAULT_DATA_BASE);
createIfNotExists();

async function createIfNotExists() {
  await dbRun(
    `CREATE TABLE IF NOT EXISTS Quizz (
    id	INTEGER NOT NULL UNIQUE,
    Type	TEXT NOT NULL UNIQUE,
    Description	TEXT,
    Image	BLOB,
    PRIMARY KEY(id AUTOINCREMENT)
    );`,
    []
  );

  try {
    //TODO : vérifier que les items sont présents en BD au lieu de catch des exceptions inutiles
    await dbRun(
      `INSERT INTO Quizz (Type, Description)
    VALUES 
        (1, "PSPO I"),
        (2, "PSM I"),
        (3, "PSP I");
    `,
      []
    );
  } catch (error) {
    //console.error(error);
    //next(error);
  }

  await dbRun(`CREATE TABLE IF NOT EXISTS Questions (
    id	INTEGER NOT NULL UNIQUE,
    IdQuizz	INTEGER DEFAULT 0,
    Title	TEXT NOT NULL,
    NbAnswers	INTEGER NOT NULL DEFAULT 1,
    Explanations	TEXT,
    PRIMARY KEY(id AUTOINCREMENT),
    FOREIGN KEY(IdQuizz) REFERENCES Quizz("id")
    );`);

  await dbRun(`CREATE TABLE IF NOT EXISTS Answers (
    id	INTEGER NOT NULL UNIQUE,
    IdQuestion	INTEGER NOT NULL,
    Valid	INTEGER NOT NULL,
    Text	TEXT NOT NULL,
    PRIMARY KEY(id AUTOINCREMENT),
    FOREIGN KEY(IdQuestion) REFERENCES Questions (id)
    );`);
}

// routes
/**
 * *************************************QUESTIONS************************************
 */

app.get("/type-quiz", async (req, res, next) => {
  const query = "SELECT * FROM Quizz";
  try {
    const answers = await dbAll(query);
    res.json(answers);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//read
app.get("/questions", async (req, res, next) => {
  const query = `SELECT * FROM Questions WHERE IqQuizz = ${QUIZZ_TYPE}`;
  try {
    const questions = await dbAll(query);
    res.json(questions);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//for seraching with id
app.get("/questions/:id", async (req, res, next) => {
  const query = `SELECT * FROM Questions where id = ${req.params.id}`;
  try {
    const question = await dbAll(query);
    res.json({
      message: "success",
      data: question,
    });
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//create new question
app.post("/questions", async (req, res, next) => {
  const { Title, NbAnswers, Explanations } = req.body;
  const sql =
    "INSERT INTO Questions(Title, NbAnswers, Explanations) VALUES ($1, $2, $3)";
  const params = [Title, NbAnswers, Explanations];

  try {
    await dbRun(sql, params);
    res.json(req.body);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//updated  with id
app.patch("/questions/:id", async (req, res, next) => {
  const { Title, NbAnswers, Explanations } = req.body;
  const { id } = req.params;
  const sql =
    "UPDATE Questions SET Title = ?, NbAnswers = ?, Explanations = ? where id = ?";
  const params = [Title, NbAnswers, Explanations, id];

  try {
    await dbRun(sql, params);
    res.json(req.body);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//deleted  with id
app.delete("/questions/:id", async (req, res, next) => {
  const query = `DELETE FROM Questions WHERE id = ${req.params.id}`;
  try {
    await dbAll(query);
    res.json(req.body);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

/**
 * *************************************ANSWERS************************************
 */

//read
app.get("/answers", async (req, res, next) => {
  const query = "SELECT * FROM Answers";
  try {
    const answers = await dbAll(query);
    res.json(answers);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//for seraching with id
app.get("/answers/:id", async (req, res, next) => {
  const query = `SELECT * FROM Answers where id = ${req.params.id}`;
  try {
    const answer = await dbAll(query);
    res.json({
      message: "success",
      data: answer,
    });
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//create new answers
app.post("/answers", async (req, res, next) => {
  const { IdQuestion, Valid, Text } = req.body;
  const sql =
    "INSERT INTO Answers (IdQuestion, Valid, Text) VALUES ($1, $2, $3)";
  const params = [IdQuestion, Valid, Text];

  try {
    await dbRun(sql, params);
    res.json(req.body);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//updated  with id
app.patch("/answers/:id", async (req, res, next) => {
  const { IdQuestion, Valid, Text } = req.body;
  const { id } = req.params;
  const sql =
    "UPDATE Answers SET IdQuestion = ?, Valid = ?, Text = ? where id = ?";
  const params = [IdQuestion, Valid, Text, id];

  try {
    await dbRun(sql, params);
    res.json(req.body);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//deleted  with id
app.delete("/answers/:id", async (req, res, next) => {
  const query = `DELETE FROM Answers WHERE id = ${req.params.id}`;
  try {
    await dbAll(query);
    res.json(req.body);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//search - todo (optimal ???)
app.get("/search/:criteria/:type", async (req, res) => {
  const { criteria } = req.params;
  const { type } = req.params;

  const queryAll = `SELECT * from Questions  WHERE Questions.IdQuizz = ${type} ORDER BY random() LIMIT 1 `;
  const queryByCriteria = `SELECT * from Questions WHERE Questions.Title LIKE '%${criteria}%' AND Questions.IdQuizz = ${type}`;
  const query = criteria == "ALL" ? queryAll : queryByCriteria;

  try {
    const questions = await dbAll(query);

    const rows = [];
    for (const question of questions) {
      const _query = `SELECT * FROM Answers WHERE Answers.IdQuestion = ${question.id}`;
      const answersData = await dbAll(_query);
      rows.push({ ...question, answersData });
    }

    res.json(rows);
  } catch (error) {
    console.error(error);
    next(error);
  }
});

//utils

//services
async function dbAll(query) {
  return new Promise(function (resolve, reject) {
    db.all(query, function (err, rows) {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}
async function dbRun(query, params) {
  return new Promise(function (resolve, reject) {
    db.run(query, params, function (err, rows) {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}
//error handlers
const createError = (status, message) => {
  const err = new Error();
  err.status = status;
  err.message = message;
  return err;
};

// for starting port
app.listen(process.env.PORT || PORT, () => {
  console.log(`Quiz pspo working on port ${process.env.PORT ?? PORT}`);
});
// TODO: if the project grows ==> separate the business lines: database, services, controllers, index and app
