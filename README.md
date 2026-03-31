Project: File Sharing Platform

Project Overview

Purpose: Implements backend helpers for authentication and S3-based file uploads for a file-sharing platform. The front-end contains an upload form that posts files to an upload endpoint.
Main components: auth.py (password hashing, JWT creation/verification), s3_utils.py (S3 client + presigned upload helpers), uploads.html (file upload form).
auth.py — Authentication helper

Responsibility: Hashing and verifying passwords; creating and decoding access tokens (JWT).
Key variables:
SECRET_KEY: JWT signing secret from environment or fallback default.
ALGORITHM: HMAC algorithm used (HS256).
ACCESS_TOKEN_EXPIRE_MINUTES: Token lifetime (1 day by default).
Functions:
hash_password(password: str) -> str: Uses passlib with bcrypt to create a salted hash. Call when creating user accounts or storing new passwords.
verify_password(password: str, hashed: str) -> bool: Verifies plaintext password against stored bcrypt hash. Call at login.
create_access_token(data: dict, expires_delta: Optional[timedelta]) -> str: Copies data, adds exp as UNIX timestamp, signs with SECRET_KEY using python-jose. Returns JWT string.
decode_access_token(token: str) -> Optional[dict]: Verifies and decodes JWT; returns payload or None on verification error.
Notes & behavior:
If python-jose isn't installed, the module raises at runtime; a small stub is present only to silence static checks.
exp is stored as integer UNIX timestamp to be broadly compatible with JWT consumers.
Password handling uses passlib with bcrypt (secure, salted, slow-hash).
Authentication (login) flow — how it works step-by-step

Client sends login credentials (username/email + password) to the backend login endpoint.
Backend looks up user by username/email and retrieves stored password hash.
Backend calls verify_password(submitted_password, stored_hash).
If False: respond with 401/403 (invalid credentials).
If password is correct, backend prepares token claims (e.g., {"sub": user_id, "role": ...}) and calls create_access_token(claims).
Backend returns the JWT to client (commonly in JSON body or a secure cookie).
Client includes token in future requests (Authorization: Bearer <token>).
Backend routes that require authentication validate tokens by calling decode_access_token(token); if None, reject.
s3_utils.py — S3 helpers

Responsibility: Provide AWS S3 client and presigned upload helpers so clients can upload directly to S3.
Behavior:
If boto3 not installed, methods raise with a clear message.
get_s3_client() creates a boto3 session client using environment-provided AWS keys and returns an S3 client.
Functions:
create_presigned_post(bucket_name, object_name, expires_in=3600, acl="private") -> Dict[str, Any]:
Calls s3_client.generate_presigned_post(...).
Returns data for browser-side multipart POST to S3 (URL + form fields).
Use for HTML form direct-to-S3 uploads when you want multipart form uploads (e.g., larger files).
create_presigned_put_url(bucket_name, object_name, expires_in=3600) -> str:
Calls s3_client.generate_presigned_url("put_object", ...).
Returns a presigned URL that a client can PUT to directly with the file body.
Useful for single-request uploads (e.g., PUT with fetch or curl).
Environment variables used:
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION.
Upload flow (end-to-end — common patterns)

Two common server-assisted approaches:
Backend returns a presigned POST form:
Client requests upload info from backend (e.g., POST /files/request-upload).
Backend calls create_presigned_post(bucket, object_key) and returns the result.
Client uses returned URL + fields to POST the file directly to S3 (browser form).
S3 stores the file; backend can be notified via S3 event or client can inform backend of completion.
Backend returns presigned PUT URL:
Client requests a presigned PUT from backend.
Backend calls create_presigned_put_url(bucket, object_key) and returns the URL.
Client does an HTTP PUT to that URL with the file body.
The project’s uploads.html uses a basic form that posts to an internal /upload/1 endpoint — that endpoint likely either:
Receives the file and uploads server-side to S3 (using s3_utils.get_s3_client() and put_object), OR
Uses the server to issue a presigned artifact and the client should instead post directly to S3 (but the HTML currently posts to /upload/1).
How components interact

Frontend form → Backend upload endpoint.
Backend upload endpoint → uses s3_utils to get S3 client or presigned data → S3 stores file.
User auth uses auth.py for login and token creation → token used for protected endpoints such as presigned request creation.
How to run locally (simple steps)

Create venv and install dependencies:
python -m venv .venv
Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install passlib[bcrypt] python-jose boto3
Run the server (project doesn't include full server file here; common frameworks: FastAPI/Flask/Django).
To test helpers only, use the provided run_test.py (if present) or a small script:
The script should import auth and s3_utils and exercise functions.
Files to open: auth.py, s3_utils.py, uploads.html, run_test.py.
Environment variables you must set for full behavior

SECRET_KEY — used to sign JWTs (override default for production).
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION — used by s3_utils to create S3 client.
Optional: other app-specific settings for DB, host/port, etc.
Security considerations (what interviewers expect you to know)

Never use default SECRET_KEY in production — supply a secure random key.
Store AWS credentials in IAM roles (if running on AWS) or a secure secret manager; avoid committing credentials.
JWTs: sign with strong secret and use reasonable expiry; if sensitive operations needed, consider refresh tokens and revocation lists.
Validate file types and sizes server-side even if uploading directly to S3.
For presigned URLs: limit TTL, restrict object key prefixes, and set ACLs appropriately.
Hash passwords with an adaptive algorithm like bcrypt (done here); set cost factor appropriately.
Error handling and failure modes

Missing dependencies (python-jose, boto3) will raise runtime errors; code includes stubs only for static analysis.
S3 client creation will fail if AWS environment variables missing — catch these errors and return meaningful responses.
JWT decode failure returns None; the app must interpret that as unauthorized.
Network and permission errors from AWS are surfaced as ClientError — catch and respond appropriately (log details, do not leak secrets).
Common interview Q&A (short, direct answers you can rehearse)

Q: "How do you store passwords?"
A: "We use passlib with bcrypt to store salted hashes; we never store plaintext."
Q: "How do you authenticate users?"
A: "On login we verify password, then issue an expiring JWT signed with an HMAC secret; subsequent requests send Authorization: Bearer <token>."
Q: "How are file uploads handled?"
A: "We generate presigned URLs or POST forms via AWS S3 using boto3 so clients can upload directly to S3, minimizing server bandwidth and improving scalability. Alternatively server-side uploads are possible by accepting files and using the S3 client to upload them."
Q: "How do you keep uploads secure?"
A: "We verify authenticated user, generate short-lived presigned URLs, validate file type/size, and set appropriate ACLs. AWS IAM restricts actions the app can perform."
Q: "What happens when an AWS call fails?"
A: "We catch botocore.exceptions.ClientError, log details, and surface a user-friendly error. Retries can be added for transient failures."
What I changed to fix your yellow-line warnings

Added explicit types and small runtime stubs for optional external modules (python-jose, boto3) so static analyzers (Pylance) don't show "possibly None" or missing attribute warnings.
Annotated external imports with # type: ignore where appropriate, and added precise function return types.
Practical demo script (what run_test.py does)

Hashes a test password and verifies it.
Creates a JWT for a test subject and attempts to decode it.
Writes results to a final file so you can open it directly in your editor.
Quick checklist to show in interview / demo

Show auth.py: point out hash_password, verify_password, token creation & decoding.
Show s3_utils.py: point out get_s3_client(), create_presigned_post(), create_presigned_put_url().
Show uploads.html: demonstrate how the form posts and explain how it would map to a presigned flow or server upload.
Run run_test.py live (or show its output) to demonstrate helpers work end-to-end.


