from app import db

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

# Table for many-to-many relationships to allow for multiple tags to be associated with multiple clubs and vice versa
club_tags = db.Table('club_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

# Table for many-to-many relationships to allow for multiple schools to be associated with multiple users for the cases of dual degrees
users_schools = db.Table('users_schools',
    db.Column('school_id', db.Integer, db.ForeignKey('school.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Table for many-to-many relationships to allow for multiple users to be associated with multiple majors for the cases of dual majors
users_majors = db.Table('users_majors',
    db.Column('major_id', db.Integer, db.ForeignKey('major.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Table for many-to-many relationships to allow for multiple users to be associated with multiple clubs and vice versa
club_members = db.Table('club_members',
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Table for many-to-many relationships to allow for multiple users to favorite multiple clubs
club_favorites = db.Table('club_favorites',
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Club (db.Model):
    __tablename__ = 'club'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True, unique=True)
    description = db.Column(db.Text(500), default="")
    tags = db.relationship('Tag', backref=db.backref('clubs'), secondary=club_tags)
    comments = db.relationship('Comment', backref=db.backref('club'), cascade="all, delete-orphan")

    # Returns club data in json format for the API
    def to_json(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'tags': [tag.name for tag in self.tags],
            'members': len(self.members),
            'favorites': len(self.favorites),
            'comments': len(self.comments)
        }
    
class Tag (db.Model):
    __tablename__ = 'tag'
    
    # Has reference to 'clubs' associated with this through backref
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    
    # Returns tag data in json format for the API
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'number_of_clubs': len(self.clubs)
        }
    
class User (db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    
    schools = db.relationship('School', secondary=users_schools, backref=db.backref('users'))
    majors = db.relationship('Major', secondary=users_majors, backref=db.backref('users'))
    clubs = db.relationship('Club', backref=db.backref("members"), secondary=club_members)
    favorites = db.relationship('Club', backref=db.backref("favorites"), secondary=club_favorites)

    # Returns non-private user data in json format for the API
    def to_json(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "graduation_year" : self.graduation_year,
            "email": self.email,
            "schools" : [s.to_json() for s in self.schools],
            "majors" : [m.to_json() for m in self.majors],
            "clubs" : [c.name for c in self.clubs],
            "favorites" : [f.name for f in self.favorites]
        }
    
class School (db.Model):
    __tablename__ = 'school'
    
    # Reference to 'users' through backref
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, index=True)

    # Returns school data in json format for the API
    def to_json(self):
        return {
            'id' : self.id,
            'code' : self.code,
            'name' : self.name,
        }
    
class Major (db.Model):
    __tablename__ = 'major'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, index=True)
    
    # Returns major data in json format for the API
    def to_json(self):
        return {
            'id' : self.id,
            'code' : self.code,
            'name' : self.name,
        }
        
class Comment (db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text(511), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    updated_at = db.Column(db.DateTime, server_default=None, onupdate=db.func.now())
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), server_default=None, index=True)

    user = db.relationship('User', backref=db.backref('comments', lazy=True))

    # One-to-many relationship between Comments to allow for replies
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side="Comment.id"), cascade="all, delete-orphan")

    # Returns Comment data in json format for the API
    def to_json(self):
        return {
            'id': self.id,
            'user': {'id': self.user_id, 'name': self.user.name},
            'club_id': self.club_id,
            'parent_id': self.parent_id,
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'replies': [reply.to_json() for reply in self.replies or []]
        }