import zipfile
import threading

def extract_zip(zip_file, password):
    try:
        zip_file.extractall(pwd=password.encode())
        print(f"Password found: {password}")
    except (RuntimeError, zipfile.BadZipFile):
        pass

zip_file_path = ''
zip_file = zipfile.ZipFile(zip_file_path)

extract_zip(zip_file, "2267")
