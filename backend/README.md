# gigagig

## Installation

### Prerequisites

- Python 3.7 or higher: Ensure you have Python installed on your machine.
- Virtual Environment Tool: Such as venv or virtualenv for creating isolated environments.
- Git: For cloning the repository.

### Setup Instructions

#### Clone the Repository

```bash
git clone https://github.com/yourusername/gigagig.git
cd gigagig
```

#### Create a Virtual Environment (using venv)

```bash
python -m venv venv
```

Activate the Virtual Environment:

On macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

#### Create a virtual environment using pyenv (macOS only)
```bash
brew install pyenv
pyenv install
```

Activate the virtual environment
```bash
pyenv shell
```

#### Install Required Dependencies

```bash
poetry install --no-root
```

#### Set Up Environment Variables

Create a .env file in the root directory and add the following variables:

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

Replace your_secret_key_here with a secure secret key.


#### Initialize the Database

```bash
flask db init

flask db migrate -m "Initial migration"

flask db upgrade
```

#### Run the Application

```
flask run
```

The application will be accessible at http://127.0.0.1:5000/.

## Packages Used
Backend:

- Python 3.12.7
- Flask
- Flask SQLAlchemy
- Flask Migrate
- Flask Login
- Flask WTF


Frontend:
- Vue.js 3
- CSS3

Bootstrap (optional for styling)


Database:
- SQLite (development)

Can be upgraded to PostgreSQL or MySQL for production


Others:
- Jinja2 Templating
- Werkzeug Security


## Contributing

We welcome contributions from the community! To contribute:


Fork the Repository: Click on the "Fork" button on GitHub.


Clone Your Fork:

```bash
git clone https://github.com/yourusername/gigagig.git
```

Create a Feature Branch:
```bash
git checkout -b feature/your-feature-name
```
Make Your Changes: Implement your feature or fix.

Commit Your Changes:

```bash
git add .

git commit -m "Add your feature"
```
Push to Your Fork:

```bash
git push origin feature/your-feature-name
```
Create a Pull Request: Go to the original repository and create a pull request from your branch.


Please ensure your code adheres to the project's coding standards and includes appropriate tests.
