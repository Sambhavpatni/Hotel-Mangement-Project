from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # change before deploying live

DB_FILE = "hotel.db"


def get_connection():
    """One place to get a connection. row_factory lets us use column names like a dict."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# A starter catalog of modern hotel amenities, seeded once when the database
# is first created. Charge of 0 means it's complimentary (included free).
DEFAULT_FACILITIES = [
    ("Swimming Pool", "Recreation", 500),
    ("Party Lawn & Banquet Hall", "Events", 15000),
    ("Spa & Wellness Center", "Wellness", 1200),
    ("Fitness Center", "Recreation", 0),
    ("Complimentary Breakfast", "Dining", 0),
    ("High-Speed WiFi", "Connectivity", 0),
    ("Airport Shuttle", "Transport", 800),
    ("Conference & Business Center", "Business", 2000),
    ("EV Charging Station", "Sustainability", 0),
    ("Pet-Friendly Stay", "Comfort", 500),
    ("Concierge & Travel Desk", "Service", 0),
    ("Laundry Service", "Service", 300),
    ("Kids' Play Zone", "Family", 0),
    ("Rooftop Restaurant & Bar", "Dining", 0),
]


def setup_database():
    """Creates all tables if they don't already exist, and migrates older databases forward."""
    engine = get_connection()
    cursor = engine.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room (
            roomid TEXT PRIMARY KEY,
            roomtype TEXT UNIQUE,
            totalnoofrooms INTEGER,
            charges INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            customerid INTEGER PRIMARY KEY,
            name TEXT,
            phoneno TEXT,
            rtype TEXT,
            rcharge INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookingrecord (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customerid TEXT,
            dateofbooking TEXT,
            noofdays INTEGER,
            roomtype TEXT,
            roomcharge INTEGER
        )
    """)

    # Migration: the table used to be called "inventory". Rename it forward
    # to "customerbill" once, so anyone with an older hotel.db keeps their data.
    existing_tables = [row[0] for row in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    if "inventory" in existing_tables and "customerbill" not in existing_tables:
        cursor.execute("ALTER TABLE inventory RENAME TO customerbill")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customerbill (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customerid TEXT,
            noofdays INTEGER,
            roomtype TEXT,
            roomcharge INTEGER,
            service INTEGER,
            facilitycharges INTEGER DEFAULT 0,
            facilities TEXT,
            totalroomcharge INTEGER
        )
    """)

    # Add any newer columns that an older customerbill/inventory table might be missing.
    bill_columns = [row[1] for row in cursor.execute("PRAGMA table_info(customerbill)").fetchall()]
    if "customerid" not in bill_columns:
        cursor.execute("ALTER TABLE customerbill ADD COLUMN customerid TEXT")
    if "facilitycharges" not in bill_columns:
        cursor.execute("ALTER TABLE customerbill ADD COLUMN facilitycharges INTEGER DEFAULT 0")
    if "facilities" not in bill_columns:
        cursor.execute("ALTER TABLE customerbill ADD COLUMN facilities TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cancellation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customerid TEXT,
            dateofbooking TEXT,
            noofdays INTEGER,
            roomtype TEXT,
            roomcharge INTEGER,
            dateofcancellation TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facility (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            category TEXT,
            charge INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facilityusage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customerid TEXT,
            facilityname TEXT,
            category TEXT,
            charge INTEGER,
            usagedate TEXT,
            billed INTEGER DEFAULT 0
        )
    """)

    # Seed the amenities catalog (only inserts ones that don't already exist by name).
    cursor.executemany(
        "INSERT OR IGNORE INTO facility (name, category, charge) VALUES (?,?,?)",
        DEFAULT_FACILITIES
    )

    engine.commit()
    engine.close()


setup_database()


@app.route("/")
def home():
    engine = get_connection()
    counts = {}
    for table in ["room", "customer", "bookingrecord", "customerbill", "cancellation", "facility", "facilityusage"]:
        counts[table] = engine.execute(f"select count(*) from {table}").fetchone()[0]
    engine.close()
    return render_template("home.html", counts=counts)


# ---------- ROOMS ----------
@app.route("/rooms")
def list_rooms():
    engine = get_connection()
    rooms = engine.execute("select * from room").fetchall()
    engine.close()
    return render_template("rooms.html", rooms=rooms)


@app.route("/rooms/add", methods=["GET", "POST"])
def add_room():
    if request.method == "POST":
        roomid = request.form["roomid"]
        roomtype = request.form["roomtype"]
        try:
            totalnoofrooms = int(request.form["totalnoofrooms"])
            charges = int(request.form["charges"])
        except ValueError:
            flash("Rooms and charge must be whole numbers.", "error")
            return render_template("add_room.html")

        engine = get_connection()
        try:
            engine.execute("insert into room values (?,?,?,?)",
                            (roomid, roomtype, totalnoofrooms, charges))
            engine.commit()
            flash("Room added.", "success")
            return redirect(url_for("list_rooms"))
        except sqlite3.IntegrityError:
            flash("That Room ID or Room Type already exists. Both must be unique.", "error")
        finally:
            engine.close()
    return render_template("add_room.html")


@app.route("/rooms/delete/<roomid>")
def delete_room(roomid):
    engine = get_connection()
    engine.execute("delete from room where roomid = ?", (roomid,))
    engine.commit()
    engine.close()
    flash("Room deleted.", "success")
    return redirect(url_for("list_rooms"))


# ---------- CUSTOMERS ----------
@app.route("/customers")
def list_customers():
    engine = get_connection()
    customers = engine.execute("select * from customer").fetchall()
    engine.close()
    return render_template("customers.html", customers=customers)


@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        name = request.form["name"]
        phoneno = request.form["phoneno"]
        rtype = request.form["rtype"]
        try:
            customerid = int(request.form["customerid"])
            rcharge = int(request.form["rcharge"])
        except ValueError:
            flash("Customer ID and room rate must be whole numbers.", "error")
            return render_template("add_customer.html")

        engine = get_connection()
        try:
            engine.execute("insert into customer values (?,?,?,?,?)",
                            (customerid, name, phoneno, rtype, rcharge))
            engine.commit()
            flash("Customer added.", "success")
            return redirect(url_for("list_customers"))
        except sqlite3.IntegrityError:
            flash("That Customer ID already exists.", "error")
        finally:
            engine.close()
    return render_template("add_customer.html")


@app.route("/customers/delete/<int:customerid>")
def delete_customer(customerid):
    engine = get_connection()
    engine.execute("delete from customer where customerid = ?", (customerid,))
    engine.commit()
    engine.close()
    flash("Customer deleted.", "success")
    return redirect(url_for("list_customers"))


# ---------- BOOKINGS ----------
@app.route("/bookings")
def list_bookings():
    engine = get_connection()
    bookings = engine.execute("select * from bookingrecord").fetchall()
    engine.close()
    return render_template("bookings.html", bookings=bookings)


@app.route("/bookings/add", methods=["GET", "POST"])
def add_booking():
    if request.method == "POST":
        customerid_raw = request.form["customerid"]
        dateofbooking = request.form["dateofbooking"]
        roomtype = request.form["roomtype"]
        try:
            noofdays = int(request.form["noofdays"])
        except ValueError:
            flash("Number of nights must be a whole number.", "error")
            return render_template("add_booking.html")

        engine = get_connection()

        # Confirm this Customer ID actually belongs to a registered customer,
        # so a mistyped ID (e.g. a Room ID instead) is caught immediately.
        try:
            customerid_lookup = int(customerid_raw)
        except ValueError:
            customerid_lookup = None

        customer_match = None
        if customerid_lookup is not None:
            customer_match = engine.execute(
                "select name from customer where customerid = ?", (customerid_lookup,)
            ).fetchone()

        if not customer_match:
            flash(
                f"No registered customer found with ID '{customerid_raw}'. "
                f"Check you haven't entered a Room ID instead, or add this customer first (Customers -> Add customer).",
                "error"
            )
            engine.close()
            return render_template("add_booking.html")

        matches = engine.execute("select charges from room where roomtype = ?", (roomtype,)).fetchall()

        if not matches:
            flash("No room found with that room type. Add a room first.", "error")
        elif len(matches) > 1:
            flash("More than one room matches that room type. Room types must be unique.", "error")
        else:
            roomcharge = matches[0]["charges"]
            engine.execute(
                "insert into bookingrecord (customerid, dateofbooking, noofdays, roomtype, roomcharge) values (?,?,?,?,?)",
                (customerid_raw, dateofbooking, noofdays, roomtype, roomcharge)
            )
            engine.commit()
            engine.close()
            flash(f"Booking added for {customer_match['name']} (Customer ID {customerid_raw}).", "success")
            return redirect(url_for("list_bookings"))
        engine.close()
    return render_template("add_booking.html")


@app.route("/bookings/delete/<int:booking_id>")
def delete_booking(booking_id):
    engine = get_connection()
    engine.execute("delete from bookingrecord where id = ?", (booking_id,))
    engine.commit()
    engine.close()
    flash("Booking deleted.", "success")
    return redirect(url_for("list_bookings"))


# ---------- FACILITIES ----------
@app.route("/facilities")
def list_facilities():
    engine = get_connection()
    facilities = engine.execute("select * from facility order by category, name").fetchall()
    usage = engine.execute(
        "select * from facilityusage order by id desc"
    ).fetchall()
    engine.close()
    return render_template("facilities.html", facilities=facilities, usage=usage)


@app.route("/facilities/add", methods=["GET", "POST"])
def add_facility():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        try:
            charge = int(request.form["charge"])
        except ValueError:
            flash("Charge must be a whole number (use 0 for complimentary).", "error")
            return render_template("add_facility.html")

        engine = get_connection()
        try:
            engine.execute("insert into facility (name, category, charge) values (?,?,?)",
                            (name, category, charge))
            engine.commit()
            flash("Facility added to the catalog.", "success")
            return redirect(url_for("list_facilities"))
        except sqlite3.IntegrityError:
            flash("A facility with that name already exists.", "error")
        finally:
            engine.close()
    return render_template("add_facility.html")


@app.route("/facilities/delete/<int:facility_id>")
def delete_facility(facility_id):
    engine = get_connection()
    engine.execute("delete from facility where id = ?", (facility_id,))
    engine.commit()
    engine.close()
    flash("Facility removed from the catalog.", "success")
    return redirect(url_for("list_facilities"))


@app.route("/facilities/use", methods=["GET", "POST"])
def add_facility_usage():
    engine = get_connection()
    facilities = engine.execute("select * from facility order by category, name").fetchall()

    if request.method == "POST":
        customerid_raw = request.form["customerid"]
        facilityname = request.form["facilityname"]
        usagedate = request.form["usagedate"]

        try:
            customerid_lookup = int(customerid_raw)
        except ValueError:
            customerid_lookup = None

        customer_match = None
        if customerid_lookup is not None:
            customer_match = engine.execute(
                "select name from customer where customerid = ?", (customerid_lookup,)
            ).fetchone()

        if not customer_match:
            flash(f"No registered customer found with ID '{customerid_raw}'.", "error")
            engine.close()
            return render_template("add_facility_usage.html", facilities=facilities)

        facility_row = engine.execute(
            "select category, charge from facility where name = ?", (facilityname,)
        ).fetchone()

        if not facility_row:
            flash("Please choose a valid facility from the list.", "error")
            engine.close()
            return render_template("add_facility_usage.html", facilities=facilities)

        engine.execute(
            "insert into facilityusage (customerid, facilityname, category, charge, usagedate, billed) values (?,?,?,?,?,0)",
            (customerid_raw, facilityname, facility_row["category"], facility_row["charge"], usagedate)
        )
        engine.commit()
        engine.close()
        flash(f"Logged {facilityname} for {customer_match['name']}. It'll be added to their next bill.", "success")
        return redirect(url_for("list_facilities"))

    engine.close()
    return render_template("add_facility_usage.html", facilities=facilities)


@app.route("/facilities/use/delete/<int:usage_id>")
def delete_facility_usage(usage_id):
    engine = get_connection()
    engine.execute("delete from facilityusage where id = ?", (usage_id,))
    engine.commit()
    engine.close()
    flash("Usage entry removed.", "success")
    return redirect(url_for("list_facilities"))


# ---------- CUSTOMER BILL ----------
@app.route("/bills")
def list_bills():
    engine = get_connection()
    bills = engine.execute("select * from customerbill order by id desc").fetchall()
    engine.close()
    return render_template("bills.html", bills=bills)


@app.route("/bills/add", methods=["GET", "POST"])
def add_bill():
    if request.method == "POST":
        customerid = request.form["customerid"]
        engine = get_connection()
        bookings = engine.execute(
            "select noofdays, roomtype, roomcharge from bookingrecord where customerid = ?",
            (customerid,)
        ).fetchall()

        if not bookings:
            flash("No booking record found for that customer ID. Add a booking first.", "error")
            engine.close()
            return render_template("add_bill.html")

        # Pull any facility usage logged for this guest that hasn't been billed yet.
        usage_rows = engine.execute(
            "select id, facilityname, charge from facilityusage where customerid = ? and billed = 0",
            (customerid,)
        ).fetchall()
        facility_total = sum(u["charge"] for u in usage_rows)
        facility_names = ", ".join(u["facilityname"] for u in usage_rows) if usage_rows else None

        # Facility charges get folded into the bill once, not once per booking row,
        # so a guest with two open bookings doesn't get double-charged for the spa visit.
        bookings_list = list(bookings)
        last_index = len(bookings_list) - 1
        for idx, b in enumerate(bookings_list):
            noofdays = b["noofdays"]
            roomtype = b["roomtype"]
            roomcharge = b["roomcharge"]
            service = 1000 * noofdays
            this_facility_total = facility_total if idx == last_index else 0
            this_facility_names = facility_names if idx == last_index else None
            total = roomcharge * noofdays + service + this_facility_total
            engine.execute(
                "insert into customerbill (customerid, noofdays, roomtype, roomcharge, service, facilitycharges, facilities, totalroomcharge) values (?,?,?,?,?,?,?,?)",
                (customerid, noofdays, roomtype, roomcharge, service, this_facility_total, this_facility_names, total)
            )

        if usage_rows:
            engine.executemany(
                "update facilityusage set billed = 1 where id = ?",
                [(u["id"],) for u in usage_rows]
            )

        engine.commit()
        engine.close()
        flash("Customer bill generated.", "success")
        return redirect(url_for("list_bills"))
    return render_template("add_bill.html")


@app.route("/bills/delete/<int:bill_id>")
def delete_bill(bill_id):
    engine = get_connection()
    engine.execute("delete from customerbill where id = ?", (bill_id,))
    engine.commit()
    engine.close()
    flash("Bill deleted.", "success")
    return redirect(url_for("list_bills"))


# ---------- CANCELLATIONS ----------
@app.route("/cancellations")
def list_cancellations():
    engine = get_connection()
    items = engine.execute("select * from cancellation").fetchall()
    engine.close()
    return render_template("cancellations.html", items=items)


@app.route("/cancellations/delete/<int:item_id>")
def delete_cancellation(item_id):
    engine = get_connection()
    engine.execute("delete from cancellation where id = ?", (item_id,))
    engine.commit()
    engine.close()
    flash("Cancellation entry removed.", "success")
    return redirect(url_for("list_cancellations"))


@app.route("/cancellations/add", methods=["GET", "POST"])
def add_cancellation():
    if request.method == "POST":
        customerid = request.form["customerid"]
        dateofcancellation = request.form["dateofcancellation"]

        engine = get_connection()
        bookings = engine.execute("select * from bookingrecord where customerid = ?", (customerid,)).fetchall()

        if not bookings:
            flash("No booking record found for that customer ID.", "error")
        else:
            for b in bookings:
                engine.execute(
                    "insert into cancellation (customerid, dateofbooking, noofdays, roomtype, roomcharge, dateofcancellation) values (?,?,?,?,?,?)",
                    (b["customerid"], b["dateofbooking"], b["noofdays"], b["roomtype"], b["roomcharge"], dateofcancellation)
                )
            engine.execute("delete from bookingrecord where customerid = ?", (customerid,))
            deleted_bills = engine.execute("delete from customerbill where customerid = ?", (customerid,)).rowcount
            engine.commit()
            engine.close()
            if deleted_bills:
                flash(f"Cancellation recorded. Booking and {deleted_bills} related bill(s) removed.", "success")
            else:
                flash("Cancellation recorded.", "success")
            return redirect(url_for("list_cancellations"))
        engine.close()
    return render_template("add_cancellation.html")


if __name__ == "__main__":
    app.run(debug=True)
