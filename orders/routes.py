import json
from datetime import date

import pdfkit
from flask import render_template, flash, request, jsonify, redirect, url_for, make_response
from flask_login import login_user, current_user, logout_user, login_required
from passlib.hash import sha256_crypt
from sqlalchemy import func

from orders import app, db
from orders.forms import RegisterForm
from orders.models import Orders, Orders_items, Products, Users, Suppliers

from sqlalchemy import or_, and_

from flask import session

# store the form values in session
@app.route('/store_data')
def store_data(value):
    # data = [{'name': 'John', 'age': 30}, {'name': 'Jane', 'age': 25}]
    session['data'] = json.dumps(value)
    return 'Data stored in session'

@app.route('/retrieve_data')
def retrieve_data():
    data = json.loads(session.get('data', '[]'))
    filters = json.loads(session.get('filters', '[]'))
    return jsonify(data=data, filters=filters)



# ########################################################## Start Filter functions
@app.route('/add_filter', methods=['POST'])
def add_filter():
    filters = json.loads(session.get('filters', '[]'))
    filter_dict = {
        'column': request.form['filter-column'],
        'condition': request.form['filter-condition'],
        'value': request.form['filter-value']
    }
    filters.append(filter_dict)
    session['filters'] = json.dumps(filters)
    return render_template(url_for('products'), filters=filters)

@app.route('/clear_filters')
def clear_filters():
    session.pop('filters', None)
    return render_template(url_for('products'))



# ########################################################## End Filter functions


def create_filter_query(filter_structure, model):
    query = None

    for f in filter_structure:
        column = getattr(model, f['column'])
        condition = f['condition']
        value = f['value']

        if condition == 'equals':
            q = column == value
        elif condition == 'not_equals':
            q = column != value
        elif condition == 'contains':
            q = column.ilike(f'%{value}%')
        elif condition == 'not_contains':
            q = ~column.ilike(f'%{value}%')
        elif condition == 'starts_with':
            q = column.ilike(f'{value}%')
        elif condition == 'ends_with':
            q = column.ilike(f'%{value}')
        else:
            raise ValueError(f"Invalid condition '{condition}'")

        if query is None:
            query = q
        else:
            query = and_(query, q)

    return query

def getlist():
    user = Users.query.filter_by(email=current_user.email).first()
    my_list = user.Roles.split(",")
    return my_list


@app.route('/dashboard')
@login_required
def dashboard():
    order = db.session.query(Orders).filter(func.date(Orders.date_creation) == date.today()).all()
    count = 0
    for i in order:
        count += int(i.total_amount)
    num_orders = db.session.query(Orders).filter(func.date(Orders.date_creation) == date.today()).count()

    context = {
        'daily': count,
        'orders': num_orders
    }

    return render_template('index.html', context=context)


@app.route('/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        user = Users.query.filter_by(email=email).first()
        if user:

            passwordd = Users.query.filter_by(email=email).first()
            if sha256_crypt.verify(password_candidate, sha256_crypt.hash(passwordd.password)):
                login_user(user)
                # flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))

            else:
                error = "Invalid Password"
                return render_template('login.html', error=error)
        else:
            error = "Invalid email"
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        addd = Users(username=username, email=email, password=password)
        db.session.add(addd)
        db.session.commit()
        flash('You are now registered', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/roles')
@login_required
def roles():
    users = Users.query.all()
    return render_template('roles.html', users=users)


@app.route('/order')
@login_required
def order():
    used_suppliers_query = Suppliers.query.filter(Suppliers.products.any()).all()

    selected_supplier_id = request.args.get('selected_supplier_id')
    if selected_supplier_id:
        selected_supplier_id = int(selected_supplier_id)
        filter_query = Products.supplier_id == selected_supplier_id
    else:
        filter_query = None


    if filter_query is None:
        products = Products.query.all()
    else:
        products = db.session.query(Products).filter(filter_query).all()
        # return render_template('product_table.html', products=products_query)


    return render_template('makeorder.html',
                           products=products,
                           filter_dropdown_cols=used_suppliers_query,
                           selected_supplier_id=selected_supplier_id)


@app.route('/insert', methods=['POST'])
@login_required
def insert():
    barcode = request.form.getlist('item_bar[]')
    qua = request.form.getlist('item_quantity[]')
    name = request.form.getlist('product_name[]')
    total = request.form.getlist('total[]')
    price = request.form.getlist('price[]')
    total_amount = request.form.get('total_amount')

    # for n, q in zip(barcode, qua):
    #     product = Products.query.filter_by(barcode=n).first()
    #     if product.quantity > 0:
    #         product.quantity = product.quantity - int(q)
    #     else:
    #         print("you do not have this much of quantity", n)
    db.session.commit()

    add = Orders(total_amount=total_amount, user_order=current_user)
    db.session.add(add)
    db.session.commit()
    for q, p, t, n, b in zip(qua, price, total, name, barcode):
        ord = Orders_items(barcode=b, quantity=q, name=n, price=p, total=t, Orders_items=add)
        db.session.add(ord)
    db.session.commit()

    return jsonify({'data': 'ok', 'order_id': add.id})


@app.route('/data', methods=['POST'])
@login_required
def getdata():
    input_item = request.json
    pro = Products.query.filter_by(barcode=input_item).first()
    return jsonify({'price': pro.price, 'name': pro.name, 'quantity': pro.quantity})


@app.route('/products',methods=['GET','POST'])
@login_required
def products():
    products_columns = [str(column.name) for column in Products.__table__.columns]
    filter_by_supplier_name = request.args.get('selected_supplier_name')

    filter_query = None
    selected_supplier_query = None
    # filter table by custom filters container
    if request.args.get('filter_query') or request.args.get('filters'):
        # filters = json.loads(request.args.get('filters'))
        filters = [{'column': 'name', 'condition': 'contains', 'value': 'ol'}]
        filter_query = create_filter_query(filter_structure=filters, model=Products)
        selected_supplier_id = request.args.get('selected_supplier_id')
        if selected_supplier_id:
            selected_supplier_id = int(selected_supplier_id)
            filter_query = and_(filter_query, Products.supplier_id == selected_supplier_id)
    else:
        selected_supplier_id = request.args.get('selected_supplier_id')
        if selected_supplier_id:
            selected_supplier_id = int(selected_supplier_id)
            filter_query = Products.supplier_id == selected_supplier_id
        else:
            filter_query = None


    if filter_query is None:
        products_query = Products.query.all()
    else:
        products_query = db.session.query(Products).filter(filter_query).all()
        # return render_template('product_table.html', products=products_query)

    print(products_query)

    # filter table by chosen supplier
    # if filter_by_supplier_name and request.args.get('selected_supplier_id'):
    #     filter_by_supplier_id = request.args.get('selected_supplier_id')
    #     products_query = Products.query.filter_by(supplier_id=filter_by_supplier_id).all()
    # else:
    #     products_query = Products.query.all()


    all_suppliers_query = Suppliers.query.with_entities(Suppliers.name, Suppliers.id).all()  # Query suppliers' names
    used_suppliers_query = Suppliers.query.filter(Suppliers.products.any()).all()



    if request.method == 'POST':
        name = request.form.get('name')
        barcode = request.form.get('barcode')
        quantity = request.form.get('quantity') or 0
        price = request.form.get('price')
        supplier_id = request.form.get('supplier_id')
        supplier_name = request.form.get('supplier_name')
        add = Products(name=name, barcode=barcode, quantity=quantity, price=price, supplier_id=supplier_id)
        db.session.add(add)
        db.session.commit()
        return redirect(url_for('products'))

    return render_template('product.html',
                           products=products_query,
                           suppliers=all_suppliers_query,
                           filter_dropdown_cols=used_suppliers_query,
                           filter_dropdown_properties=products_columns,
                           selected_supplier_id=selected_supplier_id)


@app.route("/product/delete/<int:product_id>", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Products.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))


@app.route("/product/update/<int:product_id>", methods=['POST', 'GET'])
@login_required
def update_product(product_id):
    product = Products.query.get(product_id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.barcode = request.form.get('barcode')
        product.quantity = request.form.get('quantity')
        product.price = request.form.get('price')
        db.session.commit()
        return redirect(url_for('products'))

    return render_template('update_product.html', product=product)


@app.route("/manageorder")
@login_required
def manageorder():
    orders = Orders.query.all()
    return render_template('manageorder.html', orders=orders)


def deleteorder(order_id):
    order = Orders.query.get(order_id)
    for i in order.orders:
        product = Products.query.filter_by(barcode=i.barcode).first()
        product.quantity = product.quantity + int(i.quantity)
    db.session.commit()
    db.session.delete(order)
    db.session.commit()


@app.route("/order/delete/<int:order_id>", methods=['POST'])
@login_required
def delete_order(order_id):
    deleteorder(order_id)
    return redirect(url_for('manageorder'))


@app.route("/order/update/<int:order_id>", methods=['POST', 'GET'])
@login_required
def update_order(order_id):
    order = Orders.query.get(order_id)
    if request.method == 'POST':
        barcode = request.form.getlist('item_bar[]')
        qua = request.form.getlist('item_quantity[]')
        name = request.form.getlist('item_name[]')
        total = request.form.getlist('total[]')
        price = request.form.getlist('price[]')
        total_amount = request.form.get('total_amount')
        deleteorder(order_id)
        for n, q in zip(barcode, qua):
            product = Products.query.filter_by(barcode=n).first()
            if product.quantity > 0:
                product.quantity = product.quantity - int(q)
            else:
                print("you do not have this much of quantity", n)
        db.session.commit()

        add = Orders(total_amount=total_amount, user_order=current_user)
        db.session.add(add)
        db.session.commit()
        for q, p, t, n, b in zip(qua, price, total, name, barcode):
            ord = Orders_items(barcode=b, quantity=q, name=n, price=p, total=t, Orders_items=add)
            db.session.add(ord)
        db.session.commit()

        return redirect(url_for('manageorder'))

    return render_template('update_order.html', order=order.orders, order_amount=order)


@app.route("/order/printInvoice/<int:order_id>", methods=['GET'])
@login_required
def print_invoice(order_id):
    printInvoice(order_id)
    return redirect(url_for('manageorder'))

@app.route("/printInvoice/<int:order_id>")
@login_required
def printInvoice(order_id):
    order = Orders.query.get(order_id)
    renderd = render_template('print.html', order=order)
    css = ['orders/static/css/sb-admin-2.min.css']
    wkhtml_path = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")  # by using configuration you can add path value.

    pdf = pdfkit.from_string(renderd, False, css=css, configuration = wkhtml_path)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename = {order_id}.pdf'
    return response


# SECTION: SETTINGS > MANAGE SUPPLIERS
@app.route('/suppliers', methods=['GET', 'POST'])
@login_required
def suppliers():
    suppliers = Suppliers.query.all()
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        contact = request.form.get('phone')
        note = request.form.get('note')
        try:
            add = Suppliers(name=name, address=address, contact=contact, note=note)
            db.session.add(add)
            db.session.commit()
            return jsonify({'success': True})

        except Exception as e:
            print(e)
            error = "Invalid input. Please check your input fields."
            return jsonify({'success': False, 'error': error})

    return render_template('supplier.html', suppliers=suppliers, error=error)


@app.route("/supplier/update/<int:supplier_id>", methods=['POST', 'GET'])
@login_required
def update_supplier(supplier_id):
    supplier = Suppliers.query.get(supplier_id)
    if request.method == 'POST':
        supplier.name = request.form.get('name')
        supplier.address = request.form.get('address')
        supplier.contact = request.form.get('phone')
        supplier.note = request.form.get('note')
        return redirect(url_for('suppliers'))

    return render_template('update_supplier.html', supplier=supplier)


@app.route("/supplier/delete/<int:supplier_id>", methods=['POST'])
@login_required
def delete_supplier(supplier_id):
    supplier = Suppliers.query.get(supplier_id)
    db.session.delete(supplier)
    db.session.commit()
    return redirect(url_for('suppliers'))




@app.route('/get_products')
def get_products():
    products = Products.query.all()
    products_list = [{'id': product.id,
                      'name': product.name,
                      'price': product.price,
                      'barcode': product.barcode,
                      'supplier': product.supplier.name} for product in products]
    return jsonify(products_list)