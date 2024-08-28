import streamlit as st
from PIL import Image
import pdfkit
import tempfile
import os
import base64
from num2words import num2words
from datetime import datetime


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
# These function is used to convert the Total amount which is numbers into words
def amount_to_words(amount):
    return num2words(amount, lang='en_IN', to='currency').replace('euro', 'Rupee').replace('cents', 'Paise').replace(',', '')

# Load and encode logo image
base64_string = image_to_base64("logo.png")

# Configure path to wkhtmltopdf executable
path_to_wkhtmltopdf = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

# Set up the page layout with user input for company details
col1, col2 = st.columns([3, 1])
with col1:
    company_name = st.text_input("Company Name", "Company Name")
    company_address1 = st.text_input("Company Address Line 1", "123 Main St")
    company_address2 = st.text_input("Company Address Line 2", "Suite 100")
    company_phone = st.text_input("Phone", "+1-234-567-890")
    
with col2:
    st.image(Image.open("logo.png"), width=120)
    quotation_number = st.text_input("Quotation Number", "AA240001-0")
    date = st.date_input("Date", datetime.today())

st.title("Invoice Generator")

# Initialize a list to store rows data
if "rows" not in st.session_state:
    st.session_state["rows"] = []

# User inputs for each row
rows_to_delete = []
for i in range(len(st.session_state["rows"])):
    with st.container():
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 3, 5, 3, 4, 3, 5])
        c1.write(i + 1)  # Sl No
        st.session_state["rows"][i]["HSN"] = c2.text_input(
            f"HSN {i+1}", st.session_state["rows"][i].get("HSN", "")
        )
        st.session_state["rows"][i]["Description"] = c3.text_input(
            f"Description {i+1}", st.session_state["rows"][i]["Description"]
        )
        st.session_state["rows"][i]["Quantity"] = c4.number_input(
            f"Quantity {i+1}", min_value=0, value=st.session_state["rows"][i]["Quantity"]
        )
        st.session_state["rows"][i]["Per Unit Cost"] = c5.number_input(
            f"Per Unit Cost {i+1}", min_value=0.0, format="%.2f", value=st.session_state["rows"][i]["Per Unit Cost"]
        )
        total_cost = (
            st.session_state["rows"][i]["Quantity"] * st.session_state["rows"][i]["Per Unit Cost"]
        )
        c6.write(f"Total : {total_cost:.2f}")
        st.session_state["rows"][i]["Total Cost"] = total_cost

        if c7.button(f"Delete Row {i+1}"):
            rows_to_delete.append(i)

if rows_to_delete:
    for i in sorted(rows_to_delete, reverse=True):
        st.session_state["rows"].pop(i)

if st.button("Add Row"):
    st.session_state["rows"].append(
        {
            "HSN": "",
            "Description": "",
            "Quantity": 0,
            "Per Unit Cost": 0.0,
            "Total Cost": 0.0,
        }
    )

# Calculate Subtotal, CGST, SGST, and Total Amount
subtotal = sum(row["Total Cost"] for row in st.session_state["rows"])
cgst = subtotal * 0.09
sgst = subtotal * 0.09
total_amount = subtotal + cgst + sgst

total_amount_words = amount_to_words(total_amount).capitalize()

st.write(f"**Subtotal:** {subtotal:.2f}")
st.write(f"**CGST (9%):** {cgst:.2f}")
st.write(f"**SGST (9%):** {sgst:.2f}")
st.write(f"**Total Amount:** {total_amount:.2f}")

terms_conditions = """
 <strong>Payment terms:</strong> 50% advance along with technically & commercially clear PO.<br>
 <strong>Order Terms:</strong>Once Order is placed it cannot be canceled<br>
 <strong>Delivery time:</strong> 15 days from the date of order placed<br>
 <strong>GST:</strong> Included. <br>
 <strong>Transportation:</strong> Excluded
"""

bank_details = """
Name: <strong>ACC_NAME</strong><br>
Account Number: <strong>ACC_NO</strong><br>
IFSC Code:<strong> IFSC</strong><br>
Branch:<strong> Branch Name</strong>
"""

# HTML content for the invoice
html_content = f"""
<html>
<head>
    <style>
        @page {{
            size: A4;
            margin: 20mm;
        }}
        body {{
            margin-bottom: 50mm; /* Space for footer and signature */
        }}
        .header {{
            position: relative;
            width: 100%;
            margin-bottom: 20px;
        }}
        .logo-date-container {{
            position: absolute;
            top: 0;
            right: 0;
            display: flex;
            align-items: flex-start; /* Aligns items at the start to remove any space */
        }}
        .logo {{
            width: auto; /* Use original aspect ratio */
            max-width: 120px; /* Scale the logo without distorting */
            height: auto;
        }}
        .date-quotation {{
            text-align: right;
            margin-left: 10px; /* Slight spacing between logo and date */
        }}
        .company-details {{
            text-align: left;
            margin-right: 140px; /* Adjusted to ensure space for logo */
        }}
        .invoice-header {{
            text-align: center;
            font-size: 36px; /* Larger font size */
            font-weight: bold;
            margin: 40px 0; /* Spacing around header */
        }}
        .footer {{
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 10px 0;
            color: #333;
            background-color: #f1f1f1;
        }}
        .footer p {{
            margin: 0;
            font-size: 14px;
        }}
        .signature {{
            text-align: right;
            margin-right: 40px;
            margin-top: 30px;
        }}
        .default-signature {{
            font-weight: bold;
        }}
        .details-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .details-table td {{
            border: 1px solid #000;
            padding: 8px;
            vertical-align: top; /* Align text at the top */
        }}
        .details-table th {{
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
        }}
        .terms-conditions p, .bank-details p {{
            margin-bottom: 5px; /* Increase space between paragraphs */
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: center; /* Center align table cells */
        }}
        th, td {{
            border: 1px solid #000;
            padding: 8px;
        }}
        .details-table td {{
            text-align: left; /* Left align for better readability */
        }}
        @media print {{
            .footer {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
            }}
            .signature {{
                position: fixed;
                bottom: 30mm; /* Position above the footer */
                right: 20mm;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="invoice-header">COMPANY NAME</div>  <!-- Change  the company name -->
        <div class="company-details">
            <h1>To,</h1>
            <p>{company_name}<br>{company_address1}<br>{company_address2}<br>Phone: {company_phone}</p>
        </div>
        <div class="logo-date-container">
            <img class="logo" src="data:image/png;base64,{base64_string}" alt="Company Logo" />
            <div class="date-quotation">
                <p>Date: {date.strftime('%d-%m-%Y')}</p>
                <p>Quotation Number: {quotation_number}</p>
            </div>
        </div>
    </div>
    <h2>Machine Quotation</h2>
    <table>
        <tr>
            <th>Sl No</th>
            <th>HSN</th>
            <th>Description</th>
            <th>Quantity</th>
            <th>Per Unit Cost</th>
            <th>Total Cost</th>
        </tr>
"""

for i, row in enumerate(st.session_state["rows"]):
    html_content += f"""
    <tr>
        <td>{i + 1}</td>
        <td>{row["HSN"]}</td>
        <td>{row["Description"]}</td>
        <td>{row["Quantity"]}</td>
        <td>{row["Per Unit Cost"]:.2f}</td>
        <td>{row["Total Cost"]:.2f}</td>
    </tr>
    """

html_content += f"""
    <tr>
        <td colspan="5" style="text-align: right;">Subtotal</td>
        <td>{subtotal:.2f}</td>
    </tr>
    <tr>
        <td colspan="5" style="text-align: right;">CGST (9%)</td>
        <td>{cgst:.2f}</td>
    </tr>
    <tr>
        <td colspan="5" style="text-align: right;">SGST (9%)</td>
        <td>{sgst:.2f}</td>
    </tr>
    <tr>
        <td colspan="5" style="text-align: right;">Total Amount</td>
        <td>{total_amount:.2f}</td>
    </tr>
</table>

<h3>Amount in Words: {total_amount_words}</h3>

<div class="footer">
    <p>company_name, company_address1, company_address2 | GST Number: </p>  <!-- change the company deatils accordingly -->
    <p>Contact: company_phone | Email: company_email | Website: company_website</p> <!-- change the company contact details accordingly  -->
    <br>
    <p>Thank you for your business!</p>
</div>

<div class="signature">
    <p>For Company Name,</p>
    <p>Authorized Signature</p>
    <p class="default-signature">COMPANY NAME</p>
</div>
<p><strong>NOTE :</strong> This quotation is generated by a computer and does not require a signature.</p>
<h2>Terms & Conditions and Bank Details</h2>
<table class="details-table">
    <tr>
        <td>
            <h4>Terms & Conditions</h4>
            <ul>
"""

# Splitting terms and conditions and adding each to a list item
terms_list = terms_conditions.strip().split("<br>")
for term in terms_list:
    html_content += f"<li>{term}</li>"

html_content += """
            </ul>
        </td>
        <td>
            <h4>Bank Details</h4>
            <ul>
"""

# Splitting bank details and adding each to a list item
bank_details_list = bank_details.strip().split("<br>")
for detail in bank_details_list:
    html_content += f"<li>{detail}</li>"

html_content += """
            </ul>
        </td>
    </tr>
</table>

</body>
</html>
"""

def generate_pdf(html_content):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdfkit.from_string(html_content, tmpfile.name, configuration=config)
            return tmpfile.name
    except Exception as e:
        st.error(f"An error occurred while generating the PDF: {e}")
        return None

if st.button("Generate PDF"):
    pdf_file = generate_pdf(html_content)
    if pdf_file:
        with open(pdf_file, "rb") as f:
            pdf_data = f.read()
            st.download_button(
                label="Download Invoice",
                data=pdf_data,
                file_name=f"{company_name}.pdf",
                mime="application/pdf",
            )
        os.remove(pdf_file)
