# STEP 1: INSTALL PACKAGES
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from werkzeug.utils import secure_filename


# STEP 2: INITIALISE THE FLASK APP
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'

# STEP 3: DEFINE THE FOLDER WHERE IMAGES WILL BE STORED
UPLOAD_FOLDER = "static/images"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# STEP 3: INITIALISE THE FLASK APP
db = SQLAlchemy(app)

def update_rankings():
    movies = Movie.query.order_by(Movie.rating.desc()).all()
    for i, movie in enumerate(movies, start=1):
        movie.ranking = i
    db.session.commit()

# STEP 4:  CREATE TABLE
class Movie(db.Model):
    __tablename__ = 'Movie_List'
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(50), nullable=False)
    year = db.Column(Integer, nullable=False)
    description = db.Column(String(100), nullable=False)
    rating = db.Column(Integer, nullable=False)
    ranking = db.Column(Integer, nullable=False)
    review = db.Column(String(300), nullable=False)
    summary = db.Column(String(500), nullable=False)
    image_url = db.Column(String(200), nullable=False)

# STEP 5: CREATE THE DATABASE
with app.app_context():
    db.create_all()

# STEP 6: SET HOME ROUTE - DISPLAY ALL THE LIST
@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.ranking).all()
    return render_template("index.html", movies=movies)

# STEP 7: DEFINE THE FORM
class MyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired() ])
    year = StringField('Year', validators=[DataRequired() ])
    description = StringField('Description', validators=[DataRequired() ])
    rating = StringField('Rating', validators=[DataRequired() ])
    ranking = StringField('Ranking', validators=[DataRequired() ])
    review = StringField('Review', validators=[DataRequired() ])
    summary = StringField('Summary', validators=[DataRequired() ])

    # For images, accept only JPG, JPEG. and PNG files
    image_url = FileField('Movie Image', validators=[FileAllowed(['jpg','png','jpeg'],'Images only!'),
                FileRequired()
    ])

    submit = SubmitField()

# STEP 8: DEFINE THE ADD ROUTE
@app.route("/add", methods=["POST", "GET"])
def add():
    form = MyForm()
    if form.validate_on_submit():
        # Process image file
        image_file = form.image_url.data
        if image_file:
            filename = secure_filename(image_file.filename) # Secure filename

            # Ensure the upload folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])


            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path) # Save file to static/images/

            print(f"Images saved at: {image_path}") # Debugging statement

            # Create a new movie entry with the saved image path
            image_url = f"static/images/{filename}"
            print(f"Saving movie with image_url: {image_url}")
        else:
            image_url = "" # No image uploaded

        new_list = Movie(
            title = form.title.data,
            year = form.year.data,
            description = form.description.data,
            rating = form.rating.data,
            ranking = form.ranking.data,
            review = form.review.data,
            image_url = image_url,
            summary = form.summary.data
        )
        db.session.add(new_list)
        db.session.commit() # Save the changes
        update_rankings() # Update the rankings after adding
        return redirect(url_for("home")) # Redirect to homepage after adding
    else:
        print("Form errors:", form.errors)
    return render_template("add.html", form=form)

# STEP 9: DEFINE THE EDIT FORM
class EditForm(FlaskForm):
    new_rating = StringField('Edit Rating', validators=[DataRequired() ])
    new_review = StringField('Edit Review', validators=[DataRequired() ])
    submit = SubmitField('Done')

# STEP 10: ADD EDIT TASK ROUTE
@app.route("/edit/<int:id>", methods=['GET','POST'])
def edit(id):
    movie = Movie.query.get(id) # Get the movie by ID
    form = EditForm()

    if form.validate_on_submit():
        movie.rating = form.new_rating.data # Update the rating
        movie.review = form.new_review.data # Update the review
        db.session.commit() # Save the changes
        update_rankings() # Update the rankings after editing
        return redirect(url_for('home')) # Redirect to home page
    return render_template("edit.html", form=form, movie=movie)

# STEP 11: ADD DELETE TASK ROUTE
@app.route("/delete/<int:id>", methods=['GET', 'POST'])
def delete(id):
    delete_movie = Movie.query.get(id) # Get the task by ID
    if delete_movie:
        db.session.delete(delete_movie) # Delete the movie
        db.session.commit() # Save the changes
        update_rankings() # Recalculate after deletion
        return redirect(url_for('home')) # Redirect to homepage




if __name__ == '__main__':
    app.run(debug=True)


