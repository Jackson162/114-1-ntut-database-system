# Local Development
Use python 3.12.9

1.
```
python3 -m venv .venv
```
2.
`Command` + `P` 
`Shift` + `>`
`Python: Select Interpreter` -> pick `.venv`

3.
```
source .venv/bin/activate
```

4.
```
pip3 install -r requirements.txt
```

5.
run db server
```
docker-compose -f docker-compose.db.yaml up 
```

6.
set up your .env and if it is your first time running the server or there is new files in `migrations`, set `DO_INIT_DB`=true otherwise false. `DO_INIT_DB`=true will allow `alembic upgrad` during server startup.

7.
go to vscode debugger and press green arrow to run server


# DB Migrations
## create migration files
If you change the model files in `app/database/models`,

1. `pip install alembic`
2. cd into root folder of this project.
3. set up env variables, the variables defined [here](app/core/config.py).
4. create a migration file by:
```
./.venv/bin/python -m alembic revision --autogenerate -m "${revision_message}"
```

1. check the generated file in `migrations/versions`
   
## do db migration
1. set the env variable: `DO_INIT_DB` to true, and run the server.