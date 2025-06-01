import os
from faker import Faker
from datetime import datetime
import xml.etree.ElementTree as ET
import random

fake = Faker('nl_NL')  # Nederlandse fake data

def generate_customer_xml(customerId):
    customer = ET.Element("customer")

    fields = {
        "customerId": f"CUST{customerId:07d}",  # bv. CUST0000001
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "email": fake.email(),
        "phoneNumber": fake.phone_number(),
        "birthDate": fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
        "country": "Netherlands",
        "creditCardNumber": fake.credit_card_number(card_type='mastercard'),
        "creditCardExpiry": fake.credit_card_expire(),
        "creditCardCVV": fake.credit_card_security_code(card_type='mastercard'),
        "creditCardStatus": random.choice(['active', 'pending', 'blocked']),
        "branche": random.choice(['Retail', 'Finance', 'Healthcare', 'Technology', 'Education', 'Manufacturing', 'Transportation']),
        "iban": fake.iban(),
        "createdDate": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    for key, value in fields.items():
        ET.SubElement(customer, key).text = value

    return customer

def generate_xml_file(filename="data/customers.xml", num_customers=1000):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    customers = ET.Element("customers")

    for i in range(1, num_customers + 1):
        customers.append(generate_customer_xml(i))

    tree = ET.ElementTree(customers)
    
    # Zorgt ervoor dat de XML mooi geformatteerd is
    import xml.dom.minidom
    
    raw_string = ET.tostring(customers, encoding='utf-8')
    parsed = xml.dom.minidom.parseString(raw_string)
    pretty_xml_as_string = parsed.toprettyxml(indent="  ")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(pretty_xml_as_string)
        print(f"{num_customers} fake customers written to {filename}")

    if __name__ == "__main__":
        generate_xml_file()
