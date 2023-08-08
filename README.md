# OnlineStoreManagementSystem (WEB)

Web-based store management system that allows users to manage products, customers, and orders for an online store. The application provides functionalities for adding, viewing, updating, and deleting products, customers, and orders through a user-friendly web interface.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Accessing the Application](#accessing-the-application)
  - [Managing Products](#managing-products)
  - [Managing Customers](#managing-customers)
  - [Managing Orders](#managing-orders)
- [Demo](#demo)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Description

The OnlineStoreManagementSystem is a web application designed to simplify the management of an online store's products, customers, and orders. Built using Flask, HTML, and SQLite, this application offers an intuitive interface for store administrators to perform various tasks seamlessly.

## Features

- User authentication and authorization for secure access to the application.
- CRUD operations for managing products, customers, and orders.
- Real-time updates on total prices for products and orders.
- Responsive design for a seamless experience on various devices.
- Password hashing and validation for improved security.

## Getting Started

### Prerequisites

- Python 3.x
- Flask 2.3.2
- Flask-Session 0.5.0
- python-dotenv 1.0.0
- Werkzeug 2.3.6

### Installation

1. Clone the repository to your local machine:

   ```
   git clone https://github.com/Trambl/OnlineStoreManagementSystem-WEB-.git
   cd OnlineStoreManagementSystem-WEB-
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Run the application:

   ```
   flask run
   ```

## Usage

### Accessing the Application

1. Open a web browser and navigate to `http://localhost:5000`.

2. If you're a new user, you can register an account. If you're an existing user, log in with your credentials.

### Managing Products

- Add new products by providing the product name, price, and quantity.
- View, update, and delete existing products.
- Monitor the total price of each product in real time.

### Managing Customers

- Add new customers by providing their name, email, and address.
- View, update, and delete existing customer information.

### Managing Orders

- Place new orders by selecting customers and products, along with their quantities.
- View existing orders, including order details and total prices.
- Update orders by adding or removing products.
- Delete orders and associated order items.

## Demo

You can find a live demo of the WebStoreManagementSystem [here](https://youtu.be/tZJ7N5DGe2w).

## License

This project is licensed under the [MIT License](https://www.mit.edu/~amini/LICENSE.md).

## Acknowledgments

The WebStoreManagementSystem is a demonstration project and not intended for production use. It was created as an educational exercise to showcase web development skills using Flask, HTML, and SQLite. Contributions to the project are welcome; feel free to submit issues or pull requests.