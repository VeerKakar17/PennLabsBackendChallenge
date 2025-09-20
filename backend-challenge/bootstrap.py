import json
import os

from app import app, db, DB_FILE

from models import *

def create_user():
    josh = User(name="Josh", email="josh@upenn.edu", graduation_year="2028",schools=
                [School(code="SEAS", name="School of Engineering and Applied Sciences")], majors=
                [Major(code="CSCI", name="Computer and Information Sciences")], clubs=[], favorites=[])
    
    db.session.add(josh)
    db.session.commit()

def load_data():
    try:
        with open('clubs.json', 'r') as club_file:
            club_data = json.load(club_file)
    except FileNotFoundError:
        print("clubs.json not found.");
        return;
    except json.JSONDecodeError:
        print("Invalid JSON format in clubs.json.");
        return;
    # Creates new clubs with the given parameters read from clubs.json.
    # For tags, checks if tag already exists in database otherwise creates a new one
    tags_list = {} 
    for club in club_data:
        new_club = Club(
            code=club['code'], 
            name=club['name'], 
            description=club['description'], 
            tags=[])
        for tag in club['tags']:
            if tag in tags_list:
                new_club.tags.append(tags_list[tag])
            else:
                new_tag = Tag(name=tag)
                tags_list[tag] = new_tag
                new_club.tags.append(new_tag)
        db.session.add(new_club)
    db.session.commit()

# No need to modify the below code.
if __name__ == "__main__":
    # Delete any existing database before bootstrapping a new one.
    LOCAL_DB_FILE = "instance/" + DB_FILE
    if os.path.exists(LOCAL_DB_FILE):
        os.remove(LOCAL_DB_FILE)

    with app.app_context():
        db.create_all()
        create_user()
        load_data()
