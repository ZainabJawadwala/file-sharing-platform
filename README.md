### File Sharing Platform ###

## Project Overview

The **File Sharing Platform** is a simple backend project that allows users to log in securely and upload files to **Amazon S3**. It uses **JWT (JSON Web Token)** for user authentication and AWS S3 for cloud file storage. The project consists of three main files: `auth.py`, `s3_utils.py`, and `uploads.html`, each responsible for authentication, file uploads, and the user interface.

## Authentication

The `auth.py` file handles user authentication by securely hashing passwords using **bcrypt** and verifying them during login. After successful authentication, it generates a JWT access token that users include in future requests to access protected resources. The token is signed using a `SECRET_KEY`, the `HS256` algorithm, and has a default expiration time of one day.

## AWS S3 File Upload

The `s3_utils.py` file manages file uploads to Amazon S3. It creates an S3 client using AWS credentials stored in environment variables and supports both **Presigned POST** and **Presigned PUT URL** uploads. These methods allow users to upload files directly to S3, reducing server load and improving performance.

## Frontend

The project includes a simple `uploads.html` page that provides a file upload form. The form sends files to the backend upload endpoint, where they are uploaded to Amazon S3 either directly or through presigned upload links.

## Project Workflow

Users first log in with their username or email and password. After successful verification, a JWT token is generated and returned. This token is used for authenticated requests. When a user uploads a file, the backend uses the helper functions in `s3_utils.py` to upload the file securely to Amazon S3.

## Environment Variables

The project requires the following environment variables:

* `SECRET_KEY`
* `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`
* `AWS_REGION`

These values are required for JWT authentication and AWS S3 connectivity.

## Security

Passwords are securely stored using **bcrypt** hashing instead of plain text. JWT tokens are signed using a secret key and include an expiration time for secure authentication. AWS credentials should always be stored in environment variables and never committed to the repository.

