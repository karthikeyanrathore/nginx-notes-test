from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql
from sqlalchemy import cast, literal_column


from apps.database import db

def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    # https://github.com/sqlalchemy/sqlalchemy/discussions/9910
    return func.to_tsvector(literal_column("'english'"), exp)


class Auth(db.Model):
    __tablename__ = 'auth'
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False) # TODO: hash it first
    notes = relationship("Notes", back_populates="authenticated_user", foreign_keys="Notes.authuser_id",)

    def serialize(self):
        ret = dict()
        ret["user_id"] = self.id
        ret["username"] = self.name
        return ret

class Notes(db.Model):
    __tablename__ = 'notes'
    # __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True) 
    message = Column(String, nullable=False)
    authuser_id = Column(Integer, ForeignKey("auth.id", ), nullable=False)
    # Child to parent 
    authenticated_user = relationship("Auth", back_populates="notes", foreign_keys=[authuser_id])

    # Full Text Search Indexing
    # https://stackoverflow.com/questions/42388956/create-a-full-text-search-index-with-sqlalchemy-on-postgresql
    __ts_vector__ = create_tsvector(
        cast(func.coalesce(message, ''), postgresql.TEXT)
    )
    __table_args__ = (
        Index(
            'idx_notes_fts',
            __ts_vector__,
            postgresql_using='gin'
        ),
    )


    def __repr__(self):
        return (
            "<Notes:, "
            "id: %d, "
            "message: %s, "
            "username: %s, "
        ) % (
            self.id,
            self.message,
            self.authenticated_user.name,
        )
    
    def serialize(self):
        ret = dict()
        ret["note_id"] = self.id
        ret["message"] = self.message
        ret["username"] = self.authenticated_user.name
        return ret
