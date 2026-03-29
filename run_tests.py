import subprocess
import time
import json
import os
import sys

def run_tests():
    print("Starting Django server...")
    server_process = subprocess.Popen([sys.executable, 'manage.py', 'runserver', '127.0.0.1:8080'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3) # Wait for server to start
    
    with open('api_test_results.txt', 'w') as f:
        f.write("=== Testing API Endpoints (Laboratory 8 Output) ===\n\n")

        # 1. Register User
        f.write("--- 1. Register User Endpoint ---\n")
        f.write("> http POST http://127.0.0.1:8080/api/register/ username=lab8user password=testpassword123 email=lab8@example.com\n\n")
        
        # We need to run httpie correctly
        # In windows venv, httpie is in venv/Scripts/http (or http.exe)
        http_cmd = os.path.join('venv', 'Scripts', 'http.exe')
        if not os.path.exists(http_cmd):
            # fallback globally
            http_cmd = 'http'
        
        result_reg = subprocess.run([http_cmd, 'POST', 'http://127.0.0.1:8080/api/register/', 'username=lab8user', 'password=testpassword123', 'email=lab8@example.com'], capture_output=True, text=True)
        f.write(result_reg.stdout + "\n" + result_reg.stderr + "\n\n")

        # Extract token
        token = ""
        try:
            res_json = json.loads(result_reg.stdout)
            token = res_json.get('token')
        except:
            pass
        
        # If registration fails because it exists, try login
        if not token:
            f.write("--- 2. Login User Endpoint ---\n")
            f.write("> http POST http://127.0.0.1:8080/api/login/ username=lab8user password=testpassword123\n\n")
            result_login = subprocess.run([http_cmd, 'POST', 'http://127.0.0.1:8080/api/login/', 'username=lab8user', 'password=testpassword123'], capture_output=True, text=True)
            f.write(result_login.stdout + "\n\n")
            try:
                res_json = json.loads(result_login.stdout)
                token = res_json.get('token')
            except:
                pass
        
        # 3. Create Item
        f.write("--- 3. Create Item Endpoint (POST) ---\n")
        auth_header = f"Authorization: Token {token}"
        f.write(f"> http POST http://127.0.0.1:8080/api/items/ type=Lost item_name='Blue Backpack' location='Library 2nd Floor' description='Has a keychain' \"{auth_header}\"\n\n")
        result_create = subprocess.run([http_cmd, 'POST', 'http://127.0.0.1:8080/api/items/', 'type=Lost', 'item_name=Blue Backpack', 'location=Library 2nd Floor', 'description=Has a python sticker', auth_header], capture_output=True, text=True)
        f.write(result_create.stdout + "\n" + result_create.stderr + "\n\n")

        # 4. List Items
        f.write("--- 4. List Items Endpoint (GET) ---\n")
        f.write(f"> http GET http://127.0.0.1:8080/api/items/ \"{auth_header}\"\n\n")
        result_list = subprocess.run([http_cmd, 'GET', 'http://127.0.0.1:8080/api/items/', auth_header], capture_output=True, text=True)
        f.write(result_list.stdout + "\n" + result_list.stderr + "\n\n")

    print("Shutting down Django server...")
    server_process.terminate()

if __name__ == '__main__':
    run_tests()
