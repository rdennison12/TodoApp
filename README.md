# Todos App

## Commits
* Initial commit – Recreated project from scratch.
* Able to get the app back to pre-testing status.
* Completed all tests for todos 
* Unit testing completed
* Updated Pipfile
* Completed building the front-end
* Updated .gitignore
* Added to GitHub 2026-03-17
* Added requirements.txt
* Added a secret key back in auth.py
* Added a Postgres database online 




## Notes
**If creating a new project within a parent project.**\
You'll need to make sure to use the root directory structure.
For example, if your virtual environment is in the parent project, then 
you need to use the double dot (..) to find files in the parent project.
If the files are in the same directory, you can use the single dot (.) 
to refer to the current directory.
-- Bug fix:
If the page is not loading as expected, use the get_user_id_key().
This is a function that gets the proper key for the user id.


**Running the app**
Ensure to install requirements before starting the app.\
```pipenv install --dev```\
Activate the virtual environment.\
```pipenv shell```\
For FastAPI\
```uvicorn main:app --reload```\
Or\
```fastapi dev main.py```

