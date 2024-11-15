from website import *
# create_app
from website.views import * 
#  initialize_database
import flask_migrate

app=create_app()

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'

with app.app_context():
    initialize_database()

if __name__ == '__main__':
    app.run(debug=True)

braintree.Configuration.configure(
    braintree.Environment.Sandbox,  # Naudokite Sandbox aplinką testavimui
    merchant_id='7mdb87fxq3pxkpyf',
    public_key='crtgymtyhnsyy5fm',
    private_key='15348024636f389d0be0ee7e819ba686'
)