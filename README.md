# Lumina

## How to Install

### Install ffmpeg and to path variable

### Step 1: Install Python Virtual Environment

First, you need to install Python virtual environment. Open a command prompt and run the following command:

```bash
python -m pip install virtualenv
```

### Step 2: Activate Virtual Environment

Navigate to your project folder in the command prompt and go to the Scripts folder. Then, activate the virtual environment by running the following commands:

```bash
cd Scripts
activate
```
This will activate the virtual environment.

### Step 3: Install Dependencies

To install the project dependencies, run the following command:

```bash
python -m pip install -r requirements.txt
```

### Step 4: Run the Project

Navigate back to the Lumina folder in the Scripts directory and run the Django server. You can then click on the URL or type the IP address in a browser to access the project.

```bash
cd Lumina
ollama serve
python manage.py runserver
```

## Guidelines on Committing Changes

 When committing changes to the project, follow these guidelines:

### 1. Use Seperate Apps

Make your modules in separate Django apps to maintain code manageability. You can create a new app using the following command:

```bash
python manage.py startapp _appname_
```

This ensures that your project remains organized and scalable.

### 2. Updating Requirements.txt

If you install any additional Python library, it's essential to update the requirements.txt file. To do this, run the following command:

```bash
python -m pip freeze > requirements.txt
```

This command captures a list of all installed Python libraries and their versions and saves them to the requirements.txt file. Updating this file ensures that others can easily install the dependencies required for the project by running pip install -r requirements.txt.
