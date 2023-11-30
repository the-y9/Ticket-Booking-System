# Ticket-Booking-System
This is a Flask-based web application for managing a ticket booking system. The application allows users to sign up, log in, buy tickets for shows, and manage shows and administrators. Below is an overview of the project structure and its functionalities.

## Project Structure:
- app.py: The main Flask application file containing routes and functions.
- templates/: Contains HTML templates used by the application.
- db.db: SQLite database file containing user, show, and booking data.
- used inline css.
- README.txt: This file, providing an overview of the project.

## Getting Started:
1. Install the required packages listed in the `requirements.txt` file using `pip install -r requirements.txt`.
2. Run the application by executing `python app.py`.
3. Access the application in your web browser at `http://localhost:5000/`.

## Functionality Overview:
1. User Registration and Login:
   - Users can sign up with a unique username, password, and either email or phone number.
   - Passwords are securely hashed using bcrypt.
   - Registered users can log in using their credentials.

2. Ticket Booking:
   - Users can browse available shows and buy tickets for them.
   - The available seat count for each show is updated after booking.
   - Booking details are stored in the database.

3. Show Management (Admins only):
   - Admins can log in and access a dashboard to manage shows.
   - Admins can add, update, and delete shows with information such as name, seats, price, ratings, theatre, and location.

4. Administrator Management (Admins only):
   - Admins can add other administrators to help manage the system.

5. Email Confirmation:
   - Users receive email confirmations upon successful ticket purchases.
   - The application uses the Flask-Mail extension to send emails.

## Security Considerations:
- The application uses bcrypt for password hashing.
- The application employs basic authorization checks to restrict access to certain routes.
- However, the application could be improved by implementing more advanced security practices, such as using prepared statements and sanitizing user inputs.
