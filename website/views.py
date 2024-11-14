from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from website.models import *
from . import db
import json
from .models import User, Component
from collections import Counter

views = Blueprint('views', __name__)



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






@views.route("/admin",methods=['GET','POST'])
@login_required
def admin():
    currencyMultiplier = 0
    currencySymbol="None"
    if current_user.Country == "LT":
        currencyMultiplier = 3.71
        currencySymbol = "€"
    if current_user.Country == "USA":
        currencyMultiplier = 1
        currencySymbol = "$"
 

    users = User.query.all()
    components = Component.query.all()
    return render_template('admin.html', user=current_user, users=users, components=components,currencySymbol=currencySymbol,currencyMultiplier=currencyMultiplier)


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

from flask_login import logout_user

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
    cpu1 = Component(name='Intel Core i9-9900K', description='8-Core, 16-Thread, 3.6 GHz (5.0 GHz Turbo) LGA 1151 Processor', image_url='IntelCorei9-9900K.jpg', price=499.99, stock=5)
    cpu2 = Component(name='AMD Ryzen 7 5800X', description='8-Core, 16-Thread, 3.8 GHz (4.7 GHz Boost) AM4 Processor', image_url='AMDRyzen75800X.jpg', price=449.99, stock=8)
    cpu3 = Component(name='Intel Core i5-10600K', description='6-Core, 12-Thread, 4.1 GHz (4.8 GHz Turbo) LGA 1200 Processor', image_url='IntelCorei5-10600K.jpg', price=279.99, stock=10)
    

    # Commit the changes to the database
    db.session.add_all([cpu1,cpu2,cpu3])
    db.session.commit()

    # Add GPUs
    gpu1 = Component(name='NVIDIA GeForce RTX 3080', description='10 GB GDDR6X, 8704 CUDA Cores, PCIe 4.0, Ray Tracing', image_url='NVIDIAGeForceRTX3080.jpg', price=799.99, stock=3)
    gpu2 = Component(name='AMD Radeon RX 6800 XT', description='16 GB GDDR6, 72 Ray Accelerators, PCIe 4.0, Infinity Cache', image_url='AMDRadeonRX6800XT.jpg', price=649.99, stock=6)
    gpu3 = Component(name='NVIDIA GeForce GTX 1660 Super', description='6 GB GDDR5, 1408 CUDA Cores, PCIe 3.0', image_url='NVIDIAGeForceGTX1660Super.jpg', price=249.99, stock=12)

    # Commit the changes to the database
    db.session.add_all([gpu1, gpu2, gpu3])
    db.session.commit()



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
        currencyMultiplier = 3.71
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


@views.route("/order/<CompoID>",methods=['GET','POST'])
@login_required
def order(CompoID):
    currencyMultiplier = 0
    currencySymbol="None"
    if current_user.Country == "LT":
        currencyMultiplier = 3.71
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

@views.route("/userOrders",methods=["GET","POST"])
@login_required
def userOrders():

    currencyMultiplier = 0
    currencySymbol="None"
    if current_user.Country == "LT":
        currencyMultiplier = 3.71
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

@views.route("/cartPage",methods=["GET","POST"])
@login_required
def cartPage():
     

    userID = request.args.get('userID')
    user = User.query.get(userID)
    items = user.cartItems
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
    sum=0
    for CompoID in ComponentsID:
        component = Component.query.filter_by(id=CompoID).first()
        if component:
            price = getPrice(component)
            sum+=price
    
    #Get the Components in a dictionary to save the Amount and the Components ID's
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
        if component:
            component_unique_list.append(componentIterative)
    
    component_NotUnique_list=[]
    sum1=0
    for ids in ComponentsID:
    # Retrieve the component with the given ID and append it to the list
        componentIterative = Component.query.filter_by(id=ids).first()
        if component:
            if component.isOnSale:
                sum1+=getPrice(componentIterative) * component.priceModifier
            if component.isOnSale==False:
                sum1+=getPrice(componentIterative)

    currencyMultiplier = 0
    currencySymbol="None"
    if current_user.Country == "LT":
        currencyMultiplier = 3.71
        sum1=sum1*currencyMultiplier
        currencySymbol = "€"
    if current_user.Country == "USA":
        currencyMultiplier = 1
        sum1=sum1*currencyMultiplier
        currencySymbol = "$"
 
    
    return render_template('cartPage.html',user=current_user,ComponentsID=ComponentsID,
                           ID_counter=ID_counter,components_list=component_unique_list,sum1=sum1,currencyMultiplier=currencyMultiplier,currencySymbol=currencySymbol)




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
        currencyMultiplier = 3.71
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


@views.route("/addComment",methods=["GET","POST"])
@login_required
def addComment():
    
    if request.method == 'POST':
        comment_type = request.form.get('comment_type')
        comment_data = request.form.get('comment_data')

        if not comment_type or not comment_data:
            flash('All fields are required!', 'danger')
        else:
            new_comment = Comment(comment_type=comment_type,comment_data=comment_data,user_id=current_user.id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Your comment has been added!', 'success')
            return redirect(url_for('views.home'))

    return render_template('addComment.html',user=current_user)




@views.route("/ViewComments/<selected_type>", methods=["GET", "POST"])
@login_required
def ViewComments(selected_type):
    comments = Comment.query.filter_by(comment_type=selected_type).all()
    return render_template('ViewComments.html',user=current_user, selected_type=selected_type, comments=comments)

@views.route("/viewCommentsAdmin", methods=["GET", "POST"])
@login_required
def viewCommentsAdmin():
    comments = Comment.query.all()
    return render_template('viewCommentsAdmin.html',user=current_user, comments=comments)

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





