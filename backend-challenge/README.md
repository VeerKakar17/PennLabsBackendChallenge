# Penn Labs Backend Challenge

## Documentation

Packages Included:
- abort from flask. I imported this to allow for returning error codes when something goes wrong.
- json. This allowed for easy converting and parsing of json data when reading clubs.json

API Usage:

1. '/api/clubs/<int:club_id>' 
- [GET] Returns a club with the given `club_id`
   - Throws `404 Error` if `club_id` not found.
- [POST] Modifies club data of club with `club_id` with given parameters of `name`, `tags`, and/or `description`.
   - Input `tags` is a list of String tagnames. If a tag does not exist, creates a tag with that name.
   - Returns newly modified `Club` on success.
- [DELETE] Deletes the club with the given `club_id`
   - Returns `204` code on success.
- For [DELETE] and [POST], aborts with `Error 404` if no club has a name containing <club_name>

2. '/api/clubs' 
- [POST] Creates a club with given parameters
   - Requires `code` and `name`. Also can take in `description` and `tags` 
   - Tags creates a relation between the club and the given tag(s). Creates a new tag if none exists with the given Tag Name
   - `tags` takes in a list of String tagnames
   - Returns newly created `Club` parameters on success.
   - Aborts with `Error 422` if no club code or name is provided, or if club with this name/code already exists

3. '/api/clubs/search/<club_string>'
- [GET] Returns a list of all clubs with the given string `club_string` in the name

4. '/api/tags' 
- [GET] Returns all tags and the number of clubs associated with each one

5. '/api/tags/<int:tag_id>' 
- [GET] Returns data on all clubs associated with the tag with <tag_id>
   - Aborts with `Error 404` if no tag with the id <tag_id> exists

6. '/api/users/<int:id>' 
- [GET] Returns data for the user with the id <id> in json format.
   - Returns `name`, `graduation_year`, `school`, `major`, `clubs`, and `favorites` clubs.
- [POST] Modifies the user with the id <id> by changing the specified parameters.
   - Can change `graduation_year`, `school`(s) of study, and `major`(s).
   - `school` and `major` take in lists of dictionaries, each with 2 keys being `code` and `name`. If school or major already exists in the database, only `code` is needed. New school and major will be created if none already exists. 
   - Aborts with `Error 422` if School or Major are not already in the database and no `name` is provided.
   - Returns newly updated `User` on success.
- [DELETE] Deletes the user with the id <id> from the database.
   - Returns `204` on success.
- Aborts with `Error 404` if no user exists with the id <id>.

7. '/api/users' 
- [POST] Creates a new user with given data
   - Takes in `name`, `email`, `graduation_year`, `school`, and `major`.
   - `school` and `major` take in lists of dictionaries, each with 2 keys being `id` and `name`. If school or major already exists in the database, only `id` is needed. 
   - Aborts with `Error 422` if School or Major are not already in the database and no `name` is provided.
   - Returns newly created User on success.
- Aborts with `Error 422` if `name` or `email` is not provided.
- Aborts with `Error 400` if user with given name or email already exists.

8. '/api/clubs/<int:club_id>/favorite' 
- [POST] Adds the club with the id <club_id> to the specified user's favorites list. If club is already in their favorites list, removes it from the list.
   - Takes in `user_id`.
   - Aborts with `Error 404` if club with the ID <ID> does not exist or user with specified `name` does not exist.
   - On success, returns `success` as True and `action` as removed or added depending on the operation performed.

9. '/api/clubs/<int:club_id>/join' 
- [POST] Adds club with the id <club_id> to the specified user's member list. If club is already in this list, removes it.
   - Takes in `user_id` .
   - Aborts with `Error` 404 if club with the code <club_code> does not exist or user with specified name does not exist.
   - On success, returns `success` as True and `action` as removed or added depending on the operation performed.

10. '/api/clubs/<int:club_id>/comments' 
- [GET] Returns all comments under the club with the id <club_id> sorted by date. Also returns all replies to these comments.
- [POST] Creates a new comment under the club with the id <club_id>.
   - Requires user_id under `user_id` and text under `body`. Can also take in `parent_id` if it's replying to a comment with the specified id.
   - Aborts with `Error 422` if missing required data.
   - Aborts with `Error 404` if no comment with id `parent_id` is found.
   - Returns the newly created Comment on success with code `201`.

11. '/api/comments/<int:comment_id>'
- [GET] Returns data associated with comment with id `comment_id`
- [POST] Updates body of comment and `updated_at` timestamp to current time.
   - Requires `body` field for text to change to.
   - Returns `Error 422` if `body` missing.
- [DELETE] Deletes the comment with the given id `comment_id` and returns `422`.
- Returns `Error 404` if no comment with associated `comment_id` exists.

12. '/api/schools'
- [GET] Returns list of data associated with all schools.

13. '/api/majors'
- [GET] Returns list of data associated with all majros.

Models:
1. [Club]: 
- Stores `id` as the primary key
   - `id` is an integer incremented automatically every time a new instance is created to allow unique ids.
   - Also stores `club_code` (STRING(50)), `name` (STRING(255)), `description` (STRING(511)), and `tags`
   - Through backrefs, has access to a `members` and `favorites` list, which stores every user that joined and favorited this club. 
- `code` and `name` are indexed to allow for easy searching by club codes and names.
- Has a `to_json` function which returns `id`, `code`, `name`, `description`, `tags`, `members`, `favorites`, and `comments`
   - `members`, `comments`, and `favorites` returns the length of their respective lists

2. [Tag]:
- Stores `id` as it's primary key. Stores a list of clubs with this tagthrough back references.
   - `id` is an integer incremented automatically every time a new instance is created to allow unique ids.
   - Also has unique field `name` (STRING(50)), which is indexed to allow easy searching by tag `name`.
- Has a `to_json` function which returns `id`, `name` and `number_of_clubs`

3. [User]:
- Stores `id` as its primary key. Also stores `name` (STRING(100)), `email` (STRING(255)), `clubs`, and `favorites`, and optional `graduation_year`, `school`, `major`.
   - `id` is an integer incremented automatically every time a new instance is created to allow unique ids.
   - `school` and `major` are many-to-many relationships with a relationship table mentioned below.
- Has a `to_json` function which returns `id`, `name`, `graduation_year`, `school`, `major`, `clubs`, and `favorites`
   - `club` and `favorites` returns names of all clubs in these respective lists

4. [School]:
- Stores `id` as primary key. Also stores `code` (STRING(4)) and `name` (STRING(100)), which are the 3-4 character abbreviation and full names respectively.
   - `id` is an integer incremented automatically every time a new instance is created to allow unique ids.
- Has a `to_json` function which returns `name`, `id`, and `code`.
- Implemented with a many-to-many relationship with User described with a relationship table below.
- Has a back reference to all users in the specified school.

5. [Major]:
- Stores `id` as primary key. Also stores `code` (STRING(4)) and `name` (STRING(100)) which is the 3-4 character code and full name of the major respectively.
- Has a `to_json` function which returns `code`, `name` and `id`
- Implemented with a many-to-many relationship with User with a relationship table described below.
- There is no back reference as there is no immediate need for a list of how many students are in a specified major

6. [Comment]:
- Stores `id` as a primary key. Also stores the text `body` (STRING(511)), the poster `user`, the `club_code` this is under, the parent comment id  `parent_id` if this is a reply, and `replies` for if there are comments under this.
   - `id` increments automatically every time a new comment is created to allow for each comment to automatically have a unique id.
   - `club_code` is a back reference to the one-to-many relationship with Club, as one club can have multiple comments but one comment can only be associated with one club.
   - Stores `created_at` (datetime set to current time on creation), and `updated_at` (updated to current time each time it is updated).
- For `replies`, this is a one-to-many relationship from Comment to Comment, allowing for one Comment to be associated with multiple reply Comments.
   - Uses a back reference and remote_side to allow for a relationship between the same Model.
   - Has a cascade(all, delete-orphan) to recursively remove all replies when deleting a comment to prevent orphaned comments.
- Stores `club_id` of club and `user_id` of user as Foreign Keys.
- Indexed `parent_id`, `club_id`, `created_at`, and `user_id` to allow for easy searching by each of these parameters.
- Has a `to_json` function that returns `id`, `user` (`id` and `name`), `club_id`, `text`, `created_at`, `updated_at`, and `replies`
   - `replies` calls the `to_json` function of every comment related to this comment through replies

Many-to-Many Relationship Tables:
1. [club_tags]:
- Stores `tag_id` and `club_id` to allow multiple clubs to have multiple tags, each each tag to have multiple clubs associated with them.

2. [users_schools]:
- Stores `school_id` and `user_id` to allow for multiple users to have multiple schools (for dual degrees) and each school to store all users associated with them.

3. [users_majors]:
- Stores `major_id` and `user_id` to allow for multiple users to have multiple majors (for dual majors) and each major to store all users associated with them.

4. [club_members]:
- Stores `club_id` and `user_id` to associate each user to multiple clubs and each club to multiple users.

5. [club_favorites]:
- Stores `club_id` and `user_id` to allow each user to favorite multiple clubs, and each club to have access to multiple favoriting users.

## Installation

1. Click the green "use this template" button to make your own copy of this repository, and clone it. Make sure to create a **private repository**.
2. Change directory into the cloned repository.
3. Install `pipx`
   - `brew install pipx` (macOS)
   - See instructions here https://github.com/pypa/pipx for other operating systems
4. Install `poetry`
   - `pipx install poetry`
5. Install packages using `poetry install`.

## File Structure

- `app.py`: Main file. Has configuration and setup at the top. Add your [URL routes](https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing) to this file!
- `models.py`: Model definitions for SQLAlchemy database models. Check out documentation on [declaring models](https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/) as well as the [SQLAlchemy quickstart](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#quickstart) for guidance
- `bootstrap.py`: Code for creating and populating your local database. You will be adding code in this file to load the provided `clubs.json` file into a database.

## Developing

0. Determine how to model the data contained within `clubs.json` and then complete `bootstrap.py`
1. Activate the Poetry shell with `poetry shell`.
2. Run `python3 bootstrap.py` to create the database and populate it.
3. Use `flask run` to run the project.
4. Follow the instructions [here](https://www.notion.so/pennlabs/Backend-Challenge-862656cb8b7048db95aaa4e2935b77e5).
5. Document your work in this `README.md` file.

## Submitting

Follow the instructions on the Technical Challenge page for submission.

## Installing Additional Packages

Use any tools you think are relevant to the challenge! To install additional packages
run `poetry add <package_name>` within the directory. Make sure to document your additions.
