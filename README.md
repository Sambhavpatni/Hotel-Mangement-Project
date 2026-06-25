# Aurelia — Hotel Front Desk Management System

A full-stack hotel front desk management web application built with Python and Flask, backed by a local SQLite database. It manages rooms, guests, bookings, hotel facilities/amenities, billing, and cancellations through a custom-designed web interface.

A standalone console version of the same logic (`hotel_management_sqlite.py`) is also included for reference.

---

## Features

- **Rooms** — add, view, and remove room types and their nightly rates (room types are enforced as unique to prevent booking conflicts).
- **Customers** — register guests with contact details and a default room preference.
- **Bookings** — book a room for a registered customer; validates that the Customer ID actually exists before creating a booking.
- **Facilities** — a catalog of hotel amenities (Swimming Pool, Spa, Party Lawn, EV Charging, etc.) seeded automatically on first run, plus a usage log to record which guest used which facility and when.
- **Customer Bill** — generates one running bill per stay, combining room charges, a nightly service charge, and any logged facility usage into a single total. Re-generating a bill for the same stay updates the existing bill instead of creating a duplicate.
- **Invoices** — a print-ready, itemized invoice per bill, with an option to share it directly to the guest's phone via a pre-filled WhatsApp message.
- **Cancellations** — cancel an active booking, which logs the cancellation, removes the booking, deletes the related bill, and clears any unbilled facility usage tied to that stay.

---

## Tech Stack

- **Backend:** Python 3, Flask
- **Database:** SQLite (built into Python — no separate database server required)
- **Frontend:** HTML, CSS (custom-designed, no UI framework), Jinja2 templating (Flask's built-in templating engine)

---

## Project Structure

```
hotel_web/
├── app.py                      # Main Flask application — all routes and database logic
├── hotel_management_sqlite.py  # Standalone console version (optional, not required to run the web app)
├── static/
│   └── style.css               # All styling for the web interface
└── templates/                  # HTML pages (Jinja2 templates)
    ├── base.html               # Shared layout: sidebar navigation + page structure
    ├── home.html                # Dashboard
    ├── rooms.html / add_room.html
    ├── customers.html / add_customer.html
    ├── bookings.html / add_booking.html
    ├── facilities.html / add_facility.html / add_facility_usage.html
    ├── bills.html / add_bill.html
    ├── cancellations.html / add_cancellation.html
    └── invoice.html             # Printable invoice page
```

A file named `hotel.db` will be created automatically in this same folder the first time you run the app — that file *is* the database. Back it up if you don't want to lose your data.

---

## Requirements

- Python 3.8 or newer
- Flask (the only external package required)

Check your Python version:

```bash
python --version
```

---

## How to Set Up and Run (Backend + Server)

There is no separate "compile" step — Python and Flask run the application directly, and the database is created automatically. Follow these steps:

### 1. Open the project folder

Open the `hotel_web` folder in VS Code (or any terminal):

- **VS Code:** File → Open Folder → select `hotel_web`
- Open the integrated terminal: `Terminal → New Terminal` (or `` Ctrl+` ``)

### 2. (Recommended) Create a virtual environment

This keeps Flask isolated from other Python projects on your machine. This step is optional but recommended.

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **macOS / Linux:** `source venv/bin/activate`

### 3. Install Flask

```bash
pip install flask
```

### 4. Run the application

```bash
python app.py
```

You should see output similar to:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 5. Open it in your browser

Go to:

```
http://127.0.0.1:5000
```

You'll land on the Dashboard, with navigation for Rooms, Customers, Bookings, Facilities, Customer Bill, and Cancellations.

### 6. Stop the server

Click back into the terminal and press `Ctrl + C`.

---

## Typical Usage Order

The features depend on each other in this order — skipping a step will show a clear warning rather than failing silently:

1. **Add a Room** (Rooms → Add room) — define a room type and its nightly rate.
2. **Add a Customer** (Customers → Add customer) — register the guest.
3. **Add a Booking** (Bookings → Add booking) — book the registered customer into a room type.
4. *(Optional)* **Log Facility Usage** (Facilities → Log usage) — record any amenities the guest used during their stay.
5. **Generate the Bill** (Customer Bill → Generate bill) — combines the room charge, service charge, and any logged facilities into one total. Run this again any time to refresh the bill with newly logged facility usage.
6. **View/Print/Send the Invoice** (Customer Bill → Invoice) — print it, or send it via WhatsApp if the customer's phone number is on file.
7. **Cancel a Booking**, if needed (Cancellations → Cancel a booking) — this cleans up the booking, its bill, and any unbilled facility usage automatically.

---

## Resetting the Database

To start completely fresh, simply delete the `hotel.db` file from the project folder and restart the app — it will recreate all tables (and reseed the facilities catalog) automatically.

```bash
rm hotel.db        # macOS / Linux
del hotel.db       # Windows
```

---

## Notes

- This app runs **locally only** (`127.0.0.1` / `localhost`) — it is not deployed or accessible over the internet.
- `app.run(debug=True)` is enabled for local development. Debug mode should be turned off before any production deployment.
- The WhatsApp invoice-sharing feature opens a pre-filled WhatsApp message using the guest's phone number on file — it does not send anything automatically; you still need to press send.
