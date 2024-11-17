from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for,jsonify, abort,session
from flask_login import login_required, current_user
from website.models import *
from . import db
import json
from .models import User, Component
from collections import Counter
from datetime import datetime, timedelta
views = Blueprint('views', __name__)
import flask_sqlalchemy
import braintree
from flask_login import logout_user, current_user
# from .admin import *





    






def get_components():
    return Component.query.all()  # Gauti visus komponentus iš duomenų bazės

@views.route('/components', methods=['GET'])
def view_components():
    sort_by = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')

    components = get_components()  # Gauti visus komponentus

    # Jei nėra komponentų, grąžinti pranešimą
    if not components:
        return render_template('components.html', message="No components found.")

    # Rūšiavimas
    if sort_by == 'name':
        components.sort(key=lambda x: x.name, reverse=(order == 'desc'))
    elif sort_by == 'price':
        components.sort(key=lambda x: (x.price is None, x.price), reverse=(order == 'desc'))
    elif sort_by == 'rating':
        components.sort(key=lambda x: (x.rating is None, x.rating), reverse=(order == 'desc'))

    return render_template('components.html', components=components)

@views.route('/balance')
@login_required
def balance():
    user = current_user
    return render_template('balance.html', balance=user.balance)






@views.route('/add_funds', methods=['GET', 'POST'])
@login_required
def add_funds():
    if request.method == 'POST':
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        
        if payment_method == 'credit_card':
            card_number = request.form.get('card_number')
            card_expiry = request.form.get('card_expiry')
            card_cvc = request.form.get('card_cvc')
            
        
        if amount is None or payment_method is None:
            flash('Both fields are required.', 'error')
            return render_template('add_funds.html')
        
        print(f"Amount: {amount}, Payment Method: {payment_method}")  # Debugging line
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Please enter a positive number', 'error')
            else:
                if payment_method == 'braintree':
                    # Braintree integration logic
                    try:
                        # Get nonce from Braintree
                        nonce = request.form.get('payment_method_nonce')
                        # Create a Braintree transaction
                        result = braintree.Transaction.sale({
                            'amount': str(amount),
                            'paymentMethodNonce': nonce,
                            'options': {
                                'submitForSettlement': True
                            }
                        })
                        if result.is_success:
                            # Successful payment
                            current_user.balance += amount  # Assuming you have a balance field in your User model
                            db.session.commit()  # Commit the changes
                            flash('Funds successfully added!', 'success')
                            return redirect(url_for('views.success'))  # Redirect to a success page
                        else:
                            # Payment error
                            flash('An error occurred while processing the payment: ' + result.message, 'error')
                    except Exception as e:
                        flash('An unexpected error occurred: ' + str(e), 'error')

                elif payment_method == 'paypal':
                    # PayPal integration logic
                    # Implement your PayPal logic here
                    pass

                else:
                    flash('Unknown payment method', 'error')
        except ValueError:
            flash('Please enter a valid number', 'error')

    return render_template('add_funds.html')

@views.route('/',methods=["POST","GET"])
@login_required
def home(): #When going to HomePage this function runs
    items = current_user.cartItems
    if items.startswith("[") and items.endswith("]"):
        items =items[1:-1]
    while "[]" in items:
        items = items.replace("[]", "")
    current_user.cartItems = items
    db.session.commit()
    return render_template("home.html",user=current_user)







@views.route("/update", methods=['GET', 'POST'])
@login_required
def update():
    if request.method=="POST":
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        new_password = request.form.get('newPassword')
        Country = request.form.get('Country')

        user = User.query.filter_by(email=email).first()
        if user:
            user.email = email
            user.first_name = first_name
            user.Country = Country

            if new_password:
                import hashlib
                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                user.password = hashed_password
            db.session.commit()
            flash("The user has been successfully updated",category="success")
        return redirect(url_for('views.catalog'))

    return render_template("update.html",user=current_user)


@views.route("/delete", methods=['GET', 'POST'])
@login_required
def delete():
            
            db.session.delete(current_user)
            db.session.commit()

            logout_user()
            flash("The user been successfully deleted",category="success")

            return redirect(url_for('auth.login'))



def initialize_database():
    components_to_delete = Component.query.all()
    for component in components_to_delete:
        db.session.delete(component)
    db.session.commit()    
    db.create_all()

    #Add CPUs
    cpu1 = Component(name='Intel Core i9-9900K', description='8-Core, 16-Thread, 3.6 GHz (5.0 GHz Turbo) LGA 1151 Processor', image_url='Untitled copy 2.png', price=499.99, stock=5)
    cpu2 = Component(name='AMD Ryzen 7 5800X', description='8-Core, 16-Thread, 3.8 GHz (4.7 GHz Boost) AM4 Processor', image_url='Untitled copy 3.png', price=449.99, stock=8)
    cpu3 = Component(name='Intel Core i5-10600K', description='6-Core, 12-Thread, 4.1 GHz (4.8 GHz Turbo) LGA 1200 Processor', image_url='Untitled copy 4.png', price=279.99, stock=10)
    

    # Commit the changes to the database
    db.session.add_all([cpu1,cpu2,cpu3])
    db.session.commit()

    # Add GPUs
    gpu1 = Component(name='NVIDIA GeForce RTX 3080', description='10 GB GDDR6X, 8704 CUDA Cores, PCIe 4.0, Ray Tracing', image_url='Untitled copy.png', price=799.99, stock=3)
    gpu2 = Component(name='AMD Radeon RX 6800 XT', description='16 GB GDDR6, 72 Ray Accelerators, PCIe 4.0, Infinity Cache', image_url='images/Untitled.png', price=649.99, stock=6)
    gpu3 = Component(name='NVIDIA GeForce GTX 1660 Super', description='6 GB GDDR5, 1408 CUDA Cores, PCIe 3.0', image_url='Untitled1.jpg', price=249.99, stock=12)

    # Commit the changes to the database
    db.session.add_all([gpu1, gpu2, gpu3])
    db.session.commit()






@views.route('/add_component', methods=['GET', 'POST'])
@login_required
def add_component():
    if request.method == 'POST':
        # Gauti visus formos laukus
        component_name = request.form.get('name')
        component_description = request.form.get('description')
        component_price = request.form.get('price')
        component_image_url = request.form.get('image_url')
        component_stock = request.form.get('stock')

        # Patikrinkite, ar visi būtini laukai užpildyti
        if not all([component_name, component_description, component_price, component_image_url, component_stock]):
            flash('All fields are required!', 'danger')
            return render_template('views.add_component.html')  # Grąžina šabloną su klaida

        # Sukurti naują komponentą
        new_component = Component(
            name=component_name,
            description=component_description,
            price=float(component_price),  # Paverskite į float
            image_url=component_image_url,
            stock=int(component_stock)  # Paverskite į int
        )

        # Pridėti komponentą į duomenų bazę
        db.session.add(new_component)
        db.session.commit()

        flash('Component added successfully!', 'success')
        return redirect(url_for('views.add_component'))  # Nukreipia į komponentų peržiūros puslapį

    return render_template('add_component.html')  # Grąžina šabloną, kai užklausa GETThis is also a valid response


def is_loyal_customer(user_id):
    # Nustatykite laikotarpį (pvz., paskutiniai 6 mėnesiai)
    time_threshold = datetime.now() - timedelta(days=180)

    # Gauti užsakymus per nustatytą laikotarpį
    orders = Order.query.filter(Order.user_id == user_id, Order.date >= time_threshold).all()

    # Patikrinkite, ar pirkimų skaičius viršija 3
    if len(orders) > 3:
        return True

    # Patikrinkite, ar išlaidų suma viršija 500€
    total_spent = sum(order.amount for order in orders)
    if total_spent > 500:
        return True

    return False
def apply_discount(user_id, total_amount):
    if is_loyal_customer(user_id):
        discount = total_amount * 0.1  # Pavyzdžiui, 10% nuolaida
        return total_amount - discount
    return total_amount

@views.route('/create_order', methods=['POST'])
@login_required
def create_order():
    user_id = request.form.get('user_id')
    amount = float(request.form.get('amount'))

    # Pritaikykite nuolaidą
    final_amount = apply_discount(user_id, amount)

    # Sukurkite užsakymą
    new_order = Order(user_id=user_id, amount=final_amount)
    db.session.add(new_order)
    db.session.commit()

    return f"Order created with final amount: {final_amount}€"
@views.route("/catalog", methods=['GET', 'POST'])
@login_required
def catalog():
    components = Component.query.all()
    #TO DELETE ALL USERS - AT YOUR OWN RISK
    #components_to_delete = User.query.all()
    #for component in components_to_delete:
        #db.session.delete(component)
    #db.session.commit()
    currencyMultiplier = 0
    currencySymbol="None"
    if current_user.Country == "LT":
        currencyMultiplier = 1.10
        currencySymbol = "€"
    if current_user.Country == "USA":
        currencyMultiplier = 1
        currencySymbol = "$"

    if request.method =="POST":
        if 'CompoID' in request.form:
            CompoID= request.form.get('CompoID')
            if CompoID:
                return redirect(url_for('views.order', CompoID=CompoID))
    return render_template('catalog.html', components=components, user=current_user, currencyMultiplier=currencyMultiplier,currencySymbol=currencySymbol)



def get_user_orders(user_id):
    return Order.query.filter_by(user_id=user_id).all()


@views.route("/order/<CompoID>",methods=['GET','POST'])
@login_required
def order(CompoID):
    user_orders = get_user_orders(current_user.id)
    print(f"User  ID: {current_user.id}, Orders: {user_orders}")  # Debugging line
    currencyMultiplier = 0
    currencySymbol="None"
    if current_user.Country == "LT":
        currencyMultiplier = 1.10
        currencySymbol = "€"
    if current_user.Country == "USA":
        currencyMultiplier = 1
        currencySymbol = "$"


    components = Component.query.all()
    if current_user.is_authenticated:
        user_id = current_user.get_id()
    else:
        flash('You need to log in to add items to your cart', category='danger')
        return redirect(url_for('auth.login'))
    
    # Get the component ID from the URL query parameter
    compo_id = request.args.get('componentID')
    component = Component.query.filter_by(id=CompoID).first()
    # Query the database for the corresponding component
    id2 = CompoID
    if request.method == 'POST':
        id2 = CompoID
        if id2 is not None:  # Check if compo_id is not None
            if current_user.cartItems == "Empty" or current_user.cartItems=="":
                current_user.cartItems = str(id2)
            else:
                current_user.cartItems += "," + str(id2)
            db.session.commit()
            flash("The component has been successfully added to your cart!", category="success")
            return redirect(url_for('views.home'))
        else:
            flash("No component ID provided!", category="error")
            return redirect(url_for('views.home'))
        
    return render_template('order.html', component=component, user=current_user,currencyMultiplier=currencyMultiplier,currencySymbol=currencySymbol)



def get_user_orders(user_id):
    return Order.query.filter_by(user_id=user_id).all()

@views.route("/userOrders",methods=["GET","POST"])
@login_required
def userOrders():

    currencyMultiplier = 0
    currencySymbol="None"
    if current_user.Country == "LT":
        currencyMultiplier = 1.10
        currencySymbol = "€"
    if current_user.Country == "USA":
        currencyMultiplier = 1
        currencySymbol = "$"

    userID = request.args.get('userID')
    user = User.query.get(userID)
    components = Component.query.all()
    user_orders = Order.query.filter_by(user_id=userID).all()

    return render_template('userOrders.html',user=user,user_orders=user_orders,components=components, get_component_names=get_component_names,currencyMultiplier=currencyMultiplier,currencySymbol=currencySymbol)
    
def get_component_names(order_items):
    # Clean the input string
    order_items = order_items.strip("[]")  # Remove "[" and "]"
    if order_items == "Empty":
        return "No items"

    ids = order_items.split(',')
    component_names = []
    for id in ids:
        id = id.strip()  # Remove leading/trailing whitespace
        if id:  # Check if the ID is not empty
            try:
                id = int(id)
                component = Component.query.get(id)
                if component:
                    component_names.append(component.name)
            except ValueError:
                pass  # Skip non-integer IDs
    return ', '.join(component_names)










# import jwt
# from flask_mail import Mail, Message



# # Mail konfigūracija
# views.config['MAIL_SERVER'] = 'smtp.example.com'  # Pakeiskite su savo SMTP serveriu
# views.config['MAIL_PORT'] = 587  # Paprastai 587 arba 465
# views.config['MAIL_USE_TLS'] = True
# views.config['MAIL_USERNAME'] = 'your_email@example.com'  # Jūsų el. paštas
# views.config['MAIL_PASSWORD'] = 'your_password'  # Jūsų slaptažodis
# views.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'  # Jūsų el. paštas

# mail = Mail(views)



# def send_confirmation_email(user):
#     token = jwt.encode({'confirm': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
#                        'your_secret_key', algorithm='HS256')
#     confirmation_url = url_for('confirm_email', token=token, _external=True)
    
#     subject = "Please confirm your email"
    
#     # Naudojame render_template, kad sugeneruotume HTML laišką
#     html_body = render_template('confirmation_email.html', confirmation_url=confirmation_url)
    
#     msg = Message(subject, recipients=[user.email])
#     msg.html = html_body  # Pridedame HTML turinį
#     mail.send(msg)

# @views.route('/confirm_email/<token>')
# def confirm_email(token):
#     try:
#         data = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
#         user = User.query.get(data['confirm'])
#         if user:
#             user.is_verified = True  # Pridėkite is_verified lauką prie User modelio
#             db.session.commit()
#             return "Email confirmed!"
#     except:
#         return "The confirmation link is invalid or has expired."


# def send_promotional_email():
#     users = User.query.filter_by(is_verified=True).all()
#     subject = "Check out our latest promotions!"
#     body = "Here are some great deals just for you!"

#     for user in users:
#         msg = Message(subject, recipients=[user.email])
#         msg.body = body
#         mail.send(msg)


from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user

@views.route("/cartPage", methods=["GET", "POST"])
@login_required
def cartPage():
    # Naudokite current_user, kad gautumėte prisijungusio vartotojo informaciją
    user = current_user

    # Patikrinkite, ar vartotojas turi krepšelio prekių
    if user.cartItems and user.cartItems != "Empty":
        items = user.cartItems
        # Paversti stringą į sąrašą
        ComponentsID = [int(item.strip()) for item in items.split(',') if item.strip()]
    else:
        ComponentsID = []

    ComponentsID.sort()

    # Gauti bendrą kainą
    total_price = 0
    for CompoID in ComponentsID:
        component = Component.query.filter_by(id=CompoID).first()
        if component:
            price = getPrice(component)
            total_price += price

    # Gauti komponentus žodyną, kad išsaugotumėte kiekį ir komponentų ID
    ID_counter = {}
    for ID in ComponentsID:
        ID_counter[ID] = ID_counter.get(ID, 0) + 1

    uniqueComponents = set(ComponentsID)

    component_unique_list = []
    for ids in uniqueComponents:
        componentIterative = Component.query.filter_by(id=ids).first()
        if componentIterative:
            component_unique_list.append(componentIterative)

    sum1 = 0
    for ids in ComponentsID:
        componentIterative = Component.query.filter_by(id=ids).first()
        if componentIterative:
            if componentIterative.isOnSale:
                sum1 += getPrice(componentIterative) * componentIterative.priceModifier
            else:
                sum1 += getPrice(componentIterative)

    # Nustatyti valiutos simbolį ir dauginimo koeficientą
    currencyMultiplier = 0
    currencySymbol = "None"
    if current_user.Country == "LT":
        currencyMultiplier = 1.10
        sum1 *= currencyMultiplier
        currencySymbol = "€"
    elif current_user.Country == "USA":
        currencyMultiplier = 1
        sum1 *= currencyMultiplier
        currencySymbol = "$"

    return render_template('cartPage.html', user=current_user, ComponentsID=ComponentsID,
                           ID_counter=ID_counter, components_list=component_unique_list, sum1=sum1,
                           currencyMultiplier=currencyMultiplier, currencySymbol=currencySymbol)
@views.route("/DeleteFromCart",methods=["GET","POST"])
@login_required
def DeleteFromCart():
    if request.method=="POST":
        items = current_user.cartItems
        userItemList = [int(item) for item in items.split(',') if item.strip()]
        ID = request.form.get('ID')
        AMOUNT = request.form.get('AMOUNT')


        deleted_count = 0
        while int(deleted_count) < int(AMOUNT):
            userItemList.remove(int(ID))
            deleted_count += 1
        current_user.cartItems = str(userItemList)
        if current_user.cartItems =="":
            current_user.cartItems=="Empty"
        db.session.commit()
        redirect(url_for('views.catalog'))

    return render_template("DeleteFromCart.html",user=current_user)

@views.route("/FinalizingOrder",methods=["GET","POST"])
@login_required
def FinalizingOrder():
    if request.method == "POST":
        #Retrieve Cost
        items = current_user.cartItems
        while "[]" in items:
            items = items.replace("[]", "")
        if items !="Empty":
            ComponentsID = [int(item) for item in items.split(',') if item.strip()]
        else:
            # Handle the case where user.cartItems is None, for example:
            ComponentsID = []
        ComponentsID.sort()
        current_user_id = User.getUserId(current_user)

        #Get the total Price
        amount=0
        for CompoID in ComponentsID:
            component = Component.query.filter_by(id=CompoID).first()
            if component:
                if component.isOnSale:
                    price = getPrice(component) * component.priceModifier
                    amount+=price
                if component.isOnSale==False:
                    price = getPrice(component)
                    amount+=price

        #Remove order from the stock
        flag = True
        for component_id in ComponentsID:
            component = Component.query.filter_by(id=component_id).first()
            if component:
                if component.stock >= 1:
                    component.stock -= 1
                    db.session.commit()
                else:
                    flag = False
                    flash("You have ordered more than we currently have in stock!",category="danger")
                    return redirect(url_for('views.cartPage'))
        #Retrieve Info
        if flag == True:
            address = request.form.get('address')
            userOrder = Order(address=address,amountPaid=amount,orderItems=items,user_id=current_user.id)

            user = current_user
            user.cartItems = "Empty"

            db.session.add(userOrder)
            db.session.commit()
        return redirect(url_for('views.recipt'))
    return render_template("FinalizingOrder.html",user=current_user)

@views.route("/recipt",methods=["GET","POST"])
@login_required
def recipt():

    currencyMultiplier = 0
    currencySymbol="None"
    if current_user.Country == "LT":
        currencyMultiplier = 1.10
        currencySymbol = "€"
    if current_user.Country == "USA":
        currencyMultiplier = 1
        currencySymbol = "$"


    #Retrieve information on the newest order of the current user
    newest_order = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).first()

    address = newest_order.address
    order_id = newest_order.id
    amount= newest_order.amountPaid
    date = newest_order.orderDate

    items = newest_order.orderItems
    while "[]" in items:
        items = items.replace("[]", "")
    if items !="Empty":
        ComponentsID = [int(item) for item in items.split(',') if item.strip()]
    else:
        # Handle the case where user.cartItems is None, for example:
        ComponentsID = []
    ComponentsID.sort()
    
    ID_counter = {}
    for ID in ComponentsID:
        if ID in ID_counter:
         ID_counter[ID] += 1
        else:
            ID_counter[ID] = 1

    uniqueComponents = set(ComponentsID)
    component_unique_list=[]
    for ids in uniqueComponents:
    # Retrieve the component with the given ID and append it to the list
        componentIterative = Component.query.filter_by(id=ids).first()
        if componentIterative:
            component_unique_list.append(componentIterative)
    

    return render_template("recipt.html",user=current_user, address=address, order_id=order_id,amount=amount,components_list=component_unique_list,ID_counter=ID_counter,date=date,currencyMultiplier=currencyMultiplier,currencySymbol=currencySymbol)






@views.route("/addComment",methods=["GET","POST"])
@login_required
def addComment():
    
    if request.method == 'POST':
        comment_data = request.form.get('comment_data')

        if not comment_data:
            flash(' Fields are required to fullfill', 'danger')
        else:
            new_comment = Comment(comment_data=comment_data,user_id=current_user.id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment has been added!', 'success')
            return redirect(url_for('views.home'))

    return render_template('addComment.html',user=current_user)




@views.route("/ViewComments", methods=["GET", "POST"])
@login_required
def ViewComments():
    comments = Comment.query.all()  # Išimkite filtravimą pagal tipą
    return render_template('ViewComments.html', user=current_user, comments=comments)



@views.route('/delete-comment',methods=['POST'])
@login_required
def delete_comment():
    comment=json.loads(request.data)
    commentId = comment['commentId']
    comment=Comment.query.get(commentId)
    if comment:
        if comment.user_id == current_user.id:
            db.session.delete(comment)
            db.session.commit()

    return jsonify({})

@views.route("/ViewMyComments", methods=["GET", "POST"])
@login_required
def ViewMyComments():
    comments = Comment.query.filter_by(user_id=current_user.id).all()
    return render_template('ViewMyComments.html',user=current_user, comments=comments)






@views.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    currencyMultiplier = 0
    currencySymbol = "None"
    
    if current_user.Country == "LT":
        currencyMultiplier = 1.10
        currencySymbol = "€"
    elif current_user.Country == "USA":
        currencyMultiplier = 1
        currencySymbol = "$"

    users = User.query.all()
    components = Component.query.all()
    return render_template('admin.html', user=current_user, users=users, components=components, currencySymbol=currencySymbol, currencyMultiplier=currencyMultiplier)





def CompoUpdate():
    components = Component.query.all()

    if request.method=="POST":
        ID = request.form.get('ID')
        NewName = request.form.get('NewName')
        Description = request.form.get('Description')
        imageName = request.form.get('imageName')
        Price = request.form.get('Price')
        Stock = request.form.get('Stock')

        component = Component.query.filter_by(id = ID).first()
        if component:
            component.NewName = NewName
            component.Description = Description
            component.imageName = imageName
            component.Price = Price
            component.Stock = Stock

            db.session.commit()
        flash("The Component has been successfully updated",category="success")

    return render_template('CompoUpdate.html',user=current_user, components=components)

@views.route("/CompoDelete",methods=["GET","POST"])
@login_required
def CompoDelete():
    components = Component.query.all()
    if request.method=="POST":
        ID = request.form.get('ID')
        component = Component.query.filter_by(id=ID).first()
        if component:
            db.session.delete(component)
            db.session.commit()
        return redirect(url_for('views.admin'))
    return render_template("CompoDelete.html",user=current_user,components=components)

@views.route("/CompoCreate",methods=["GET","POST"])
@login_required
def CompoCreate():
    

    components = Component.query.all()
    if request.method=="POST":
        NewName = request.form.get('NewName')
        Description = request.form.get('Description')
        imageName = request.form.get('imageName')
        Price = request.form.get('Price')
        Stock = request.form.get('Stock')

        if not NewName or not Description or not imageName or not Price or not Stock:
            flash('Please fill out all fields', 'error')
        else:
            try:
                newComponent = Component(
                    name=NewName, 
                    description=Description, 
                    image_url=imageName, 
                    price=float(Price), 
                    stock=int(Stock), 
                    isOnSale=False, 
                    priceModifier=1
                )

                db.session.add(newComponent)
                db.session.commit()
                return redirect(url_for('views.admin'))
            except ValueError:
                flash('Please enter valid data for Price and Stock', 'error')
    return render_template("CompoCreate.html",user=current_user,components=components)
@views.route("/addStock",methods=["GET","POST"])
@login_required
def addStock():
    components = Component.query.all()
    if request.method=="POST":
        ID = request.form.get('ID')
        NEWSTOCK = request.form.get('NEWSTOCK')
        component = Component.query.filter_by(id=ID).first()
        if component:
            component.stock = NEWSTOCK
            db.session.commit()
            return redirect(url_for('views.catalog'))
    return render_template("addStock.html",user=current_user,components=components)

@views.route("/DeleteAccountAdmin", methods=["GET", "POST"])
@login_required
def DeleteAccountAdmin():
    if request.method == "POST":
        ID = request.form.get('ID')
        user = User.query.filter_by(id=ID).first()
        
        if user:
            # Ištrinkite visus susijusius užsakymus
            orders = Order.query.filter_by(user_id=user.id).all()
            for order in orders:
                db.session.delete(order)
            
            # Dabar ištrinkite vartotoją
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('views.admin'))
    
    return render_template("DeleteAccountAdmin.html", user=current_user)


@views.route("/EditUserAdmin", methods=["GET", "POST"])
@login_required
def edit_user_admin():
    if request.method == "POST":
        ID = request.form.get('ID')
        email = request.form.get('email')
        name = request.form.get('name')
        currency = request.form.get('country-selector')
        password = request.form.get('password')

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = User.query.filter_by(id=ID).first()

        if user:
            user.email = email
            user.first_name = name
            user.password = hashed_password
            user.Country = currency
            db.session.commit()
            return redirect(url_for('views.admin'))  # Redirect to the admin page after updating

    return render_template("EditUserAdmin.html", user=current_user)



@views.route("/Statistics", methods=["GET", "POST"])
@login_required
def Statistics():
    # Highest order paid
    highest_order = db.session.query(Order).order_by(Order.amountPaid.desc()).first()
    
    # User with the most orders
    most_orders_user = db.session.query(
        User, func.count(Order.id).label('order_count')
    ).join(Order).group_by(User.id).order_by(func.count(Order.id).desc()).first()
    
    # Newest and oldest user
    newest_user = db.session.query(User).order_by(User.id.desc()).first()
    oldest_user = db.session.query(User).order_by(User.id).first()

    # Kiek prekių nupirkta kurią dieną
    orders_per_day = db.session.query(
        func.date(Order.orderDate).label('date'),
        func.sum(Order.amountPaid).label('total_sales')
    ).group_by(func.date(Order.orderDate)).all()

    # Už kiek nupirkta
    sales_per_day = db.session.query(
        func.date(Order.orderDate).label('date'),
        func.sum(Order.amountPaid).label('total_sales')
    ).group_by(func.date(Order.orderDate)).all()

    # Pelningiausi mėnesiai
    monthly_sales = db.session.query(
        func.strftime('%Y-%m', Order.orderDate).label('month'),
        func.sum(Order.amountPaid).label('total_sales')
    ).group_by(func.strftime('%Y-%m', Order.orderDate)).order_by(func.sum(Order.amountPaid).desc()).all()

    # Most wanted component
    all_orders = db.session.query(Order).all()
    component_counter = Counter()

    for order in all_orders:
        order_items = order.orderItems.split(',')  # Assuming orderItems is a comma-separated string of component IDs
        component_counter.update(order_items)

    most_wanted_component_id = component_counter.most_common(1)[0][0]
    most_wanted_component = db.session.query(Component).filter_by(id=most_wanted_component_id).first()

    return render_template(
        'Statistics.html',
        user=current_user,
        highest_order=highest_order,
        most_orders_user=most_orders_user,
        newest_user=newest_user,
        oldest_user=oldest_user,
        orders_per_day=orders_per_day,
        sales_per_day=sales_per_day,
        monthly_sales=monthly_sales,
        most_wanted_component=most_wanted_component,
        most_wanted_component_count=component_counter[most_wanted_component_id]
    )
    
    
    
    
@views.route('/remove_component', methods=['GET', 'POST'])
@login_required
def remove_component():
    if request.method == 'POST':
        component_name = request.form.get('component_name')
        if not component_name:
            return render_template('remove_component.html', error="Component name is required")

        component = Component.query.filter_by(name=component_name).first()
        if component is None:
            return render_template('remove_component.html', error="Component not found")

        try:
            db.session.delete(component)
            db.session.commit()
            return render_template('remove_component.html', message=f"{component_name} deleted successfully")
        except Exception as e:
            db.session.rollback()  # Atkuriame sesiją, jei įvyko klaida
            return render_template('remove_component.html', error=str(e))

    return render_template('remove_component.html')


@views.route("/Bdelete", methods=['GET', 'POST'])
@login_required
def Bdelete():
    return render_template("Bdelete.html",user=current_user)


@views.route("/EditUserAdmin",methods=["GET","POST"])
@login_required
def EditUserAdmin():
    if request.method=="POST":
        ID = request.form.get('ID')
        email = request.form.get('email')
        name = request.form.get('name')
        Currency = request.form.get('country-selector')

        import hashlib
        password = request.form.get('password')
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = User.query.filter_by(id=ID).first()
        if user:
            user.email = email
            user.first_name = name
            user.password = hashed_password
            user.Country = Currency
            db.session.commit()
            return redirect(url_for('views.admin'))
            
    return render_template("EditUserAdmin.html",user=current_user)


@views.route("/viewCommentsAdmin", methods=["GET", "POST"])
@login_required
def viewCommentsAdmin():
    comments = Comment.query.all()
    return render_template('viewCommentsAdmin.html',user=current_user, comments=comments)


