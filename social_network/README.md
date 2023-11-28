# Your Project Name

This project aims to build a scalable and efficient social networking API with user authentication, search functionality, friend request management, and friend listing capabilities. The system will ensure proper handling of user interactions while adhering to the specified constraints. The API will be developed using Django Rest Framework to leverage its powerful features and ease of integration with Django's ORM for database operations.

## Prerequisites

- Python 3.x
- [Virtualenv](https://virtualenv.pypa.io/en/latest/) (recommended)

## Getting Started

### 1. Clone the Repository

```bash
git clone 
cd your-repo

# On Windows
python -m venv venv

# On macOS/Linux
python3 -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver

----
# Using Docker
# Go to the root directory
sudo docker-compose up -d


----POSTMAN

I have shared the POSTMAN API collection JSON. You can import it into Postman for testing and exploring the API.

