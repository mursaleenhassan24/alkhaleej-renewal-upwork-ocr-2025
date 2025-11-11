# main.py ya app startup mein
from database import init_database, get_db

# Initialize database (ek baar startup pe)
db = init_database(
    connection_string="mongodb://localhost:27017",
    database_name="your_database"
)

# Ab kahin bhi use kar sakte ho
from database import get_db

# Users operations
db = get_db()

# CREATE user
user_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "account_type": "premium",
    "password": "hashed_password"
}
user_id = await db.users.create(user_data)

# READ user
user = await db.users.get_by_id(user_id)
all_users = await db.users.get_all()

# UPDATE user
await db.users.update(user_id, {"account_type": "enterprise"})

# DELETE user
await db.users.delete(user_id)


# Clients operations
client_data = {
    "phone_number": "1234567890",
    "name": "John Doe"
}
client_id = await db.clients.create(client_data)
client = await db.clients.get_by_id(client_id)


# Requests operations
request_data = {
    "client_id": client_id,
    "status": "pending",
    "source": "mobile_app"
}
request_id = await db.requests.create(request_data)


# Documents operations
document_data = {
    "response_message_id": "msg_123",
    "request_id": request_id,
    "document_type": "qatar_id",
    "file_name": "qatar_id.pdf",
    "file_path": "/uploads/qatar_id.pdf",
    "file_size": 1024,
    "mime_type": "application/pdf"
}
doc_id = await db.documents.create(document_data)


# Qatar ID operations
qatar_id_data = {
    "id_no": "12345678901",
    "name": "Ahmed Ali",
    "expiry_date": "2025-12-31",
    "dob": "1990-01-01",
    "nationality": "Qatar"
}
qid_id = await db.qatar_ids.create(qatar_id_data)


# Istimara operations
istimara_data = {
    "vehicle_number": "123456",
    "vehicle_type": "Sedan",
    "owner_en": "Ahmed Ali",
    "owner_qid": "12345678901",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry"
}
istimara_id = await db.istimaras.create(istimara_data)


# Find operations
pending_requests = await db.requests.find({"status": "pending"})
client_by_phone = await db.clients.find_one({"phone_number": "1234567890"})

# Count operations
total_users = await db.users.count()
pending_count = await db.requests.count({"status": "pending"})


# Shutdown pe close karo
await db.close()