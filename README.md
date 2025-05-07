# Event Management App with RBAC

## Step 1:

- Seperated each router for each part of the app (eg. auth has auth_router for login/signup)
- Auth has been separated into dependencies, routes, schemas, service and utils
  - dependencies.py: functions to get current user details from cookies and check their roles
  - routes.py: contains all signup, login and logout endpoints
  - schemas.py: contains models for user when signing up and logging in
  - service.py: contains Service class that divides the tasks into class methods for modularization
  - utils.py: contains all helper functions such as decoding and encoding JSON web tokens
- Database initialization and all main models such as User, Event etc. are in a separate db folder

## Step 2:

- Added another router for events (event_router)
- Events folder has also been separated into routes, schemas, and service
  - routes.py: contains all event creation, edit, search, update and delete endpoints
  - schemas.py: contains models for event creation and registration
  - service.py: contains the main class that updates the database with each method
- Added Stripe payment method
  - all payment methods and routing is done in payments folder
