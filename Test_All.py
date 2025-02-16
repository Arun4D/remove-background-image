import webbrowser
import requests
import base64
import json
import tkinter as tk
from tkinter import filedialog, messagebox

# Replace with your actual API Gateway URLs for Lambda
UPLOAD_API_URL = "https://<<replace>>.execute-api.us-west-1.amazonaws.com/prod/neesoft/bgremove/upload"
PROCESS_API_URL = "https://<<replace>>.execute-api.us-west-1.amazonaws.com/prod/neesoft/bgremove/process"
DOWNLOAD_API_URL = "https://<<replace>>.execute-api.us-west-1.amazonaws.com/prod/neesoft/bgremove/download"
API_KEY = "<<replace>>"
file_name = ""  # Global variable to store uploaded file name

def upload_image():
    global file_name
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if not file_path:
        return

    try:
        # Read and encode image in base64
        with open(file_path, "rb") as image_file:
            base64_encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Extract file name
        file_name = file_path.split("/")[-1]

        # Set headers
        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "file-name": file_name
        }

        # Set request payload
        payload = {
            "body": base64_encoded_image,
            "headers": {
                "file-name": file_name
            },
            "isBase64Encoded": True
        }

        # Send request to Lambda
        response = requests.post(UPLOAD_API_URL, headers=headers, data=json.dumps(payload))

        # Show response
        if response.status_code == 200:
            result = response.json()
            response_body = json.loads(result.get("body", "{}"))
            file_name = response_body.get("file_name", "")
            print(result)
            messagebox.showinfo("Success", f"Image uploaded successfully!")
        else:
            messagebox.showerror("Error", f"Failed to upload image.\nResponse: {response.text}")

    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")

def process_image():
    global file_name
    if not file_name:
        messagebox.showerror("Error", "No file uploaded to process!")
        return
    try:
        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "file_name": file_name
        }

        print("Payload:", payload)
        response = requests.post(PROCESS_API_URL, headers=headers, json=payload)
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
        
        if response.status_code == 200:
            result = response.json()
            response_body = result.get("body", {})
            file_name = response_body.get("file_name", "")
            messagebox.showinfo("Success", "Image processed successfully!")
        else:
            messagebox.showerror("Error", f"Failed to process image.\nResponse: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")

def download_image():
    global file_name
    if not file_name:
        messagebox.showerror("Error", "No file available for download!")
        return
    try:
        headers = {
            "x-api-key": API_KEY,
            "Content-Type": "application/json",
        }

        response = requests.get(f"{DOWNLOAD_API_URL}?file_name={file_name}", headers=headers)
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
        if response.status_code == 200:
            response_data = response.json()

            # Extract the file URL from the response
            response_body = json.loads(response_data.get("body", "{}"))  # Handle nested JSON in "body"
            file_url = response_body.get("file_url", "N/A")

            if file_url != "N/A":
                # Show message box with "OK" button that opens the file in browser
                if messagebox.askyesno("Success", f"Download URL: {file_url}\n\nOpen in browser?"):
                    webbrowser.open(file_url)  # Open URL in default browser
            else:
                messagebox.showerror("Error", "File URL not found!")
        else:
            messagebox.showerror("Error", f"Failed to get download URL.\nResponse: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")

# Create UI
root = tk.Tk()
root.title("AWS Lambda Image Processing")

upload_button = tk.Button(root, text="Upload Image", command=upload_image, padx=20, pady=10)
upload_button.pack(pady=10)

process_button = tk.Button(root, text="Process Image", command=process_image, padx=20, pady=10)
process_button.pack(pady=10)

download_button = tk.Button(root, text="Download Image", command=download_image, padx=20, pady=10)
download_button.pack(pady=10)

root.mainloop()
