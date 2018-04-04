from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField, PasswordField, SelectField
from wtforms.validators import Length, NumberRange, Email, InputRequired, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Super Secret Unguessable Key'


import db


@app.before_request
def before_request():
    db.open_db_connection()


@app.teardown_request
def teardown_request(exception):
    db.close_db_connection()


# Home page
@app.route('/')
def index():
    return render_template("index.html")


# Testing page
@app.route('/test')
def test():
    return render_template("test.html")


# A user's profile
@app.route('/profile')
def profile():
    return render_template("profile.html")


# A list of the user's posts
@app.route('/posts/<user_id>')
def user_posts(user_id):
    user = db.find_user_by_id(user_id)
    if user is None:
        flash('No user with id {}'.format(user_id))
        posts = []
    else:
        posts = db.posts_by_user(user_id)
    return render_template('user-posts.html', user=user, posts=posts)


@app.route('/favorites/1')
def temp_user_favorites():
    favs = db.favorites_by_user(1)
    return render_template('favorites.html', user=1, favorites=favs)


# A list of the user's posts
# @app.route('/favorites/<user_id>')
# def user_favorites(user_id):
#     user = db.find_user_by_id(user_id)
#     if user is None:
#         flash('No user with id {}'.format(user_id))
#         favs = []
#     else:
#         favs = db.favorites_by_user(user_id)
#     return render_template('favorites.html', user=user, favorites=favs)


# Adds a post to favorites
# TODO: Update to use current user when authentication gets added
# TODO: Check for duplicate favorites before adding
@app.route('/favorites/add/<post_id>')
def add_to_favorites(post_id):
    post = db.find_post_by_id(post_id)

    if post is not None:
        db.add_to_favorites(post_id)
        flash("Post {} added to favorites".format(post_id))
    else:
        flash("Post {} doesn't exist".format(post_id))
    return redirect(url_for('all_posts'))


# A user's settings
@app.route('/settings')
def settings():
    return render_template("settings.html")
  

# The form to create or edit a post
class PostForm(FlaskForm):
    product = StringField('Product (ex. Strawberries)', validators=[Length(min=1, max=40, message='Product must be between 1 and 40 characters')])
    description = StringField('Description (<150 characters)', validators=[Length(min=1, max=150, message='Description must be between 1 and 150 characters')])
    price = FloatField('Price (ex. 5.99)', validators=[NumberRange(min=0.01, max=1000, message='Price must be between $0.01 and $1000')])
    quantity = IntegerField('Quantity (ex. 100)', validators=[NumberRange(min=1, max=1000, message='Quantity must be between 1 and 1000')])
    category = SelectField('Category', choices=[('Vegetables', 'Vegetables'),
                                                ('Fruits', 'Fruits'),
                                                ('Meat', 'Meat'),
                                                ('Dairy', 'Dairy'),
                                                ('Grains', 'Grains')])
    loc = StringField('Location (ex. Indianapolis)', validators=[Length(min=1, max=40, message='Location must be between 1 and 40 characters')])

    submit = SubmitField('Save Post')


# Create a post
@app.route('/posts/create', methods=['GET', 'POST'])
def create_post():
    post_form = PostForm()

    if post_form.validate_on_submit():
            rowcount = db.create_post(post_form.price.data,
                                      post_form.quantity.data,
                                      post_form.product.data,
                                      post_form.category.data,
                                      post_form.loc.data,
                                      post_form.description.data)

            if rowcount == 1:
                flash("Post added successfully")
                return redirect(url_for('all_posts'))
            else:
                flash("New post not created")

    for error in post_form.errors:
        for field_error in post_form.errors[error]:
            flash(field_error)
    return render_template('post-form.html', form=post_form, mode='create')


# Edit a post
@app.route('/posts/edit/<id>', methods=['GET', 'POST'])
def edit_post(id):
    row = db.find_post_by_id(id)

    if row is None:
        flash("Post doesn't exist")
        return redirect(url_for('index'))

    post_form = PostForm(price=row['price'],
                         quantity=row['quantity'],
                         product=row['product'],
                         loc=row['loc'],
                         description=row['description'])

    if post_form.validate_on_submit():
        rowcount = db.update_post(post_form.price.data,
                                  post_form.quantity.data,
                                  post_form.product.data,
                                  post_form.loc.data,
                                  post_form.description.data,
                                  id)

        if rowcount == 1:
            flash("Post '{}' updated".format(post_form.product.data))
            return redirect(url_for('index'))
        else:
            flash('Post not updated')

    return render_template('post-form.html', form=post_form, mode='update')


@app.route('/posts/delete/<id>')
def delete_post_by_id(id):
    post = db.find_post_by_id(id)
    if post is None:
        flash("Post doesn't exist")
    else:
        db.delete_post_by_id(id)
        flash("Post deleted")
        return redirect(url_for('all_posts'))


# The form to create or update a user
class UserForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=1, max=50)])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('New Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Save User')


# Create a user
@app.route('/users/create', methods=['GET', 'POST'])
def create_user():
    user_form = UserForm()

    if user_form.validate_on_submit():
        user = db.find_user_by_email(user_form.email.data)

        if user is not None:
            flash("User {} already exists".format(user_form.email.data))
        else:
            rowcount = db.create_user(user_form.name.data,
                                      user_form.email.data,
                                      user_form.password.data,
                                      5.0,
                                      True)

            if rowcount == 1:
                flash("User {} created".format(user_form.email.data))
                return redirect(url_for('all_users'))
            else:
                flash("New user not created")

    return render_template('user-form.html', form=user_form, mode='create')


# Edit a post by a user's ID (primary key)
@app.route('/users/edit/<id>', methods=['GET', 'POST'])
def edit_user(id):
    row = db.find_user_by_id(id)

    if row is None:
        flash("User doesn't exist")
        return redirect(url_for('all_users'))

    user_form = UserForm(name=row['name'],
                         email=row['email'],
                         password=row['password'])

    if user_form.validate_on_submit():
        rowcount = db.update_user(user_form.name.data,
                                  user_form.email.data,
                                  user_form.password.data,
                                  id)

        if rowcount == 1:
            flash("User '{}' updated".format(user_form.email.data))
            return redirect(url_for('all_users'))
        else:
            flash('User not updated')

    return render_template('user-form.html', form=user_form, mode='update')


# Delete a user by their ID (primary key)
@app.route('/users/delete/<id>')
def delete_user_by_id(id):
    user = db.find_user_by_id(id)
    posts = db.posts_by_user(id)

    if user is None:
        flash("User doesn't exist")
        return redirect(url_for('all_users'))

    db.delete_favorite_by_user_id(id)

    for post in posts:
        db.delete_favorite_by_post_id(post[0])
        db.delete_post_by_user_id(id)

    db.delete_user_by_id(id)
    flash("User {} deleted".format(id))
    return redirect(url_for('all_users'))


# Gets a list of all the users in the database
@app.route('/users')
def all_users():
    return render_template('all-users.html', users=db.all_users())


# All the posts in the database
@app.route('/posts')
def all_posts():
    return render_template('all-posts.html', posts=db.all_posts())


if __name__ == '__main__':
    app.run()
