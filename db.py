from flask import g
import psycopg2
import psycopg2.extras

''' Uncomment your database before working on your code, and comment it out again when pushing '''
# data_source_name = 'host=faraday.cse.taylor.edu dbname=joeyferg user=joeyferg password=kavibeda'
# data_source_name = 'host=faraday.cse.taylor.edu dbname=joeschuette user=joeschuette password=kahilewo'
# data_source_name = 'host=faraday.cse.taylor.edu dbname=rrc4 user=rrc4 password=decisage'
# data_source_name = 'host=faraday.cse.taylor.edu dbname=esmarrel user=esmarrel password=mowozate'
# data_source_name = 'host=faraday.cse.taylor.edu dbname=harrisonvdn user=harrisonvdn password=mudojose'


# Open database connection
def open_db_connection():
    g.connection = psycopg2.connect(data_source_name)
    g.cursor = g.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


# Close database connection
def close_db_connection():
    g.cursor.close()
    g.connection.close()


# Create a user
def create_user(first_name, last_name, email, password, phone, rating, active):
    query = '''
        INSERT INTO "user" (first_name, last_name, email, password, phone, rating, active)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(phone)s, %(rating)s, %(active)s)
    '''
    g.cursor.execute(query, {'first_name': first_name, 'last_name': last_name, 'email': email,
                             'password': password, 'phone': phone, 'rating': rating, 'active': active})
    g.connection.commit()
    return g.cursor.rowcount


# Find a user by their email
def find_user_by_email(email):
    g.cursor.execute('SELECT * FROM "user" WHERE email = %(email)s', {'email': email})
    return g.cursor.fetchone()


# Find a user by name
def find_user_by_id(id):
    g.cursor.execute('SELECT * FROM "user" WHERE id = %(id)s', {'id': id})
    return g.cursor.fetchone()


# Returns a list of all users
def all_users():
    g.cursor.execute('SELECT * FROM "user"')
    return g.cursor.fetchall()


# Update a user
def update_user(first_name, last_name, email, password, phone, user_id):
    query = '''
        UPDATE "user"
        SET first_name = %(first_name)s, last_name = %(last_name)s, 
            email = %(email)s, password = %(password)s, phone = %(phone)s
        WHERE id = %(id)s
    '''
    g.cursor.execute(query, {'id': user_id, 'first_name': first_name, 'last_name': last_name,
                             'email': email, 'password': password, 'phone': phone})
    g.connection.commit()
    return g.cursor.rowcount


# Delete a user by their ID
def delete_user_by_id(user_id):
    g.cursor.execute('DELETE FROM "user" WHERE id = %(user_id)s', {'user_id': user_id})
    g.connection.commit()
    return g.cursor.rowcount


# Finds a post by it's ID
def find_post_by_id(id):
    g.cursor.execute('SELECT * FROM post WHERE id = %(id)s', {'id': id})
    return g.cursor.fetchone()


# Finds all posts by a user
def posts_by_user(user_id):
    g.cursor.execute('SELECT * FROM post WHERE user_id = %(user_id)s', {'user_id': user_id})
    g.connection.commit()
    return g.cursor.fetchall()


# Creates a post
def create_post(price, quantity, product, loc, description):
    query = '''
        INSERT INTO post (price, quantity, product, loc, description)
        VALUES (%(price)s, %(quantity)s, %(product)s, %(loc)s, %(description)s)
    '''
    g.cursor.execute(query, {'price': price, 'quantity': quantity, 'product': product, 'loc': loc, 'description': description})
    g.connection.commit()
    return g.cursor.rowcount


# Returns the entire post table
def all_posts():
    g.cursor.execute('SELECT * FROM post')
    return g.cursor.fetchall()


# Updates/edits a post
def update_post(price, quantity, product, loc, description, post_id):
    query = '''
        UPDATE post 
        SET price = %(price)s, product = %(product)s, quantity = %(quantity)s, loc = %(loc)s, description = %(description)s
        WHERE id = %(id)s
    '''
    g.cursor.execute(query, {'id': post_id, 'price': price, 'quantity': quantity, 'product': product, 'loc': loc, 'description': description})
    g.connection.commit()
    return g.cursor.rowcount


# Deletes a single post by post ID
def delete_post_by_id(post_id):
    g.cursor.execute('DELETE FROM post WHERE id = %(post_id)s', {'post_id': post_id})
    g.connection.commit()
    return g.cursor.rowcount


# Deletes all posts by a user's ID
def delete_post_by_user_id(user_id):
    g.cursor.execute('DELETE FROM post WHERE user_id = %(user_id)s', {'user_id': user_id})
    g.connection.commit()
    return g.cursor.rowcount
