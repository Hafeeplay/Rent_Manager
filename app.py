from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import hashlib
import csv
import os
import datetime
from datetime import timedelta
import json


app = Flask(__name__)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/Admin@786Rent@786')
def home():
    return render_template('index.html')

# Route for handling the login page logic
@app.route('/login1', methods=['POST', 'GET'])
def login1():
    error = None
    if request.method == 'POST':
        user=(request.form['username'])
        passer=(request.form['password'])
        if request.form['username'] != 'Admin@786' or request.form['password'] != 'Rent@786':
            error = 'Invalid Credentials. Please try again.'
        else:
            
            return redirect(f'/{user}{passer}')
    return render_template('login.html', error=error)

CSV_FILE = './templates/properties.csv'
CSV_FOLDER = 'csv_files'


def load_properties():
    properties = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            properties.append(row)
    return properties

def save_properties(properties):
    fieldnames = ['property_name', 'total_houses', 'present_month']
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(properties)

def create_property_csv(property_name):
    csv_file = f'{CSV_FOLDER}/{property_name}.csv'
    with open(csv_file, 'w', newline='') as file:
        fieldnames = ['tenant_name', 'room_no', 'in_date', 'rent', 'advance_paid', 'due_amount', 'amount_paid', 'remarks']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

@app.route('/property')
def index():
    properties = load_properties()
    return render_template('property.html', properties=properties)

@app.route('/add_property', methods=['POST'])
def add_property():
    property_name = request.form['property_name']
    total_houses = request.form['total_houses']
    present_month = datetime.datetime.now().strftime('%B')

    try:
        total_houses = int(total_houses)
    except ValueError:
        error_message = " Invalid Input.  Please enter a number."
        properties = load_properties()
        return render_template('property.html', properties=properties, error_message=error_message)


    property_data = {
        'property_name': property_name,
        'total_houses': total_houses,
        'present_month': present_month
    }

    properties = load_properties()
    properties.append(property_data)
    save_properties(properties)

    create_property_csv(property_name)

    return redirect('/property')


CSV_FOLDER = 'csv_files'

def load_tenants(property_name):
    tenants = []
    csv_file = f"{property_name}.csv"
    csv_path = f"{CSV_FOLDER}/{csv_file}"
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tenants.append(row)
    return tenants

def save_tenants(property_name, tenants):
    csv_file = f"{property_name}.csv"
    csv_path = f"{CSV_FOLDER}/{csv_file}"
    fieldnames = ['tenant_name', 'room_no', 'in_date', 'rent', 'advance_paid', 'due_amount', 'amount_paid', 'remarks']
    with open(csv_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tenants)


@app.route('/property/<property_name>/tenant_details')
def tenant_details(property_name):
    tenants = load_tenants(property_name)
    return render_template('tenant.html', property_name=property_name, tenants=tenants)

@app.route('/add_tenant/<property_name>', methods=['POST'])
def add_tenant(property_name):
    tenant_name = request.form['tenant_name']
    room_no = request.form['room_no']
    in_date = request.form['in_date']
    rent = request.form['rent']
    advance_paid = request.form['advance_paid']

    if (tenant_name and room_no and in_date and rent and advance_paid):
        # error_message = "Please fill in all the fields."
    
        tenants = load_tenants(property_name)

        tenant_data = {
            'tenant_name': tenant_name,
            'room_no': room_no,
            'in_date': in_date,
            'rent': rent,
            'advance_paid': advance_paid,
            'due_amount': rent,
            'amount_paid': '',
            'remarks': ''
        }

        tenants.append(tenant_data)
        save_tenants(property_name, tenants)

        csv_file = f"{property_name}_{tenant_name}.csv"
        csv_path = os.path.join(CSV_FOLDER, csv_file)
        with open(csv_path, 'w', newline='') as file:
            fieldnames = ['due_amount', 'amount_paid', 'datetime']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

        

        return redirect(f'/property/{property_name}/tenant_details')
        # return render_template('tenant.html', property_name=property_name, tenants=load_tenants(property_name), error_message=error_message)
    else:
        error_message = "Please fill in all the fields."
        return render_template('tenant.html', property_name=property_name, tenants=load_tenants(property_name), error_message=error_message)





def save_payment_history(property_name, tenant_name, data):
    csv_file = f"{property_name}_{tenant_name}.csv"
    csv_path = os.path.join(CSV_FOLDER, csv_file)

    with open(csv_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)




def update_due_amount(property_name, tenant_name, amount_paid):
    tenants = load_tenants(property_name)
    for tenant in tenants:
        if tenant['tenant_name'] == tenant_name:
            due_amount = int(tenant['due_amount'])
            if amount_paid <= due_amount:
                tenant['due_amount'] = str(due_amount - amount_paid)
                tenant['amount_paid'] = str(amount_paid)
                tenant['remarks'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                save_tenants(property_name, tenants)
                save_payment_history(property_name, tenant_name, [tenant['due_amount'], tenant['amount_paid'], tenant['remarks']])
                
            else:
                # Handle invalid input or error message
                pass




@app.route('/update_amount_paid/<property_name>/<index>', methods=['POST'])
def update_amount_paid(property_name, index):
    amount_paid = int(request.form.get("amount_paid"))
    tenants = load_tenants(property_name)
    tenant_name = tenants[int(index) - 1]['tenant_name']
    
   
    update_due_amount(property_name, tenant_name, amount_paid)

    return redirect(f'/property/{property_name}/tenant_details')




@app.route('/download_history/<property_name>/<tenant_name>')
def download_history(property_name, tenant_name):
    csv_file = f"{property_name}_{tenant_name}.csv"
    csv_path = os.path.join(CSV_FOLDER, csv_file)
    return send_file(csv_path, as_attachment=True)


# Update dues for all tenants
def update_dues(property_name):
    tenants = load_tenants(property_name)
    current_date = datetime.datetime.now()

    for tenant in tenants:
        in_date = datetime.datetime.strptime(tenant['in_date'], '%Y-%m-%d')
        function_last_called_date = datetime.datetime.strptime(tenant['remarks'], '%Y-%m-%d %H:%M:%S') if tenant['remarks'] else None

        if function_last_called_date:
            months_diff = (current_date.year - function_last_called_date.year) * 12 + (current_date.month - function_last_called_date.month)
        else:
            months_diff = (current_date.year - in_date.year) * 12 + (current_date.month - in_date.month)

        if months_diff > 0:
            rent = int(tenant['rent'])
            tenant['due_amount'] = str(int(tenant['due_amount']) + (months_diff * rent))
            tenant['remarks'] = current_date.strftime('%Y-%m-%d %H:%M:%S')

    save_tenants(property_name, tenants)

# Route for updating dues
@app.route('/update_dues/<property_name>', methods=['POST'])
def update_dues_route(property_name):
    update_dues(property_name)
    return redirect(f'/property/{property_name}/tenant_details')

if __name__ == '__main__':
    app.run(debug=True)
