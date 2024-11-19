from website.auth import*
from website.views import * 
from website.models import *
from website import *
app=create_app()

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'

with app.app_context():
    initialize_database()

if __name__ == '__main__':
    app.run(debug=True)


