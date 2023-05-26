from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = '9ae52ad014c879078f798507be8ac651'  # Set your secret key here

# Connect to the MySQL database
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='vinay',
    database='election_system'
)

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('index.html')

    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        voter_id = request.form['voter_id']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        age = request.form['age']
        cursor = db.cursor()
        q = "SELECT voter_id FROM admin WHERE voter_id = %s"
        cursor.execute(q, (voter_id,))
        v_id = cursor.fetchone()
        if not v_id:
            error_message = "Invalid voter ID. Please recheck and enter the Voter ID."
            return render_template('register.html', message=error_message)

        # Check if the username already exists
        query = "SELECT username FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            error_message = "Username already exists. Please choose a different one."
            return render_template('register.html', message=error_message)

        # If username does not exist, proceed with registration
        insert_query = "INSERT INTO users (id,voter_id, username, password, voted, email, age) VALUES (%s,%s, %s, %s, 0, %s, %s)"
        cursor.execute(insert_query, (voter_id,voter_id, username, password, email, age))
        db.commit()
        return render_template('login.html', message="You are successfully registered. Kindly login.")

    return render_template('register.html')


# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Perform authentication and redirect to dashboard if successful
        username = request.form['username']
        password = request.form['password']
        if username=="admin":
            if password=="admin@123":
                return redirect(url_for('admin'))
            else:
                error_message="Incorrect password"
                return render_template('login.html',error_message=error_message)
        # Perform authentication logic here
        cursor = db.cursor()
        query = "SELECT username,password FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        if user:
                session['username'] = username
                return redirect(url_for('dashboard'))
        else:
            # Authentication failed, show an error message
            error_message = 'Invalid username or password'
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')

@app.route('/candidates')
def candidates():
    # Add your code to fetch and display candidates from the database
    query = "SELECT * FROM candidates"
    cursor = db.cursor()
    cursor.execute(query)
    candidates = cursor.fetchall()
    # Close the database connection
    cursor.close()
    # Pass the candidate details to the template
    return render_template('candidates.html', candidates=candidates)

@app.route('/users')
def users():
    # Add your code to fetch and display users from the database
    cursor = db.cursor()
    query = "SELECT * FROM users"
    cursor.execute(query)
    users= cursor.fetchall()
    # Close the database connection
    cursor.close()
    # Pass the candidate details to the template
    return render_template('users.html', users=users)


# Route for the dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Process the vote submission
        candidate_name = request.form['candidate']
        update_vote_count(candidate_name)
        mark_user_voted(session['username'])
        return redirect(url_for('thankyou', candidate=candidate_name))
    
    # Retrieve and display election data
    election_data = get_election_data()
    return render_template('dashboard.html', data=election_data)

# Route for the admin page
# Route for the admin page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
            # Handle candidate registration form submission
            candidate_name = request.form['candidate_name']
            party_name=request.form['party_name']
            age=request.form['age']
            # Perform candidate registration
            cursor = db.cursor()
            insert_query = "INSERT INTO candidates (candidate_name,votes,party,age) VALUES (%s,0,%s,%s)"
            cursor.execute(insert_query, (candidate_name,party_name,age))
            db.commit()
            return render_template('admin.html', error_message="Candidate successfully registered.")
    return render_template('admin.html')

@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    if request.method == "POST":
        candidate_name = request.form['candidate_name']
        cursor = db.cursor()
        # Check if the candidate exists
        query = "SELECT * FROM candidates WHERE candidate_name = %s"
        cursor.execute(query, (candidate_name,))
        candidate = cursor.fetchone()
        
        if not candidate:
            error_message = "Candidate not found. Please enter a valid Candidate Name."
            return render_template('cancel.html',message=error_message)
        
        # Delete the candidate record from the database
        delete_query = "DELETE FROM candidates WHERE candidate_name = %s"
        cursor.execute(delete_query, (candidate_name,))
        db.commit()
        
        success_message = "Candidate registration canceled successfully."
        return render_template('cancel.html', message=success_message)
    
    return render_template('cancel.html')

# Route for the profile page
@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        # Retrieve user details from the database based on the username
        cursor = db.cursor()
        query = "SELECT voter_id,username, email, age FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if user:
            user_details = {
                'voter_id':user[0],
                'username': user[1],
                'email': user[2],
                'age': user[3]
            }
            return render_template('profile.html', user=user_details)
    
    # Redirect to the login page if the user is not authenticated
    return redirect(url_for('login'))

@app.route('/vote', methods=['POST', 'GET'])
def vote():
    if 'username' not in session:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))

    username = session['username']
    cursor = db.cursor()
    q = "SELECT voted FROM users WHERE username = %s"
    cursor.execute(q, (username,))
    vote = cursor.fetchone()

    if request.method == 'POST':
        if vote and vote[0] == 0:
            candidate_name = request.form['candidate']
            update_vote_count(candidate_name)
            mark_user_voted(session['username'])
            return redirect(url_for('thankyou', candidate=candidate_name))
        else:
            return redirect(url_for('dashboard', error_message="You have already cast your vote"))

    # Handle GET requests separately (display the voting page)
    if vote and vote[0] == 0:
        cursor = db.cursor()
        query = "SELECT party, candidate_name, votes FROM candidates"
        cursor.execute(query)
        candidates = cursor.fetchall()
        return render_template('vote.html', candidates=candidates)
    else:
        return redirect(url_for('dashboard', error_message="You have already cast your vote"))

# Function to retrieve election data from the database
def get_election_data():
    cursor = db.cursor()
    query = "SELECT party, candidate_name FROM candidates ORDER BY candidate_name ASC"
    cursor.execute(query)
    election_data = {}
    for party, candidate_name in cursor.fetchall():
        election_data[candidate_name] = {'party': party}
    return election_data


# Function to update the vote count for the selected candidate
def update_vote_count(candidate_name):
    cursor = db.cursor()
    query = "UPDATE candidates SET votes = votes+1 WHERE candidate_name = %s"
    cursor.execute(query, (candidate_name,))
    db.commit()

# Function to mark the user as voted
def mark_user_voted(username):
    cursor = db.cursor()
    query = "UPDATE users SET voted = 1 WHERE username = %s"
    cursor.execute(query, (username,))
    db.commit()

# Route for the thank you and result page
@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

def get_election_result():
    cursor = db.cursor()
    query = "SELECT candidate_name,party,votes FROM candidates ORDER BY votes DESC"
    cursor.execute(query)
    election_data = {}
    for candidate_name,party,votes in cursor.fetchall():
        election_data[candidate_name] = [votes,party]
    return election_data

@app.route('/results')
def results():
    # Retrieve and display election results
    election_data = get_election_result()
    return render_template('results.html', data=election_data)

@app.route('/logout')
def logout():
    # Clear the user's session
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
