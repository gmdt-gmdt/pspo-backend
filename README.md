# Quiz Pspo api

db.sqlite - to get and save data
body-parser middleware so that JSON request bodies will be parsed into the req.body object as follows:
db.serialize makes sure that each query inside the callback runs in sequence.
Next, we get the parsed JSON request body returned by body-parser by writing:
Next, we create a prepared statement to insert data to the persons table with db.prepare. This lets us set data for the placeholders marked by the ? and also sanitizes the data to avoid SQL injection attacks.

# Todo

If the project grows ==> separate the business lines: database, services, controllers, index and app
# pspo-backend
