"""Exercise the hosted startup path against disposable Docker PostgreSQL."""
import json
import re
import subprocess
import time
import uuid
from http.cookies import SimpleCookie
from urllib.request import Request, urlopen


def docker(*arguments):
    return subprocess.check_output(["docker", *arguments], text=True).strip()


def main():
    namespace = "medresearch-smoke-" + uuid.uuid4().hex[:8]
    database, web = namespace + "-db", namespace + "-web"
    docker("network", "create", namespace)
    try:
        docker("run", "-d", "--name", database, "--network", namespace,
               "-e", "POSTGRES_USER=research", "-e", "POSTGRES_PASSWORD=disposable-test-only",
               "-e", "POSTGRES_DB=research", "postgres:16")
        for _ in range(60):
            ready = subprocess.run(["docker", "exec", database, "pg_isready", "-U", "research"], capture_output=True)
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Disposable PostgreSQL did not start")
        docker("run", "-d", "--name", web, "--network", namespace, "-p", "127.0.0.1::8000",
               "-e", f"DATABASE_URL=postgresql://research:disposable-test-only@{database}/research?sslmode=disable",
               "-e", "DJANGO_SECRET_KEY=disposable-container-smoke-secret-with-more-than-fifty-characters",
               "-e", "DJANGO_TRUST_PROXY=1", "-e", "RENDER_EXTERNAL_HOSTNAME=medresearch-smoke.onrender.com",
               "-e", "EMAIL_VERIFICATION_REQUIRED=0", "-e", "PORT=8000",
               "medresearch:ci", "python", "backend/hosted_start.py")
        base = "http://" + docker("port", web, "8000/tcp").splitlines()[0]
        cookies = SimpleCookie()

        def request(path, data=None):
            headers = {"Host": "medresearch-smoke.onrender.com", "X-Forwarded-Proto": "https"}
            if cookies:
                headers["Cookie"] = "; ".join(f"{key}={value.value}" for key, value in cookies.items())
            if data is not None:
                headers.update({"Content-Type": "application/json", "Origin": "https://medresearch-smoke.onrender.com",
                                "X-CSRFToken": cookies["medresearch_csrftoken"].value})
            req = Request(base + path, headers=headers, data=None if data is None else json.dumps(data).encode())
            with urlopen(req, timeout=5) as response:
                for header in response.headers.get_all("Set-Cookie", []):
                    cookies.load(header)
                return response.read()

        def wait_ready():
            for _ in range(60):
                try:
                    if json.loads(request("/api/health/"))["status"] == "ok":
                        return
                except (OSError, ValueError):
                    pass
                time.sleep(1)
            raise RuntimeError("Hosted application did not become healthy")

        wait_ready()
        index = request("/profile")
        assert b'id="root"' in index
        asset = re.search(rb'src="(/assets/[^\"]+\.js)"', index).group(1).decode()
        assert len(request(asset)) > 1000
        request("/api/session/")
        account = json.loads(request("/api/auth/register/", {
            "username": "container-smoke", "password": "researchpass", "password_confirmation": "researchpass",
        }))
        assert account["user"]["username"] == "container-smoke"
        docker("restart", web)
        base = "http://" + docker("port", web, "8000/tcp").splitlines()[0]
        wait_ready()
        assert json.loads(request("/api/session/"))["user"]["id"] == account["user"]["id"]
        print("Hosted Docker smoke passed: migrations, assets, CSRF registration and session persistence after restart.")
    except Exception:
        subprocess.run(["docker", "logs", web], check=False)
        raise
    finally:
        subprocess.run(["docker", "rm", "-f", web, database], check=False, capture_output=True)
        subprocess.run(["docker", "network", "rm", namespace], check=False, capture_output=True)


if __name__ == "__main__":
    main()
