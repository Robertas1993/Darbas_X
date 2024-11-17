# from flask import Blueprint, render_template
# from flask_login import login_required, current_user
# from .models import User, Component  # Importuojame tik tai, ko reikia
# from .auth import *  # Jei reikia, galite importuoti konkrečius dalykus
# from .views import *  # Jei reikia, galite importuoti konkrečius dalykus
# from collections import Counter
# from sqlalchemy import func
# admin_bp = Blueprint('admin', __name__)








# @views.route("/admin", methods=['GET', 'POST'])
# @login_required
# def admin():
#     currencyMultiplier = 0
#     currencySymbol = "None"
    
#     if current_user.Country == "LT":
#         currencyMultiplier = 1.10
#         currencySymbol = "€"
#     elif current_user.Country == "USA":
#         currencyMultiplier = 1
#         currencySymbol = "$"

#     users = User.query.all()
#     components = Component.query.all()
#     return render_template('admin.html', user=current_user, users=users, components=components, currencySymbol=currencySymbol, currencyMultiplier=currencyMultiplier)

# def CompoUpdate():
#     components = Component.query.all()

#     if request.method=="POST":
#         ID = request.form.get('ID')
#         NewName = request.form.get('NewName')
#         Description = request.form.get('Description')
#         imageName = request.form.get('imageName')
#         Price = request.form.get('Price')
#         Stock = request.form.get('Stock')

#         component = Component.query.filter_by(id = ID).first()
#         if component:
#             component.NewName = NewName
#             component.Description = Description
#             component.imageName = imageName
#             component.Price = Price
#             component.Stock = Stock

#             db.session.commit()
#         flash("The Component has been successfully updated",category="success")

#     return render_template('CompoUpdate.html',user=current_user, components=components)

# @views.route("/CompoDelete",methods=["GET","POST"])
# @login_required
# def CompoDelete():
#     components = Component.query.all()
#     if request.method=="POST":
#         ID = request.form.get('ID')
#         component = Component.query.filter_by(id=ID).first()
#         if component:
#             db.session.delete(component)
#             db.session.commit()
#         return redirect(url_for('views.admin'))
#     return render_template("CompoDelete.html",user=current_user,components=components)

# @views.route("/CompoCreate",methods=["GET","POST"])
# @login_required
# def CompoCreate():
    

#     components = Component.query.all()
#     if request.method=="POST":
#         NewName = request.form.get('NewName')
#         Description = request.form.get('Description')
#         imageName = request.form.get('imageName')
#         Price = request.form.get('Price')
#         Stock = request.form.get('Stock')

#         if not NewName or not Description or not imageName or not Price or not Stock:
#             flash('Please fill out all fields', 'error')
#         else:
#             try:
#                 newComponent = Component(
#                     name=NewName, 
#                     description=Description, 
#                     image_url=imageName, 
#                     price=float(Price), 
#                     stock=int(Stock), 
#                     isOnSale=False, 
#                     priceModifier=1
#                 )

#                 db.session.add(newComponent)
#                 db.session.commit()
#                 return redirect(url_for('views.admin'))
#             except ValueError:
#                 flash('Please enter valid data for Price and Stock', 'error')
#     return render_template("CompoCreate.html",user=current_user,components=components)
# @views.route("/addStock",methods=["GET","POST"])
# @login_required
# def addStock():
#     components = Component.query.all()
#     if request.method=="POST":
#         ID = request.form.get('ID')
#         NEWSTOCK = request.form.get('NEWSTOCK')
#         component = Component.query.filter_by(id=ID).first()
#         if component:
#             component.stock = NEWSTOCK
#             db.session.commit()
#             return redirect(url_for('admin_bp.catalog'))
#     return render_template("addStock.html",user=current_user,components=components)

# @views.route("/DeleteAccountAdmin", methods=["GET", "POST"])
# @login_required
# def DeleteAccountAdmin():
#     if request.method == "POST":
#         ID = request.form.get('ID')
#         user = User.query.filter_by(id=ID).first()
        
#         if user:
#             # Ištrinkite visus susijusius užsakymus
#             orders = Order.query.filter_by(user_id=user.id).all()
#             for order in orders:
#                 db.session.delete(order)
            
#             # Dabar ištrinkite vartotoją
#             db.session.delete(user)
#             db.session.commit()
#             return redirect(url_for('views.admin'))
    
#     return render_template("DeleteAccountAdmin.html", user=current_user)

# @views.route("/EditUserAdmin",methods=["GET","POST"])
# @login_required
# def EditUserAdmin():
#     if request.method=="POST":
#         ID = request.form.get('ID')
#         email = request.form.get('email')
#         name = request.form.get('name')
#         Currency = request.form.get('country-selector')

#         import hashlib
#         password = request.form.get('password')
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()

#         user = User.query.filter_by(id=ID).first()
#         if user:
#             user.email = email
#             user.first_name = name
#             user.password = hashed_password
#             user.Country = Currency
#             db.session.commit()
#             return redirect(url_for('views.admin'))
            
#     return render_template("EditUserAdmin.html",user=current_user)




# @views.route("/Statistics", methods=["GET", "POST"])
# @login_required
# def Statistics():
#     # Highest order paid
#     highest_order = db.session.query(Order).order_by(Order.amountPaid.desc()).first()
    
#     # User with the most orders
#     most_orders_user = db.session.query(
#         User, func.count(Order.id).label('order_count')
#     ).join(Order).group_by(User.id).order_by(func.count(Order.id).desc()).first()
    
#     # Newest and oldest user
#     newest_user = db.session.query(User).order_by(User.id.desc()).first()
#     oldest_user = db.session.query(User).order_by(User.id).first()

#     # Kiek prekių nupirkta kurią dieną
#     orders_per_day = db.session.query(
#         func.date(Order.orderDate).label('date'),
#         func.sum(Order.amountPaid).label('total_sales')
#     ).group_by(func.date(Order.orderDate)).all()

#     # Už kiek nupirkta
#     sales_per_day = db.session.query(
#         func.date(Order.orderDate).label('date'),
#         func.sum(Order.amountPaid).label('total_sales')
#     ).group_by(func.date(Order.orderDate)).all()

#     # Pelningiausi mėnesiai
#     monthly_sales = db.session.query(
#         func.strftime('%Y-%m', Order.orderDate).label('month'),
#         func.sum(Order.amountPaid).label('total_sales')
#     ).group_by(func.strftime('%Y-%m', Order.orderDate)).order_by(func.sum(Order.amountPaid).desc()).all()

#     # Most wanted component
#     all_orders = db.session.query(Order).all()
#     component_counter = Counter()

#     for order in all_orders:
#         order_items = order.orderItems.split(',')  # Assuming orderItems is a comma-separated string of component IDs
#         component_counter.update(order_items)

#     most_wanted_component_id = component_counter.most_common(1)[0][0]
#     most_wanted_component = db.session.query(Component).filter_by(id=most_wanted_component_id).first()

#     return render_template(
#         'Statistics.html',
#         user=current_user,
#         highest_order=highest_order,
#         most_orders_user=most_orders_user,
#         newest_user=newest_user,
#         oldest_user=oldest_user,
#         orders_per_day=orders_per_day,
#         sales_per_day=sales_per_day,
#         monthly_sales=monthly_sales,
#         most_wanted_component=most_wanted_component,
#         most_wanted_component_count=component_counter[most_wanted_component_id]
#     )
    
    
    
    
# @views.route('/remove_component', methods=['GET', 'POST'])
# @login_required
# def remove_component():
#     if request.method == 'POST':
#         component_name = request.form.get('component_name')
#         if not component_name:
#             return render_template('remove_component.html', error="Component name is required")

#         component = Component.query.filter_by(name=component_name).first()
#         if component is None:
#             return render_template('remove_component.html', error="Component not found")

#         try:
#             db.session.delete(component)
#             db.session.commit()
#             return render_template('remove_component.html', message=f"{component_name} deleted successfully")
#         except Exception as e:
#             db.session.rollback()  # Atkuriame sesiją, jei įvyko klaida
#             return render_template('remove_component.html', error=str(e))

#     return render_template('remove_component.html')


# @views.route("/Bdelete", methods=['GET', 'POST'])
# @login_required
# def Bdelete():
#     return render_template("Bdelete.html",user=current_user)


# @views.route("/EditUserAdmin",methods=["GET","POST"])
# @login_required
# def EditUserAdmin():
#     if request.method=="POST":
#         ID = request.form.get('ID')
#         email = request.form.get('email')
#         name = request.form.get('name')
#         Currency = request.form.get('country-selector')

#         import hashlib
#         password = request.form.get('password')
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()

#         user = User.query.filter_by(id=ID).first()
#         if user:
#             user.email = email
#             user.first_name = name
#             user.password = hashed_password
#             user.Country = Currency
#             db.session.commit()
#             return redirect(url_for('views.admin'))
            
#     return render_template("EditUserAdmin.html",user=current_user)


# @views.route("/viewCommentsAdmin", methods=["GET", "POST"])
# @login_required
# def viewCommentsAdmin():
#     comments = Comment.query.all()
#     return render_template('viewCommentsAdmin.html',user=current_user, comments=comments)





