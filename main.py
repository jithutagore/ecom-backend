from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymysql
from services.query_scrapper import google_search,html_parser,comparer,google_search_morzilla
from services.models_api import UserCreate,Login
from datetime  import datetime,timedelta
import jwt
# Your JWT secret key
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"




# Function to create JWT token
def create_jwt_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Function to decode JWT token
def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Your other functions...

# Your database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='admin123',
    database='ecommerce',
    cursorclass=pymysql.cursors.DictCursor
)

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)



cursor = conn.cursor()

# API endpoints
@app.post("/auth/signup")
async def create_user(user: UserCreate):
    sql = "INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)"
    val = (user.firstName, user.lastName, user.email, user.password)
    cursor.execute(sql, val)
    conn.commit()
    token = create_jwt_token(user.email)  # Create JWT token for the user
    return {"success": True, "token": token}

@app.get("/search/")
async def search(query: str):
    try:
        html_content = google_search(query)
        results = html_parser(html_content)
        return {"results": results}
    except HTTPException as e:
        return {"error": str(e.detail)}
    except ConnectionResetError as e:
        return {"error": "Connection reset by peer"}  # Handle connection reset error gracefully


@app.post("/login/")
async def user_login(login: Login):
    sql = "SELECT * FROM users WHERE email = %s AND password = %s"
    val = (login.email, login.password)
    cursor.execute(sql, val)
    user = cursor.fetchone()
    if user:
        token = create_jwt_token(user['email'])  # Create JWT token for the user
        return {"success": True, "token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    

@app.get("/get_product_info/")
async def get_product_info(url: str):
    html_content = google_search_morzilla(url)
    if html_content:
        product_info = comparer(html_content)
        return product_info
    else:
        return {"error": "Failed to fetch HTML content."}

# Run the application with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8500)
