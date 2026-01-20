# M-Pesa Backend API Documentation

## Project Setup

### 1. Install Dependencies

```bash
pip install django djangorestframework django-cors-headers psycopg2-binary
```

### 2. Create Django Project Structure

```bash
django-admin startproject mpesa_backend .
python manage.py startapp accounts
```

### 3. Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run Server

```bash
python manage.py runserver
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### Authentication Endpoints

#### 1. Register User
- **URL**: `/api/auth/register/`
- **Method**: `POST`
- **Auth Required**: No

**Request Body:**
```json
{
  "phone_number": "+254712345678",
  "full_name": "John Doe",
  "pin": "1234",
  "confirm_pin": "1234"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": "uuid-here",
    "phone_number": "+254712345678",
    "full_name": "John Doe",
    "balance": "0.00",
    "created_at": "2025-01-20T10:30:00Z"
  }
}
```

#### 2. Login
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Auth Required**: No

**Request Body:**
```json
{
  "phone_number": "+254712345678",
  "pin": "1234"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": "uuid-here",
    "phone_number": "+254712345678",
    "full_name": "John Doe",
    "balance": "5000.00",
    "created_at": "2025-01-20T10:30:00Z"
  }
}
```

#### 3. Logout
- **URL**: `/api/auth/logout/`
- **Method**: `POST`
- **Auth Required**: Yes

**Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

---

### Transaction Endpoints

All transaction endpoints require authentication. Include the token in headers:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

#### 1. Check Balance
- **URL**: `/api/transactions/balance/`
- **Method**: `GET`
- **Auth Required**: Yes

**Response:**
```json
{
  "phone_number": "+254712345678",
  "balance": "5000.00",
  "full_name": "John Doe"
}
```

#### 2. Send Money
- **URL**: `/api/transactions/send_money/`
- **Method**: `POST`
- **Auth Required**: Yes

**Request Body:**
```json
{
  "receiver_phone": "+254798765432",
  "amount": "500.00",
  "description": "Payment for services"
}
```

**Response:**
```json
{
  "message": "Money sent successfully",
  "transaction": {
    "id": "uuid-here",
    "transaction_code": "ABC123XYZ789",
    "sender_phone": "+254712345678",
    "receiver_phone": "+254798765432",
    "amount": "500.00",
    "transaction_type": "SEND",
    "status": "COMPLETED",
    "description": "Payment for services",
    "created_at": "2025-01-20T11:15:00Z"
  },
  "new_balance": "4500.00"
}
```

#### 3. Deposit Money
- **URL**: `/api/transactions/deposit/`
- **Method**: `POST`
- **Auth Required**: Yes

**Request Body:**
```json
{
  "amount": "1000.00",
  "description": "Deposit from bank"
}
```

**Response:**
```json
{
  "message": "Deposit successful",
  "transaction": {
    "id": "uuid-here",
    "transaction_code": "DEP987ZYX654",
    "sender_phone": null,
    "receiver_phone": "+254712345678",
    "amount": "1000.00",
    "transaction_type": "DEPOSIT",
    "status": "COMPLETED",
    "description": "Deposit from bank",
    "created_at": "2025-01-20T11:20:00Z"
  },
  "new_balance": "5500.00"
}
```

#### 4. Withdraw Money
- **URL**: `/api/transactions/withdraw/`
- **Method**: `POST`
- **Auth Required**: Yes

**Request Body:**
```json
{
  "amount": "200.00",
  "description": "ATM withdrawal"
}
```

**Response:**
```json
{
  "message": "Withdrawal successful",
  "transaction": {
    "id": "uuid-here",
    "transaction_code": "WTH456ABC321",
    "sender_phone": "+254712345678",
    "receiver_phone": null,
    "amount": "200.00",
    "transaction_type": "WITHDRAW",
    "status": "COMPLETED",
    "description": "ATM withdrawal",
    "created_at": "2025-01-20T11:25:00Z"
  },
  "new_balance": "5300.00"
}
```

#### 5. Transaction History
- **URL**: `/api/transactions/history/`
- **Method**: `GET`
- **Auth Required**: Yes

**Response:**
```json
[
  {
    "id": "uuid-here",
    "transaction_code": "ABC123XYZ789",
    "sender_phone": "+254712345678",
    "receiver_phone": "+254798765432",
    "amount": "500.00",
    "transaction_type": "SEND",
    "status": "COMPLETED",
    "description": "Payment for services",
    "created_at": "2025-01-20T11:15:00Z"
  },
  {
    "id": "uuid-here",
    "transaction_code": "DEP987ZYX654",
    "sender_phone": null,
    "receiver_phone": "+254712345678",
    "amount": "1000.00",
    "transaction_type": "DEPOSIT",
    "status": "COMPLETED",
    "description": "Deposit from bank",
    "created_at": "2025-01-20T11:20:00Z"
  }
]
```

---

## Client Integration Examples

### C# Example

```csharp
using System.Net.Http;
using System.Text;
using Newtonsoft.Json;

public class MpesaClient
{
    private readonly HttpClient _client;
    private string _token;

    public MpesaClient()
    {
        _client = new HttpClient();
        _client.BaseAddress = new Uri("http://localhost:8000/api/");
    }

    public async Task<bool> Login(string phoneNumber, string pin)
    {
        var data = new { phone_number = phoneNumber, pin = pin };
        var content = new StringContent(JsonConvert.SerializeObject(data), Encoding.UTF8, "application/json");
        
        var response = await _client.PostAsync("auth/login/", content);
        var result = await response.Content.ReadAsStringAsync();
        var loginResult = JsonConvert.DeserializeObject<dynamic>(result);
        
        _token = loginResult.token;
        _client.DefaultRequestHeaders.Add("Authorization", $"Token {_token}");
        
        return response.IsSuccessStatusCode;
    }

    public async Task<decimal> GetBalance()
    {
        var response = await _client.GetAsync("transactions/balance/");
        var result = await response.Content.ReadAsStringAsync();
        var balanceData = JsonConvert.DeserializeObject<dynamic>(result);
        
        return balanceData.balance;
    }
}
```

### Java Example

```java
import okhttp3.*;
import org.json.JSONObject;

public class MpesaClient {
    private final OkHttpClient client;
    private String token;
    private static final String BASE_URL = "http://localhost:8000/api/";

    public MpesaClient() {
        this.client = new OkHttpClient();
    }

    public boolean login(String phoneNumber, String pin) throws Exception {
        JSONObject json = new JSONObject();
        json.put("phone_number", phoneNumber);
        json.put("pin", pin);

        RequestBody body = RequestBody.create(
            json.toString(),
            MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
            .url(BASE_URL + "auth/login/")
            .post(body)
            .build();

        Response response = client.newCall(request).execute();
        JSONObject result = new JSONObject(response.body().string());
        
        this.token = result.getString("token");
        return response.isSuccessful();
    }

    public double getBalance() throws Exception {
        Request request = new Request.Builder()
            .url(BASE_URL + "transactions/balance/")
            .addHeader("Authorization", "Token " + token)
            .get()
            .build();

        Response response = client.newCall(request).execute();
        JSONObject result = new JSONObject(response.body().string());
        
        return result.getDouble("balance");
    }
}
```

### HTML/JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>M-Pesa Client</title>
</head>
<body>
    <h1>M-Pesa Web Client</h1>
    <div id="login">
        <input type="text" id="phone" placeholder="Phone Number">
        <input type="password" id="pin" placeholder="PIN">
        <button onclick="login()">Login</button>
    </div>
    <div id="balance" style="display:none;">
        <h2>Balance: <span id="balanceAmount"></span></h2>
        <button onclick="getBalance()">Refresh Balance</button>
    </div>

    <script>
        let token = '';

        async function login() {
            const phone = document.getElementById('phone').value;
            const pin = document.getElementById('pin').value;

            const response = await fetch('http://localhost:8000/api/auth/login/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone_number: phone, pin: pin})
            });

            const data = await response.json();
            token = data.token;
            
            document.getElementById('login').style.display = 'none';
            document.getElementById('balance').style.display = 'block';
            
            getBalance();
        }

        async function getBalance() {
            const response = await fetch('http://localhost:8000/api/transactions/balance/', {
                headers: {'Authorization': `Token ${token}`}
            });

            const data = await response.json();
            document.getElementById('balanceAmount').textContent = data.balance;
        }
    </script>
</body>
</html>
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request creating a resource
- `400 Bad Request` - Invalid data or business logic error
- `401 Unauthorized` - Missing or invalid authentication token
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "error": "Insufficient balance"
}
```

Or for validation errors:
```json
{
  "field_name": ["Error message"]
}
```

---

## Notes

- All monetary values use 2 decimal places
- Phone numbers should include country code (e.g., +254)
- Tokens don't expire but can be invalidated via logout
- All timestamps are in UTC
- Transaction codes are automatically generated and unique