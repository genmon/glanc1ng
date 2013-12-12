# Useful pages

http://blog.y3xz.com/blog/2012/08/16/flask-and-postgresql-on-heroku/
https://devcenter.heroku.com/articles/getting-started-with-python
http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
http://ryaneshea.com/lightweight-python-apps-with-flask-twitter-bootstrap-and-heroku
http://blog.miguelgrinberg.com/post/flask-migrate-alembic-database-migration-wrapper-for-flask
http://stackoverflow.com/questions/19323990/flask-migrate-not-creating-tables
https://github.com/mattupstate/flask-social-example
http://pythonhosted.org/Flask-Social/

# Postgres

http://www.moncefbelyamani.com/how-to-install-postgresql-on-a-mac-with-homebrew-and-lunchy/

To have launchd start postgresql at login:
    ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents
Then to load postgresql now:
    launchctl load ~/Library/LaunchAgents/homebrew.mxcl.postgresql.plist
Or, if you don't want/need launchctl, you can just run:
    postgres -D /usr/local/var/postgres

(I did the first two.)

lunchy start postgres
