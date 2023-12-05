from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('research.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/customers/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        first_name = request.form['customer_first_name']
        last_name = request.form['customer_last_name']
        gender = request.form['customer_gender']
        dob = request.form['customer_dob']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customer (customer_last_name, customer_first_name, customer_gender, customer_dob)
            VALUES (?, ?, ?, ?)
        ''', (last_name, first_name, gender, dob))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    else:
        return render_template('add_customer.html')

@app.route('/customers')
def customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customer').fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)


@app.route('/products')
def products():
    return render_template('products.html')
@app.route('/get_product', methods=['GET', 'POST'])
def get_product():
    if request.method == 'POST':
        product_code = request.form['product_code']
        return redirect(url_for('product_info', product_code=product_code))
    return render_template('get_product.html')

@app.route('/product_info/<product_code>')
def product_info(product_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM product WHERE product_code = ?", (product_code,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        message = 'Product with code {} does not exist.'.format(product_code)
        return render_template('get_product.html', message=message)
    else:
        product_info = {key: product[key] for key in product.keys()}
        return render_template('product_info.html', product=product_info)
    
@app.route('/sort_customers', methods=['GET'])
def sort_customers():
    # Get the selected sorting option from the form
    sort_by = request.args.get('sort_by')

    # Define a dictionary to map sorting options to corresponding SQL columns
    sort_mapping = {
        'customer_id': 'customer_id',
        'customer_last_name': 'customer_last_name',
        'customer_first_name': 'customer_first_name',
        'customer_gender': 'customer_gender',
        'customer_dob': 'customer_dob'
    }

    # Check if the selected sorting option is valid
    if sort_by in sort_mapping:
        # Connect to the database
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Retrieve customers from the database, sorted by the selected option
        cursor.execute(f'SELECT * FROM customer ORDER BY {sort_mapping[sort_by]}')
        sorted_customers = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Render the customers.html template with the sorted customers
        return render_template('customers.html', customers=sorted_customers)
    else:
        # If an invalid sorting option is selected, redirect to the customer list without sorting
        return redirect(url_for('customers'))

if __name__ == '__main__':
    app.run(debug=True)