flask db upgrade -d db_migrations
python -m loading_scripts.db_setup
flask run --debug