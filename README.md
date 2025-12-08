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
includes linting with ruff, testing & code coverage with pytest cov. Coverage must pass before the branch can be merged into the main codebase.

## Branch rules
THe workflow build must pass before the branch can be merged into main. These are configured within the branch protection rules in GitHub.

