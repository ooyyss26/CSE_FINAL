Final Project: CSE1
Activity: Building a CRUD REST API with MySQL, Testing, and XML/JSON Output

OBJECTIVE:
Build a CRUD (Create, Read, Update, Delete) REST API using Flask and MySQL. The API must interface with a database containing at least 20 records and be capable of outputting responses in either JSON or XML format based on a URI parameter (e.g., 'format'). The project must include robust error handling, input validation, security mechanisms (like JWT), search functionality, and comprehensive unit tests covering all CRUD operations.

SETUP INSTRUCTIONS:
1.  Setup a MySQL server with a chosen database containing at least 20 records for testing.
2.  Create a new GitHub repository, initialize it with a README file, and clone it locally.
3.  Create a virtual environment, and add it to your .gitignore file.
4.  Install required libraries (e.g., flask, make_response, jsonify, request MySQL, requirements.txt).
5.  Code the Flask REST API Web Application.

REQUIREMENTS & GRADING (60 Points Total):
* **GitHub (8 pts):** Multiple commits with different timestamps.
* **CRUD Operations (16 pts):** Must contain input validations and error handling, returning appropriate HTTP status codes and correct headers.
* **CRUD Tests (8 pts):** Write test cases covering all CRUD operations, including different scenarios and edge cases.
* **Formatting Options (8 pts):** Implement XML/JSON output based on a URI 'format' parameter.
* **Search Functionality (6 pts):** Allow users to search for records based on specific criteria.
* **Security (8 pts):** Add security mechanisms to secure the API endpoints (JWT or similar).
* **Documentation (6 pts):** Update the README with setup instructions, guides, test-running instructions, and technical information (documenting popular APIs for reference).
