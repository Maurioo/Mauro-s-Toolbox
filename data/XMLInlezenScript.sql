USE [CRM_Demo];
GO

-- Stap 1: Lees XML-bestand in
DECLARE @xml XML;

SELECT @xml = BulkColumn
FROM OPENROWSET(BULK 'C:\Users\mauro\Downloads\simulated-crm-pipeline\data\customers.xml', SINGLE_BLOB) AS xmlData;

-- Stap 2: Insert alle <customer> items in dbo.Customers
INSERT INTO dbo.Customers (
    CustomerID,
    FirstName,
    LastName,
    Email,
    PhoneNumber,
    BirthDate,
    Country,
    CreditCardNumber,
    CreditCardExpiry,
    CreditCardCVV,
    CreditCardStatus,
    Branche,
    IBAN,
    CreatedDate
)
SELECT
    x.customer.value('(customerId)[1]', 'VARCHAR(20)'),
    x.customer.value('(firstName)[1]', 'NVARCHAR(50)'),
    x.customer.value('(lastName)[1]', 'NVARCHAR(50)'),
    x.customer.value('(email)[1]', 'NVARCHAR(100)'),
    x.customer.value('(phoneNumber)[1]', 'NVARCHAR(30)'),
    x.customer.value('(birthDate)[1]', 'DATE'),
    x.customer.value('(country)[1]', 'NVARCHAR(50)'),
    x.customer.value('(creditCardNumber)[1]', 'VARCHAR(25)'),
    x.customer.value('(creditCardExpiry)[1]', 'VARCHAR(10)'),
    x.customer.value('(creditCardCVV)[1]', 'VARCHAR(10)'),
    x.customer.value('(creditCardStatus)[1]', 'VARCHAR(20)'),
    x.customer.value('(branche)[1]', 'VARCHAR(50)'),
    x.customer.value('(iban)[1]', 'VARCHAR(34)'),
    x.customer.value('(createdDate)[1]', 'DATETIME')
FROM 
    @xml.nodes('/customers/customer') AS x(customer);
