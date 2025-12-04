# Help Desk Ticket Manager

A Python Django web application for managing help desk tickets.

## Functionality
- View, create, update, and delete tickets  
- Central database with sample records  
- Data validation with clear error messages

## User roles
- Regular users can create and view tickets  
- Administrators have full control over all records (full CRUD)

## Security requirements
- Evidence should include:
  - A blocked SQL injection attempt  
  - A prevented XSS attack where script content does not execute  
  - Correct handling of access restrictions when a regular user attempts to reach an admin-only page  


## Dev setup
- enable virtual environment before development 

source django_env/bin/activate


## 
Uses Django 3.1
