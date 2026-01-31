import json
import traceback

try:
    from auth import hash_password, verify_password, create_access_token, decode_access_token
except Exception as e:
    print('Failed to import auth module:', e)
    raise


def main():
    out = {}
    try:
        h = hash_password("secret123")
        ok = verify_password("secret123", h)
        token = None
        decoded = None
        try:
            token = create_access_token({"sub": "testuser"})
            decoded = decode_access_token(token)
        except Exception as e:
            token = f"ERROR: {e}"
        out = {"hash": h, "verify": ok, "token": token, "decoded": decoded}
    except Exception as e:
        out = {"error": str(e), "traceback": traceback.format_exc()}

    s = json.dumps(out, ensure_ascii=False, indent=2)
    print(s)
    with open("final", "w", encoding="utf-8") as f:
        f.write("# Test output\n")
        f.write(s)


if __name__ == "__main__":
    main()
