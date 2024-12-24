# FreshBasket

FreshBasket is a scalable e-commerce platform for selling fresh vegetables and fruits, developed using Python Flask and hosted on AWS EC2 with Amazon RDS for database management. It ensures high availability, scalability, and efficient handling of user interactions, product catalogs, and order processing.

---

## Features
- User authentication and secure login.
- Browse and search for products.
- Add/remove items to the shopping cart.
- Order placement and tracking.
- Cloud hosting with AWS EC2 and scalable database via Amazon RDS.

---

## Tech Stack
- **Backend**: Python Flask  
- **Database**: Amazon RDS  
- **Cloud Infrastructure**: AWS EC2, AWS S3 (optional)  
- **Frontend**: (Optional - React/HTML/CSS)  

---

## Installation & Setup
1. Clone the repo: `git clone https://github.com/your-username/freshbasket.git && cd freshbasket`
2. Install dependencies: `pip install -r requirements.txt`
3. Add `.env` file:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URI=<Amazon RDS URI>
   SECRET_KEY=<Your Secret Key>
4.Run the app: flask run (accessible at http://127.0.0.1:5000).
