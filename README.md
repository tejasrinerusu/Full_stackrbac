# Full Stack RBAC Application

## Start Application

Make sure Docker has been installed before starting application

Windows: `start.bat`

Linux: `start.sh`

## Backend

Change `psycopg2==2.9.5` -> `psycopg2-binary==2.9.5` in `requirements.txt` in order to work on Linux

### Seeding

Default data will be seeded automatically

-   #### Super User

    To seed super user. Run the following command:

    `python seed_superuser.py <email> <password>`

-   #### Normal User

    To seed normal user. Run the following command:

    `python seed_user.py <email> <password>`

-   #### Permission

    To seed permissions. Run the following command:

    `python seed_permission.py [<permission1>]`

### Endpoints

the `auth` endpoint verify user has all the permissions to use API (AND check)

the `user` endpoint provides CRUD for user

the `user_has_role` endpoint provides CRUD for user has role

the `role` endpoint provides CRUD for role

the `role_has_permission` endpoint provides CRUD for role has permission

the `permission` endpoint provides CRUD for permission

### Database

Use Postgresql docker image

Connects to Postgresql container `db:5432`

Docker compose expose Postgresql to localhost port `4000`

### Testing

Unit tests are written in `/tests` directory

Github Actions for Auto run Unit Tests is set up

### Docker Image

A `Dockerfile` is written for docker compose to spin up the backend

### FAQ

-   #### `/usr/bin/env: ‘bash\r’: No such file or directory` during docker compose:

    Make sure all the `.sh` files are using `LF` for End of Line Sequence

## Frontend

A React frontend for user to access the RBAC Application

### Docker Image

A `Dockerfile` is written for docker compose to spin up the frontend
