from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=False, nullable=False)
  identify = db.Column(db.Integer, unique=True, nullable=False)
  points = db.Column(db.Integer, nullable=False, default=0)

  def __repr__(self):
    return '<User %r>' % self.name
