DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS event;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT,
  google_id TEXT UNIQUE,
  provider TEXT NOT NULL	
);

CREATE TABLE event (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  user_id INTEGER NOT NULL,
  start TEXT NOT NULL, 
  end TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  display TEXT,
  notified INTEGER DEFAULT 0,
  FOREIGN KEY(user_id) REFERENCES user(id)
)