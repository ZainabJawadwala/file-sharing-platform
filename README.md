# File Sharing Platform

## Project Overview

This project implements backend helpers for authentication and AWS S3-based file uploads for a file-sharing platform. The frontend contains a simple upload form that allows users to submit files to an upload endpoint.

The main goal of the project is to provide secure user authentication using JWT tokens and efficient file uploads using Amazon S3.

## Main Components

### auth.py

The `auth.py` module is responsible for user authentication and security-related operations.

It provides functionality for:

* Password hashing using bcrypt
* Password verification during login
* JWT access token creation
* JWT token validation and decoding

#### Key Variables

* `SECRET_KEY` – JWT signing secret loaded from environment variables or a fallback default value.
* `ALGORITHM` – HMAC signing algorithm (`HS256`).
* `ACCESS_TOKEN_EXPIRE_MINUTES` – Token expiration period (default: 1 day).

#### Functions

**hash_password(password: str) -> str**

Creates a secure bcrypt hash of the provided password. This function is used when creating user accounts or storing new passwords.

**verify_password(password: str, hashed: str) -> bool**

Verifies whether a plaintext password matches a previously stored bcrypt hash.

**create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str**

Creates and signs a JWT access token. The token payload includes an expiration timestamp (`exp`) stored as a UNIX timestamp for compatibility with JWT consumers.

**decode_access_token(token: str) -> Optional[dict]**

Validates and decodes a JWT token. Returns the token payload if valid; otherwise returns `None`.

---

### s3_utils.py

The `s3_utils.py` module provides helper functions for AWS S3 operations and presigned uploads.

Its purpose is to allow clients to upload files directly to Amazon S3 while reducing backend server load.

#### Functions

**get_s3_client()**

Creates and returns an AWS S3 client using credentials stored in environment variables.

**create_presigned_post(bucket_name, object_name, expires_in=3600, acl="private")**

Generates a presigned POST form that allows browser-based multipart uploads directly to S3.

Returns:

* Upload URL
* Required form fields

This method is useful for larger file uploads.

**create_presigned_put_url(bucket_name, object_name, expires_in=3600)**

Generates a presigned PUT URL that allows direct file uploads to S3 using a single HTTP request.

This method is useful for uploads performed using tools such as Fetch API, cURL, or other HTTP clients.

---

### uploads.html

The frontend upload form is implemented in `uploads.html`.

The form submits files to an internal `/upload/1` endpoint. Depending on the backend implementation, this endpoint may:

* Upload files to S3 on the server side using the AWS S3 client.
* Generate presigned upload credentials and allow direct uploads to S3.

---

## Authentication Flow

The authentication process follows these steps:

1. The client submits login credentials (username/email and password).
2. The backend retrieves the corresponding user record and stored password hash.
3. The submitted password is verified using `verify_password()`.
4. If verification fails, the request is rejected.
5. If verification succeeds, token claims are prepared and passed to `create_access_token()`.
6. A signed JWT token is generated and returned to the client.
7. The client includes the token in future requests using:

```text
Authorization: Bearer <token>
```

8. Protected routes validate incoming tokens using `decode_access_token()`.
9. Invalid or expired tokens are rejected.

---

## File Upload Flow

The project supports two common upload approaches.

### Presigned POST Upload

1. Client requests upload information from the backend.
2. Backend generates a presigned POST using `create_presigned_post()`.
3. Upload information is returned to the client.
4. Client uploads the file directly to Amazon S3.
5. The file is stored in the specified S3 bucket.

### Presigned PUT Upload

1. Client requests a presigned upload URL.
2. Backend generates the URL using `create_presigned_put_url()`.
3. URL is returned to the client.
4. Client uploads the file using an HTTP PUT request.
5. Amazon S3 stores the uploaded file.

---

## Component Interaction

The overall workflow is:

1. User logs into the application.
2. Authentication is handled by `auth.py`.
3. JWT access tokens are generated and used for protected requests.
4. Upload requests are processed through backend upload endpoints.
5. Backend uses `s3_utils.py` to create S3 clients or presigned upload credentials.
6. Files are uploaded and stored in Amazon S3.

---

## Environment Variables

The following environment variables must be configured:

```env
SECRET_KEY=your_secret_key

AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=your_region
```

These values are required for JWT signing and AWS S3 connectivity.

---

## Local Setup

### Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate the Environment

**Windows PowerShell**

```bash
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install passlib[bcrypt] python-jose boto3
```

### Run the Application

Run the project using the appropriate application server depending on the framework being used.

For testing helper functions, run:

```bash
python run_test.py
```

---

## Security Considerations

* Passwords are securely stored using bcrypt hashing.
* JWT tokens are signed using a secret key and include expiration timestamps.
* AWS credentials should never be committed to source control.
* In production environments, use a strong custom `SECRET_KEY`.
* File type and size validation should be performed before uploads.
* Presigned URLs should use short expiration periods.
* AWS IAM permissions should be restricted to the minimum required access.

---

## Error Handling

The project includes handling for common failure scenarios:

* Missing `python-jose` dependency will prevent JWT functionality.
* Missing `boto3` dependency will prevent AWS S3 functionality.
* Missing AWS environment variables will cause S3 client creation failures.
* Invalid or expired JWT tokens return `None` during validation.
* AWS service failures may raise `ClientError` exceptions and should be handled appropriately by the application.

---

## Testing

The `run_test.py` script can be used to verify the core functionality of the project.

The script performs the following actions:

* Hashes a sample password.
* Verifies the generated password hash.
* Creates a JWT token.
* Decodes and validates the JWT token.
* Writes results to an output file for inspection.
