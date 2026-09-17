from flask import Flask, render_template, request, redirect, session
import sqlite3
import urllib.parse
from datetime import datetime
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import random

app = Flask(__name__)
app.secret_key = "rentmanager"

def get_db():
    conn = sqlite3.connect("rent.db")
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/")
def home():
    return redirect("/login")


@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/login")

    conn = get_db()

    rooms = conn.execute("SELECT * FROM rooms").fetchall()

    data = []

    for room in rooms:

        last = conn.execute(
        "SELECT * FROM bills WHERE room_id=? ORDER BY id DESC LIMIT 1",
        (room["id"],)
        ).fetchone()

        data.append((room, last if last else {"units": 0, "total": 0}))

    conn.close()

    return render_template("index.html", data=data)


@app.route("/generate", methods=["POST"])
def generate():

    room_id = request.form["room_id"]
    curr = int(request.form["current"])
    water = int(request.form["water"])
    balance = int(request.form["balance"])

    conn = get_db()

    room = conn.execute(
    "SELECT * FROM rooms WHERE id=?",
    (room_id,)
    ).fetchone()

    last = conn.execute(
    "SELECT * FROM bills WHERE room_id=? ORDER BY id DESC LIMIT 1",
    (room_id,)
    ).fetchone()

    prev = 0
    if last:
        prev = last["curr_reading"]

    units = curr - prev
    electricity = units * 12

    total = room["rent"] + electricity + water + balance

    month = datetime.now().strftime("%B %Y")

    conn.execute("""
    INSERT INTO bills
    (room_id,prev_reading,curr_reading,units,electricity,water,balance,total,month)
    VALUES(?,?,?,?,?,?,?,?,?)
    """,
    (room_id,prev,curr,units,electricity,water,balance,total,month)
    )

    conn.commit()
    conn.close()

    return f"""
    <h2>Bill Generated</h2>
    Previous Reading: {prev}<br>
    Units Used: {units}<br>
    Electricity: {electricity}<br>
    Total Bill: {total}<br><br>
    <a href="/dashboard">Back</a>
    """


@app.route("/history/<room_id>")
def history(room_id):

    conn = get_db()

    room = conn.execute(
    "SELECT * FROM rooms WHERE id=?",
    (room_id,)
    ).fetchone()

    bills = conn.execute(
    "SELECT * FROM bills WHERE room_id=?",
    (room_id,)
    ).fetchall()

    conn.close()

    return render_template("history.html", room=room, bills=bills)
@app.route("/send/<int:room_id>")
def send(room_id):

    conn = get_db()

    room = conn.execute(
    "SELECT * FROM rooms WHERE id=?",
    (room_id,)
    ).fetchone()

    last = conn.execute(
    "SELECT * FROM bills WHERE room_id=? ORDER BY id DESC LIMIT 1",
    (room_id,)
    ).fetchone()

    if not last:
        return "No bill yet"

    message = f"""
⚡ Electricity Bill

Room: {room['room_number']}
Rent: ₹{room['rent']}

Units Used: {last['units']}
Total Bill: ₹{last['total']}

Please pay your bill Via Phone Pay Or Cash
For Phone Pay use:chhayasalunkhe1977@axl
Phone No: 7972722366(Chhaya Salunkhe)
"""

    phone = room["phone"]

    text = urllib.parse.quote(message)

    url = f"https://wa.me/91{phone}?text={text}"

    conn.close()

    return redirect(url)

@app.route("/tenants")
def tenants():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM tenants
        ORDER BY room_number
    """)

    tenants = cursor.fetchall()

    conn.close()

    return render_template(
        "tenants.html",
        tenants=tenants
    )

@app.route("/add_tenant", methods=["POST"])
def add_tenant():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tenants
        (
        room_number,
        name,
        profession,
        phone,
        joining_date,
        leaving_date,
        rent,
        deposit
        )

        VALUES
        (?,?,?,?,?,?,?,?)

    """,

    (

        request.form["room_number"],
        request.form["name"],
        request.form["profession"],
        request.form["phone"],
        request.form["joining_date"],
        request.form["leaving_date"],
        request.form["rent"],
        request.form["deposit"]

    ))

    conn.commit()
    conn.close()

    return redirect("/tenants")

@app.route("/update_tenant", methods=["POST"])
def update_tenant():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE tenants

        SET

        room_number=?,
        name=?,
        profession=?,
        phone=?,
        joining_date=?,
        leaving_date=?,
        rent=?,
        deposit=?

        WHERE id=?

    """,

    (

        request.form["room_number"],
        request.form["name"],
        request.form["profession"],
        request.form["phone"],
        request.form["joining_date"],
        request.form["leaving_date"],
        request.form["rent"],
        request.form["deposit"],
        request.form["id"]

    ))

    conn.commit()

    conn.close()

    return redirect("/tenants")

@app.route("/delete_tenant/<int:id>")
def delete_tenant(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM tenants WHERE id=?",

        (id,)

    )

    conn.commit()

    conn.close()

    return redirect("/tenants")

@app.route("/delete/<int:bill_id>")
def delete(bill_id):

    conn = get_db()

    conn.execute("DELETE FROM bills WHERE id=?", (bill_id,))

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "salunkhe_corner" and password == "sc5737":
            session["admin"] = True
            return redirect("/dashboard")

        return "Invalid Login"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")
@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect("/login")

    conn = get_db()

    rooms = conn.execute(
        "SELECT * FROM rooms ORDER BY room_number"
    ).fetchall()

    settings = conn.execute(
        "SELECT * FROM settings LIMIT 1"
    ).fetchone()

    conn.close()

    return render_template(
        "admin.html",
        rooms=rooms,
        settings=settings
    )

@app.route("/update_admin", methods=["POST"])
def update_admin():

    if "admin" not in session:
        return redirect("/login")

    conn = get_db()

    conn.execute("""
        UPDATE settings
        SET
            building_name=?,
            owner_name=?,
            owner_phone=?
        WHERE id=1
    """,
    (
        request.form["building_name"],
        request.form["owner_name"],
        request.form["owner_phone"]
    ))

    ids = request.form.getlist("id[]")
    phones = request.form.getlist("phone[]")
    rents = request.form.getlist("rent[]")

    for room_id, phone, rent in zip(ids, phones, rents):

        conn.execute("""
            UPDATE rooms
            SET
                phone=?,
                rent=?
            WHERE id=?
        """,
        (
            phone,
            rent,
            room_id
        ))

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/summary")
def summary():

    conn = get_db()

    rooms = conn.execute("SELECT * FROM rooms").fetchall()



    room_names=[]
    room_units=[]
    room_bills=[]

    total_rent=0
    total_units=0
    total_bills=0

    for r in rooms:

        total_rent += r["rent"]
        room_names.append(r["room_number"])

        last = conn.execute(
        "SELECT units,total FROM bills WHERE room_id=? ORDER BY id DESC LIMIT 1",
        (r["id"],)
        ).fetchone()

        if last:
            room_units.append(last["units"])
            room_bills.append(last["total"])
            total_units += last["units"]
            total_bills += last["total"]
        else:
            room_units.append(0)
            room_bills.append(0)

    conn.close()    # <-- ADD THIS LINE

    return render_template(
        "summary.html",
        rooms=len(rooms),
        total_rent=total_rent,
        total_units=total_units,
        total_bills=total_bills,
        room_names=room_names,
        room_units=room_units,
        room_bills=room_bills
    )



@app.route("/fix")
def fix():
    conn = get_db()
    conn.execute("UPDATE bills SET total = 3705 WHERE id = 1")
    conn.commit()
    conn.close()
    return "Updated successfully"


@app.route("/download-summary-pdf")
def download_summary_pdf():

    conn = get_db()
    rooms = conn.execute("SELECT * FROM rooms").fetchall()

    data = []
    total_units = 0
    rate = 12

    for r in rooms:
        last = conn.execute(
            "SELECT units FROM bills WHERE room_id=? ORDER BY id DESC LIMIT 1",
            (r["id"],)
        ).fetchone()

        units = last["units"] if last else 0
        amount = units * rate

        total_units += units
        data.append([r["room_number"], units, f"₹{rate}", f"₹{amount}"])

    conn.close()

    

    

    file_path = "summary_report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Header
    elements.append(Paragraph("<b>SALUNKHE CORNER</b>", styles['Title']))
    elements.append(Paragraph("Monthly Electricity Consumption Report", styles['Normal']))
    elements.append(Spacer(1, 10))

    # Date & ID
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    report_id = f"SC-2026-{random.randint(1000,9999)}"

    elements.append(Paragraph(f"Date: {now}", styles['Normal']))
    elements.append(Paragraph(f"Report ID: {report_id}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Table
    table_data = [["Room", "Units", "Rate", "Amount"]] + data

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("ALIGN",(0,0),(-1,-1),"CENTER")
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Summary
    total_amount = total_units * rate

    elements.append(Paragraph("<b>Summary</b>", styles['Heading2']))
    elements.append(Paragraph(f"Total Rooms: {len(rooms)}", styles['Normal']))
    elements.append(Paragraph(f"Total Units: {total_units}", styles['Normal']))
    elements.append(Paragraph(f"Rate: ₹{rate}", styles['Normal']))
    elements.append(Paragraph(f"Total Amount: ₹{total_amount}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Footer
    elements.append(Paragraph("Generated by: Salunkhe Corner System", styles['Normal']))
    elements.append(Paragraph(f"Date & Time: {now}", styles['Normal']))

    doc.build(elements)

    return send_file(file_path, as_attachment=True)




if __name__ == "__main__":
    app.run(debug=True)