from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

from models import *


@app.route("/")
def main():
    return "Welcome to Penn Club Review!"


@app.route("/api")
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})


@app.route("/api/test", methods=["GET"])
def test():
    clubs = Club.query.filter(Club.name.contains("p")).all()
    return jsonify([club.to_json() for club in clubs])

# GET: returns the club with the given club id
# POST: modify a club with given parameters given club code
# DELETE: Delete the specified club from the database given club code
@app.route("/api/clubs/<int:club_id>", methods=["GET","POST","DELETE"])
def clubs(club_id):
    if request.method == "GET":
        club = Club.query.get(club_id)
        
        if club is None:
            return jsonify({'error':'Club Not Found'}), 404

        return jsonify(club.to_json())

    if request.method == "POST":
        club = Club.query.get(club_id)
        
        # Abort if club does not exist
        if club is None:
            return jsonify({'error':'Club Not Found'}), 404
        
        # Get relevant club data from input json
        data = request.get_json()
        name = data.get('name')
        tags = data.get('tags')
        description = data.get('description')
        
        # Update data for all parameters passed in
        updated = False
        if name is not None:
            club.name = name
            updated = True
        if description is not None:
            club.description = description
            updated = True
        if tags is not None:
            club.tags = get_model_list(tags, Tag)
            updated = True
        
        if not updated:
            return jsonify({'error': 'At least one field to update (name, tags, description) must be non-null.'}), 400
            
        db.session.commit()
        return jsonify(club.to_json()), 200
    
    if request.method == "DELETE":
        # Aborts if club does not exist
        club = Club.query.get(club_id)
        if club is None:
            return jsonify({'error':'Club Not Found'}), 404
            
        # Deletes the specified club
        db.session.delete(club)
        
        db.session.commit()
        return "", 204
    
# GET: Returns a list of all clubs with the given string in their name
@app.route("/api/clubs/search/<club_string>", methods=["GET"])
def search_clubs(club_string):
    clubs = Club.query.filter(Club.name.contains(club_string)).all();
    return jsonify([club.to_json() for club in clubs]), 200;

# Creates a club with the given parameters
@app.route("/api/clubs", methods=["POST"])
def create_club():
    # Get relevant information from input josn
    data = request.get_json()
    club_code = data.get('code')
    club_name = data.get('name')
    club_description = data.get('description')
    club_tags = data.get('tags')
    
    # Abort if missing club code/name or if club already exists
    if club_code is None or club_name is None:
        return jsonify({'error':'Required club data missing'}), 422
    if Club.query.filter(Club.code == club_code).first() is not None:
        return jsonify({'error':'Bad Request: Club already exists'}), 400
    if Club.query.filter(Club.name == club_name).first() is not None:
        return jsonify({'error':'Bad Request: Club with this name already exists'}), 400

    # Get the list of tags, using pre-existing ones when possible
    tags_list = get_model_list(club_tags, Tag)

    # Creates the club with the input parameters
    new_club = Club(
        code=club_code, 
        name=club_name, 
        description=club_description, 
        tags=tags_list)
    db.session.add(new_club)
    db.session.commit()

    return jsonify(new_club.to_json()), 201

# Helper method to generate a list of database objects when given names and the model type
# Searches for pre-existing ones when possible, otherwise creates new
# To be used for many-to-many relationships
def get_model_list(models, model_type):
    return_list = []
    if models is not None:
        for model in models:
            result = model_type.query.filter(model_type.name == model).first()
            if result is None:
                new_model = model_type(name=model)
                return_list.append(new_model)
            else:
                return_list.append(result)
    return return_list
    
# Returns a list of all tags and the number of clubs associated with them.
@app.route("/api/tags", methods=["GET"])
def get_tags():
    tags = Tag.query.all()
    return jsonify([tag.to_json() for tag in tags])

# Returns a list of all clubs with the requested tag. Aborts if tag does not exist.
@app.route("/api/tags/<int:tag_id>", methods=["GET"])
def get_clubs_by_tag(tag_id):
    tag = Tag.query.get(tag_id)

    if tag is None:
        return jsonify({'error':'Tag Not Found'}), 404

    return jsonify([club.to_json() for club in tag.clubs]), 200

# GET: Returns user data for the user with the requested id
# DELETE: Deletes the user with the requsted id
# POST: Modifies the user with the given updated data
@app.route("/api/users/<int:id>", methods=["GET", "DELETE", "POST"])
def user(id):
    user = User.query.get(id)
    
    # Abort if user does not exist
    if user is None:
        return jsonify({'error':'User Not Found'}), 404
    
    if request.method == "GET":
        return jsonify(user.to_json()), 200
    
    if request.method == "DELETE":
        db.session.delete(user)
        db.session.commit()
        return "", 204
    
    if request.method == "POST":
        # Updates the specified user information if provided
        data = request.get_json()
        name = data.get('name')
        user_graduation_year = data.get('graduation_year')
        user_schools = data.get('schools')
        user_majors = data.get('majors')
        user_email = data.get('email')

        if user_graduation_year is not None:
            user.graduation_year = user_graduation_year
            
        # If School data provided, updates current School(s). If not in system and missing Name, abort.
        if user_schools is not None:
            user_schools = get_relation_list(user_schools, School)
            if user_schools is None:
                return jsonify({'error':'School Name Missing and School does not already exist'}), 422
            user.schools = user_schools
        
        # If Major data provided, updates current Major(s). If not in system and missing Name, abort.    
        if user_majors is not None:
            user_majors = get_relation_list(user_majors, Major)
            if user_majors is None:
                return jsonify({'error':'Major Name Missing and Major does not already exist'}), 422
            user.majors = user_majors
            
        if name is not None:
            user.name = name
            
        if user_email is not None:
            user.email = user_email
            
        db.session.commit()
        return jsonify(user.to_json()), 200

# Creates a new user with the given data
@app.route("/api/users", methods=["POST"])
def create_user():
    # Get parameters from input json
    data = request.get_json()
    user_name = data.get('name')
    user_email = data.get('email')
    user_graduation_year = data.get('graduation_year')
    user_school = data.get('school')
    user_major = data.get('major')
    
    # Aborts if no user name or email, or if user with given name/email already exists
    if user_name is None or user_email is None:
        return jsonify({'error':'User Name or Email Missing'}), 422
    if User.query.filter(User.name == user_name).first() is not None:
        return jsonify({'error':'Bad Request: User with this name already exists'}), 400
    if User.query.filter(User.email == user_email).first() is not None:
        return jsonify({'error':'Bad Request: User with this email already exists'}), 400

    # Handles School and Major data to handle None case and using pre-existing vs creating new 
    # instances of each. Also aborts if Major/School not found and no name provided.
    user_majors = get_relation_list(user_major, Major)
    if user_majors is None:
        user_majors = []
    user_schools = get_relation_list(user_school, School)
    if user_schools is None:
        user_schools = []
    
    # Creates user with given parameters
    new_user = User(
        name=user_name,
        email=user_email,
        graduation_year=user_graduation_year,
        schools=user_schools,
        majors=user_majors
    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_json()), 201

# Given a type of model and list of model instances (primarily for School and Major Data),
# returns the existing version if already in the database, otherwise creates a new one with name and id.
# Returns None if none found and no name was provided.
def get_relation_list(models, model_type):
    return_list = []
    if models is not None:
        for model in models:
            if not isinstance(model, dict) or "id" not in model:
                return None
            result = model_type.query.filter(model_type.id == model["id"]).first()
            if result is None:
                if "name" not in model:
                    return None
                new_model = model_type(id=model["id"], name=model["name"])
                return_list.append(new_model)
            else:
                return_list.append(result)
    return return_list
    
# Adds a club to a user's favorites list when passed a username.
# If club is already favorited, removes it from the list
@app.route("/api/clubs/<int:club_id>/favorite", methods=["POST"])
def add_remove_favorite(club_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id == None:
        return jsonify({'error':'Missing Required Data user_id'}), 422

    club = Club.query.get(club_id)
    user = User.query.get(user_id)

    # Abort if club or user doesn ot exist
    if club is None:
        return jsonify({'error':'Club not found'}), 404
    if user is None:
        return jsonify({'error':'User not found'}), 404

    # Logic for adding/removing club from User's favorites list
    if club in user.favorites:
        user.favorites.remove(club)
        action = "removed"
    else:
        user.favorites.append(club)
        action = "added"
        
    db.session.commit()
    return jsonify({'success': True, 'action': action}), 200

# Adds a club to a user's member list when passed a username.
# If user is already a member, removes them from the list
@app.route("/api/clubs/<int:club_id>/join", methods=["POST"])
def add_remove_member(club_id):
    data = request.get_json()
    user_id = data.get('user_id')

    # Abort if no user id provided
    if user_id is None:
        return jsonify({'error':'Missing Required Data user_id'}), 422

    club = Club.query.get(club_id)
    user = User.query.get(user_id)

    # Abort if Club or User does not exist
    if club is None:
        return jsonify({'error':'Club not found'}), 404
    if user is None:
        return jsonify({'error':'User not found'}), 404

    # Logic for adding/removing club from User's member list
    if club in user.clubs:
        user.clubs.remove(club)
        action = "left"
    else:
        user.clubs.append(club)
        action = "joined"

    db.session.commit()
    return jsonify({'success': True, 'action': action}), 200


# GET: Returns comment with the given ID
# POST: Modifies comment with the given ID
# DELETE: Removes the comment with the given id as well as all replies to that comment
@app.route("/api/comments/<int:comment_id>", methods=["DELETE", "POST", "GET"])
def comment(comment_id):
    comment = Comment.query.get(comment_id)
    
    # Aborts if comment with specified code does not exist
    if comment is None:
        return jsonify({'error':'Comment not found'}), 404

    if request.method == "GET":
        return jsonify(comment.to_json()), 200

    data = request.get_json()
    if request.method == "POST":
        comment_body = data.get('body')
        
        # Abort if missing user name or comment body
        if comment_body == None:
            return jsonify({'error':'Required data body is missing'}), 422

        comment.body = comment_body
        comment.updated_at = db.func.now()
            
        db.session.commit()
        return jsonify(comment.to_json()), 200
    
    if request.method == "DELETE":
        # Delete the comment from the database
        db.session.delete(comment)
        db.session.commit()
        return "", 204
    
@app.route("/api/clubs/<int:club_id>/comments", methods=["GET","POST"])
def comment_club(club_id):
    club = Club.query.get(club_id)
    
    # Aborts if club with specified code does not exist
    if club is None:
        return jsonify({'error':'Club not found'}), 404
    
    # Returns a list of all information for all comments obtained through the to_json() function
    if request.method == "GET":
        return jsonify(sorted([comment.to_json() for comment in club.comments if comment.parent_id is None], key=lambda item: item['created_at'])), 200
    
    data = request.get_json()
    if request.method == "POST":
        user_id = data.get('user_id')
        comment_body = data.get('body')
        parent_id = data.get('parent_id')
        
        # Abort if missing user name or comment body
        if user_id is None or comment_body is None:
            return jsonify({'error':'Required data user_id or body is missing'}), 422
        if User.query.get(user_id) is None:
            return jsonify({'error':'User not found'}), 404

        # Creates the Comment with given data
        comment = Comment(
            user_id=user_id, 
            body=comment_body, 
            club_id=club_id,
            parent_id=parent_id
        )
            
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment.to_json()), 201
    
@app.route("/api/schools", methods=["GET"])
def get_schools():
    schools = School.query.all()
    return jsonify([school.to_json() for school in schools]), 200

@app.route("/api/majors", methods=["GET"])
def get_majors():
    majors = Major.query.all()
    return jsonify([major.to_json() for major in majors]), 200

if __name__ == "__main__":
    app.run()
