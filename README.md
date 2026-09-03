# Auctra — Intelligent Forward Auction Platform

A web-based forward auction platform built with Django that allows users to register, create and participate in auctions, place competitive bids, monitor auction activity in real time, and track auction results. The platform provides a secure and user-friendly environment for managing auction listings, evaluating bids, and connecting buyers with sellers through a transparent bidding process.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
  - [User Authentication](#user-authentication)
  - [Auction Management](#auction-management)
  - [Bidding](#bidding)
  - [Auction Results](#auction-results)
  - [Administration](#administration)
- [How It Works](#how-it-works)
- [System Structure](#system-structure)
- [Database](#database)
- [Technology Stack](#technology-stack)
- [Project Status](#project-status)
- [License](#license)

---

## Overview

**Auctra** is a Django-based web application designed to provide a simple online auction experience.

The platform follows a **forward auction model**, where multiple users compete by increasing their bids. The highest valid bid becomes the leading bid and can become the winner when the auction closes.

The project includes user authentication, auction management, bidding functionality, highest-bid tracking, auction results, and a Django administration panel.

---

## Key Features

### User Authentication

- User registration
- User login and logout
- Django-based authentication
- Separate administrator access

### Auction Management

- Create and manage auctions
- Starting price
- Minimum bid increment
- Auction start and end time
- Auction status management
- Active auction dashboard

### Bidding

- Users can participate in active auctions
- Competitive forward bidding
- Individual bids stored in the database
- Current highest bid tracking
- Bidder and auction relationships

### Auction Results

- Winning bidder tracking
- Winning bid tracking
- Final winning price
- Auction closing information

### Administration

The Django Admin panel provides management of:

- Users
- Auction items
- Auctions
- Bids
- Auction results

---

## How It Works

```text
User Registration
        ↓
      Login
        ↓
Auction Dashboard
        ↓
Select Active Auction
        ↓
View Auction Details
        ↓
    Place Bid
        ↓
Highest Bid Updated
        ↓
   Auction Closes
        ↓
 Winner Recorded
```

Auctra uses a **forward auction**, meaning the price moves upward as users compete.

Example:

```text
Starting Price: ₹10,000

Bid 1 → ₹10,500
Bid 2 → ₹11,000
Bid 3 → ₹12,000
Bid 4 → ₹12,500

Winning Bid → ₹12,500
```

---

## System Structure

```text
Auctra/
│
├── auction_project/
│   └── Django project configuration
│
├── auctions/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── bids/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── accounts/
│   └── Authentication and registration
│
├── static/
│   └── auction/
│       ├── css/
│       └── js/
│
├── db.sqlite3
└── manage.py
```

---

## Database

The application uses **SQLite** as its database.

The main models are:

- **Scrap** — currently used as the auction item model
- **Auction** — stores auction information and status
- **Bid** — stores bids placed by users
- **AuctionResult** — stores the final auction outcome
- **User** — Django's built-in authentication model

The auction and bidding models are connected using Django model relationships.

---

## Technology Stack

| Technology   | Purpose               |
| ------------ | --------------------- |
| Python       | Backend               |
| Django       | Web framework         |
| SQLite       | Database              |
| HTML         | Frontend              |
| CSS          | Styling               |
| JavaScript   | Frontend interactions |
| Django Admin | Administration        |

---

## Project Status

**Working Prototype**

Auctra currently provides the core functionality of an online forward auction portal, including authentication, auction management, bidding, highest-bid tracking, auction results, and administrative management.

The project is structured so that additional functionality can be added in future versions.

---

## License

This project is developed for learning and demonstration purposes.
