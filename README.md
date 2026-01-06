# Help Desk Ticket Manager

A Python Django web application for managing help desk tickets.

## Functionality
- View, create, update, and delete tickets (CRUD) 
- Central database with sample records  
- Data validation with clear error messages

## Authentication
The regular user must be logged in to create and edit a ticket. A logged in superuser can perform all CRUD functions. If a non-logged in user attempts to add, edit or delete a ticket they are redirected to the login page.

## User roles
- Regular users can create and view tickets  
- Administrators (Django superusers) have full control over all records (full CRUD) and access to the Django admin database

## Security requirements
- Evidence should include:
  - A blocked SQL injection attempt  
  - A prevented XSS attack where script content does not execute  
  - Correct handling of access restrictions when a regular user attempts to reach an admin-only page  

## Errors
Login and Signup forms have error messages and tips to help the user fill out the details.


## Dev setup
- enable virtual environment before development 

source django_env/bin/activate


## Versions
Uses Django 3.1, Python 3.10.4


## GHA workflow
Includes linting with autopep8, testing & code coverage with pytest and coverage libraries. Coverage must pass before the branch can be merged into the main codebase.

## Testing
Testing is performed using pytest. The test suite can be run manually but is always run in the branch on GitHub, within a minimum coverage set to ensure sufficient testing is made for the application. The GitHub workflow file shows the test outcome with the coverage table.

The `pyproject.toml` file has the configuration for the coverage threshold.

## Project delivery management
Using Github projects the application is planned with all component details with the individual task item. The items are tracked by their respective columns, ToDo, Backlog, InProgress, Peer Review, QA, Ready for Release and Done. The specificity of the columns allows a finer tuned tracking process to prevent any uncertainty with the status of the task. Especially when multiple tasks are being worked on in unison, such as adding authentication with the 'Create' or 'Edit' functionality for a ticket.

Project is available at: https://github.com/users/lucasshaw12/projects/2

## Branch rules
THe workflow build must pass before the branch can be merged into main. These are configured within the branch protection rules in GitHub.

## Hosting
Hosted on Heroku with gunicorn and django-heroku libraries. Changes need to be pushed to heroku with `git push heroku main`. If pushing from non main branch `git push heroku <branch_name>:main` 

Verify the Git and Heroku remote address with `git remote -v`

Heroku static files currently disabled with `heroku config:set DISABLE_COLLECTSTATIC=1`

## Heroku database access from CLI
Run `heroku pg:psql`
List all tables `\dt`
See all users `SELECT id, email, username, is_staff, is_superuser, is_active, date_joined FROM accounts_customuser ORDER BY id;`
Delete a user `DELETE FROM accounts_customuser WHERE id = 3;`

## Testing OWASP attacks
Terminal window 1 - Open a terminal and run `heroku logs -t` to show live continuous logging

Displaying logs of Heroku app for images/video. Visible in terminal and web browser console
`heroku logs -t`

For Cross Site Request Forgery (CSRF) - https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/
Should see a 403 forbidden in web browser console and heroku logs
fetch("/tickets/add",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:"title=csrf_attack&description=forged_request"}).then(r=>console.log("status:",r.status))

Broken Access Control (AKA unauthorised access to a page or action)
Ensure no user is logged in
Try to navigate to the URL - https://sedo-qa-assignment-444a66b40d4d.herokuapp.com/tickets/add
Show that the user is redirected with a 302 status code and is shown the login page

A10 Mishandling of exceptional conditions: safe error handling
Django.settings DEBUG=False to prevent showing full stack trace when an exception occurs. This could be caused by vising a resource that does not exist such as `/tickets/99999999/edit`.
Confirm the resource id does not exist in the database. 
Attempt to visit that resource in the URL. 
User sees a 404 page and not the web applications stack trace. 
Heroku terminal logs will show 404 status code. 
