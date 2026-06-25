import sqlite3
from datetime import datetime

DB_FILE = "hotel.db"


def get_connection():
    """One place to get a connection — no server, no password, just a local file."""
    return sqlite3.connect(DB_FILE)


def setup_database():
    """Creates all tables if they don't already exist. Safe to run every time."""
    engine = get_connection()
    cursor = engine.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room (
            roomid TEXT,
            roomtype TEXT,
            totalnoofrooms INTEGER,
            charges INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            customerid INTEGER,
            name TEXT,
            phoneno TEXT,
            rtype TEXT,
            rcharge INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookingrecord (
            customerid TEXT,
            dateofbooking TEXT,
            noofdays INTEGER,
            roomtype TEXT,
            roomcharge INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            noofdays INTEGER,
            roomtype TEXT,
            roomcharge INTEGER,
            service INTEGER,
            totalroomcharge INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cancellation (
            customerid TEXT,
            dateofbooking TEXT,
            noofdays INTEGER,
            roomtype TEXT,
            roomcharge INTEGER,
            dateofcancellation TEXT
        )
    """)

    engine.commit()
    engine.close()


setup_database()

f = 1
while f == 1:
    print("1. For Insert Record")
    print("2. For Search Record")
    print("3. For View Record")
    print("4. For Update Record")
    print("5. For Delete Record")
    print("6. For Exit")
    choice = int(input("Enter your choice "))

    if choice == 1:
        print("1.FOR INSERT ROOM RECORD")
        print("2.FOR INSERT CUSTOMER RECORD")
        print("3.FOR INSERT BOOKING  RECORD")
        print("4.FOR INSERT ROOM INVENTORY RECORD")
        print("5.FOR INSERT ROOM CANCELLATION RECORD")
        ch = int(input("Enter your choice "))

        if ch == 1:
            roomid = input("Enter roomid ")
            roomtype = input("Enter room type ")
            totalnoofrooms = input("Enter totalnoofrooms ")
            charge = int(input("Enter room charge "))
            engine = get_connection()
            cursor = engine.cursor()
            query = "insert into room values(?,?,?,?)"
            t = (roomid, roomtype, totalnoofrooms, charge)
            cursor.execute(query, t)
            engine.commit()
            engine.close()

        elif ch == 2:
            customerid = int(input("Enter customer id "))
            name = input("Enter name ")
            phoneno = input("Enter phoneno ")
            RType = input("Enter roomtype ")
            RCharge = int(input("Enter roomcharge "))
            engine = get_connection()
            cursor = engine.cursor()
            qry = "insert into customer values(?,?,?,?,?)"
            t = (customerid, name, phoneno, RType, RCharge)
            cursor.execute(qry, t)
            engine.commit()
            engine.close()

        elif ch == 3:
            customer_id = input("ENTER CUSTOMER ID ")
            dateofbooking = input("ENTER DATE IN FORMAT - YYYY-MM-DD ")
            noofdays = int(input("ENTER NO OF DAYS "))
            roomtype = input("ENTER ROOM TYPE ")
            engine = get_connection()
            cursor = engine.cursor()
            cursor1 = engine.cursor()
            qry1 = "select charges from room where roomtype = ?"
            t1 = (roomtype,)
            cursor1.execute(qry1, t1)
            p = cursor1.fetchall()
            if not p:
                print("No room found with that room type. Add a room first (option 1 -> 1).")
            elif len(p) > 1:
                print("Warning: more than one room matches that room type, so no booking was created.")
                print("Matching charges found:", [i[0] for i in p])
                print("Room types should be unique. Check option 3 -> 1 (View Room Record) to see the duplicates.")
            else:
                roomcharge = p[0][0]
                qry = "insert into bookingrecord values(?,?,?,?,?)"
                t = (customer_id, dateofbooking, noofdays, roomtype, roomcharge)
                cursor.execute(qry, t)
                engine.commit()
            engine.close()

        elif ch == 4:
            customer_id = input("ENTER CUSTOMER ID ")
            engine = get_connection()
            cursor = engine.cursor()
            qry = "select noofdays, roomtype, roomcharge from bookingrecord where customerid = ?"
            t = (customer_id,)
            cursor.execute(qry, t)
            a = cursor.fetchall()
            if not a:
                print("No booking record found for that customer ID. Add a booking first (option 1 -> 3).")
                engine.close()
            else:
                for i in a:
                    print(i)
                    p = int(i[0])
                    p1 = i[1]
                    p2 = int(i[2])
                    service = 1000 * p
                    totalroomcharge = p2 * p + service
                cursor1 = engine.cursor()
                qry = "insert into inventory values(?,?,?,?,?)"
                t = (p, p1, p2, service, totalroomcharge)
                cursor1.execute(qry, t)
                engine.commit()
                engine.close()

        elif ch == 5:
            customer_id = input("ENTER CUSTOMER ID ")
            dateofcancellation = input("ENTER DATEOFCANCELLATION ")
            engine = get_connection()
            cursor = engine.cursor()
            qry = "select * from bookingrecord where customerid = ?"
            t = (customer_id,)
            cursor.execute(qry, t)
            a = cursor.fetchall()
            if not a:
                print("No booking record found for that customer ID.")
                engine.close()
            else:
                for i in a:
                    print(i)
                    p, p1, p2, p3, p4 = i[0], i[1], i[2], i[3], i[4]
                cursor1 = engine.cursor()
                qry = "insert into cancellation values(?,?,?,?,?,?)"
                t = (p, p1, p2, p3, p4, dateofcancellation)
                cursor1.execute(qry, t)
                engine.commit()
                cursor2 = engine.cursor()
                qry = "delete from bookingrecord where customerid = ?"
                t = (customer_id,)
                cursor2.execute(qry, t)
                engine.commit()
                engine.close()

    elif choice == 2:
        print("1.SEARCH ROOM RECORD")
        print("2.SEARCH CUSTOMER RECORD")
        print("3.SEARCH BOOKING  RECORD")
        print("4.SEARCH ROOM INVENTORY RECORD")
        print("5.SEARCH ROOM CANCELLATION RECORD")
        ch = int(input("Enter your choice "))

        if ch == 1:
            roomid = input("Enter roomid ")
            engine = get_connection()
            cursor = engine.cursor()
            qry = "select * from room where roomid = ?"
            t = (roomid,)
            cursor.execute(qry, t)
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("Roomid", i[0])
                print("Type", i[1])
                print("Total number of rooms", i[2])
                print("Charges", i[3])
            engine.close()

        elif ch == 2:
            customerid = int(input("Enter customerid "))
            engine = get_connection()
            cursor = engine.cursor()
            qry = "select * from customer where customerid = ?"
            t = (customerid,)
            cursor.execute(qry, t)
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("Customer Id", i[0])
                print("Name", i[1])
                print("phoneno", i[2])
                print("Room Type", i[3])
                print("Room Charge", i[4])
            engine.close()

        elif ch == 3:
            customerid = int(input("Enter Customer Id "))
            engine = get_connection()
            cursor = engine.cursor()
            qry = "select * from bookingrecord where customerid = ?"
            t = (customerid,)
            cursor.execute(qry, t)
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("Customer Id", i[0])
                print("Date of Booking", i[1])
                print("No of days", i[2])
                print("Room Type", i[3])
                print("Room Charge", i[4])
            engine.close()

        elif ch == 4:
            roomtype = input("Enter Room type ")
            engine = get_connection()
            cursor = engine.cursor()
            qry = "select * from inventory where roomtype = ?"
            t = (roomtype,)
            cursor.execute(qry, t)
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("No of Days", i[0])
                print("Room Type", i[1])
                print("Room Charge", i[2])
                print("Service", i[3])
                print("Total Room Charge", i[4])
            engine.close()

        elif ch == 5:
            customerid = int(input("Enter Customer Id "))
            engine = get_connection()
            cursor = engine.cursor()
            qry = "select * from cancellation where customerid = ?"
            t = (customerid,)
            cursor.execute(qry, t)
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("Customer id", i[0])
                print("Date of booking", i[1])
                print("No of Days", i[2])
                print("Room Type", i[3])
                print("Room Charge", i[4])
                print("Date of Cancellation", i[5])
            engine.close()

    elif choice == 3:
        print("1.VIEW ROOM RECORD")
        print("2.VIEW CUSTOMER RECORD")
        print("3.VIEW BOOKING  RECORD")
        print("4.VIEW ROOM INVENTORY RECORD")
        print("5.VIEW ROOM CANCELLATION RECORD")
        ch = int(input("Enter your choice "))

        if ch == 1:
            engine = get_connection()
            cursor = engine.cursor()
            cursor.execute("select * from room")
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("Roomid", i[0])
                print("Type", i[1])
                print("Total number of rooms", i[2])
                print("Charges", i[3])
            engine.close()

        elif ch == 2:
            engine = get_connection()
            cursor = engine.cursor()
            cursor.execute("select * from customer")
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("Customer Id", i[0])
                print("Name", i[1])
                print("phoneno", i[2])
                print("Room Type", i[3])
                print("Room Charge", i[4])
            engine.close()

        elif ch == 3:
            engine = get_connection()
            cursor = engine.cursor()
            cursor.execute("select * from bookingrecord")
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("Customer Id", i[0])
                print("Date of Booking", i[1])
                print("No of days", i[2])
                print("Room Type", i[3])
                print("Room Charge", i[4])
            engine.close()

        elif ch == 4:
            engine = get_connection()
            cursor = engine.cursor()
            cursor.execute("select * from inventory")
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("No of Days", i[0])
                print("Room Type", i[1])
                print("Room Charge", i[2])
                print("Service", i[3])
                print("Total Room Charge", i[4])
            engine.close()

        elif ch == 5:
            engine = get_connection()
            cursor = engine.cursor()
            cursor.execute("select * from cancellation")
            f_rows = cursor.fetchall()
            for i in f_rows:
                print("Customer id", i[0])
                print("Date of booking", i[1])
                print("No of Days", i[2])
                print("Room Type", i[3])
                print("Room Charge", i[4])
                print("Date of Cancellation", i[5])
            engine.close()

    elif choice == 4:
        print("1.UPDATE ROOM RECORD")
        print("2.UPDATE CUSTOMER RECORD")
        print("3.UPDATE BOOKING RECORD")
        ch = int(input("Enter your choice "))

        if ch == 1:
            roomid = input("Enter room id whose record you want to update ")
            print("1. Update Room type")
            print("2. Update Total number of room")
            print("3. Update Charges")
            ch2 = int(input("Enter your choice "))
            engine = get_connection()
            cursor = engine.cursor()
            if ch2 == 1:
                roomtype = input("Enter room type you want to update ")
                cursor.execute("update room set roomtype = ? where roomid = ?", (roomtype, roomid))
            elif ch2 == 2:
                totalnoofrooms = input("Enter total number of rooms you want to update ")
                cursor.execute("update room set totalnoofrooms = ? where roomid = ?", (totalnoofrooms, roomid))
            elif ch2 == 3:
                charges = int(input("Enter room charges you want to update "))
                cursor.execute("update room set charges = ? where roomid = ?", (charges, roomid))
            engine.commit()
            engine.close()

        elif ch == 2:
            customerid = int(input("Enter Customer Id whose record you want to update "))
            print("1. UPDATE NAME")
            print("2. PHONENO")
            print("3. RTYPE")
            print("4. RCHARGE")
            ch2 = int(input("Enter your choice "))
            engine = get_connection()
            cursor = engine.cursor()
            if ch2 == 1:
                name = input("Enter your name to update ")
                cursor.execute("update customer set name = ? where customerid = ?", (name, customerid))
            elif ch2 == 2:
                phoneno = input("Enter your phoneno to update ")
                cursor.execute("update customer set phoneno = ? where customerid = ?", (phoneno, customerid))
            elif ch2 == 3:
                rtype = input("Enter room type to update ")
                cursor.execute("update customer set rtype = ? where customerid = ?", (rtype, customerid))
            elif ch2 == 4:
                rcharge = int(input("Enter room charge to update "))
                cursor.execute("update customer set rcharge = ? where customerid = ?", (rcharge, customerid))
            engine.commit()
            engine.close()

        elif ch == 3:
            customerid = int(input("Enter Customer Id whose record you want to update "))
            print("1. UPDATE DATEOFBOOKING")
            print("2. NOOFDAYS")
            print("3. ROOMTYPE")
            print("4. ROOMCHARGE")
            ch2 = int(input("Enter your choice "))
            engine = get_connection()
            cursor = engine.cursor()
            if ch2 == 1:
                dateofbooking = input("Enter your dateofbooking to update ")
                cursor.execute("update bookingrecord set dateofbooking = ? where customerid = ?", (dateofbooking, customerid))
            elif ch2 == 2:
                noofdays = int(input("Enter your noofdays to update "))
                cursor.execute("update bookingrecord set noofdays = ? where customerid = ?", (noofdays, customerid))
            elif ch2 == 3:
                roomtype = input("Enter your roomtype to update ")
                cursor.execute("update bookingrecord set roomtype = ? where customerid = ?", (roomtype, customerid))
            elif ch2 == 4:
                roomcharge = int(input("Enter your roomcharge to update "))
                cursor.execute("update bookingrecord set roomcharge = ? where customerid = ?", (roomcharge, customerid))
            engine.commit()
            engine.close()

    elif choice == 5:
        print("1.DELETE ROOM RECORD")
        print("2.DELETE CUSTOMER RECORD")
        print("3.DELETE BOOKING RECORD")
        print("4.DELETE ROOM INVENTORY RECORD")
        print("5.DELETE CANCELLATION RECORD")
        ch = int(input("Enter your choice "))
        engine = get_connection()
        cursor = engine.cursor()

        if ch == 1:
            roomid = input("Enter roomid whose room record you want to delete ")
            cursor.execute("delete from room where roomid = ?", (roomid,))
        elif ch == 2:
            customerid = int(input("Enter customerid whose customer record you want to delete "))
            cursor.execute("delete from customer where customerid = ?", (customerid,))
        elif ch == 3:
            customerid = int(input("Enter customerid whose bookingrecord you want to delete "))
            cursor.execute("delete from bookingrecord where customerid = ?", (customerid,))
        elif ch == 4:
            roomtype = input("Enter roomtype whose inventory record you want to delete ")
            cursor.execute("delete from inventory where roomtype = ?", (roomtype,))
        elif ch == 5:
            customerid = int(input("Enter customerid whose cancellation record you want to delete "))
            cursor.execute("delete from cancellation where customerid = ?", (customerid,))

        engine.commit()
        engine.close()
        print("Record deleted successfully")

    elif choice == 6:
        f = 0
