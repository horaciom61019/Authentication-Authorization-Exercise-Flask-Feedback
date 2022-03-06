DROP DATABASE IF EXISTS flask_feedback;

CREATE DATABASE flask_feedback;

\c flask_feedback

CREATE TABLE users
(
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  email TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL
);