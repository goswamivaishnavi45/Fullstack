# Helper (not part of the API): turn an existing user into an admin.
# Run: python make_admin.py someone@example.com
# (Signup always creates role "user"; letting the client choose its own role would be a security hole.)
import sys

from app.db.session import SessionLocal
from app.services.users import get_user_by_email

with SessionLocal() as db:
    user = get_user_by_email(db, sys.argv[1])
    if user is None:
        print("No user with that email - sign up first.")
    else:
        user.role = "admin"
        db.commit()
        print(f"{user.email} is now an admin.")
