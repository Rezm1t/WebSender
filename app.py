"""
Flask Backend for PS4/PS5 Payload Sender
Sends binary payloads to PlayStation consoles via socket

Socket Communication Mechanism:
This application creates TCP socket connections and transmits binary payload data
directly to PlayStation consoles, similar to how NetCat operates.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import socket
import os
from werkzeug.utils import secure_filename

# Flask app initialization
app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)
CORS(app)

# Configuration
ALLOWED_EXTENSIONS = {'js', 'elf', 'bin', 'zip'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_payload_via_socket(ip_address, port, file_path):
    """
    ====== CORE SOCKET SENDING FUNCTION ======
    This is the central function that implements NetCat-like payload transmission.
    
    SOCKET COMMUNICATION PROCESS:
    1. Create TCP socket (AF_INET = IPv4, SOCK_STREAM = TCP)
    2. Connect to target device (PS4/PS5) at IP:PORT
    3. Read binary payload file into memory
    4. Send ALL binary data through the socket using sendall()
    5. Close socket connection
    
    The target device must be listening on the specified port in developer mode.
    
    Args:
        ip_address: Target PlayStation console IP address (IPv4)
        port: Target listening port (typically 9020, 9021, 9080)
        file_path: Full path to binary payload file
        
    Returns:
        dict: Status information {'status': 'success'/'error', 'message': str, 'bytes_sent': int}
    """
    try:
        # Validate port number
        port = int(port)
        if port < 1 or port > 65535:
            return {'status': 'error', 'message': 'Invalid port number (1-65535)'}
        
        print(f"[*] Starting payload transmission to {ip_address}:{port}")
        
        # ===== BINARY FILE READING =====
        # Read the entire payload file as binary data
        with open(file_path, 'rb') as f:
            payload_data = f.read()
        
        print(f"[*] Loaded payload: {len(payload_data)} bytes")
        
        # ===== SOCKET CREATION =====
        # Create TCP socket for transmission
        # AF_INET = IPv4 protocol
        # SOCK_STREAM = TCP (reliable, ordered byte stream)
        sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sending_socket.settimeout(15)  # 15 second timeout for connection
        
        print(f"[*] Socket created successfully")
        
        # ===== SOCKET CONNECTION =====
        # Connect to the target PlayStation device
        # Device must be listening on this port in Developer Mode
        print(f"[*] Connecting to {ip_address}:{port}...")
        sending_socket.connect((ip_address, port))
        
        print(f"[+] Connected! Transmitting payload...")
        
        # ===== PAYLOAD TRANSMISSION =====
        # Send the entire binary payload through the socket
        # sendall() ensures all data is transmitted before returning
        # This is the critical operation - bytes are sent to the device
        bytes_sent = sending_socket.sendall(payload_data)
        
        # Close socket connection - clean shutdown
        sending_socket.close()
        
        print(f"[+] Transmission complete! Bytes sent: {len(payload_data)}")
        
        return {
            'status': 'success',
            'message': f'Payload sent successfully! ({len(payload_data)} bytes transmitted)',
            'bytes_sent': len(payload_data)
        }
        
    except socket.timeout:
        print(f"[-] Connection timeout - device not responding on {ip_address}:{port}")
        return {'status': 'error', 'message': 'Connection timeout - device not responding'}
    except socket.gaierror:
        print(f"[-] Invalid IP address: {ip_address}")
        return {'status': 'error', 'message': 'Invalid IP address'}
    except ConnectionRefusedError:
        print(f"[-] Connection refused - check if device is listening on port {port}")
        return {'status': 'error', 'message': 'Connection refused - check IP/port and device status'}
    except socket.error as e:
        print(f"[-] Socket error: {str(e)}")
        return {'status': 'error', 'message': f'Connection error: {str(e)}'}
    except Exception as e:
        print(f"[-] Unexpected error: {str(e)}")
        return {'status': 'error', 'message': f'Error: {str(e)}'}


@app.route('/')
def index():
    """Serve the main HTML page from templates folder"""
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS) from static folder"""
    return send_from_directory(app.static_folder, filename)


@app.route('/send-payload', methods=['POST'])
def send_payload():
    """
    API endpoint: /send-payload (POST)
    
    ENDPOINT FLOW:
    1. Receive FormData with ip_address, port, and file upload
    2. Validate input parameters
    3. Check file type and size
    4. Save uploaded file to /uploads folder
    5. Call send_payload_via_socket() to transmit through socket
    6. Return JSON response with status
    7. Clean up by deleting temporary file
    
    Request:
        - ip_address (string): Target PS4/PS5 IP address
        - port (string): Target listening port
        - payload_file (file): Binary payload file
        
    Response:
        - status: 'success' or 'error'
        - message: Human readable status message
        - bytes_sent: Number of bytes transmitted (on success)
    """
    try:
        # ===== INPUT VALIDATION =====
        ip_address = request.form.get('ip_address', '').strip()
        port = request.form.get('port', '').strip()
        
        # Check required fields
        if not ip_address or not port:
            return jsonify({'status': 'error', 'message': 'IP address and port are required'}), 400
        
        # Check file in request
        if 'payload_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        file = request.files['payload_file']
        
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        # ===== FILE VALIDATION =====
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error', 
                'message': 'Invalid file type. Allowed: .js, .elf, .bin, .zip'
            }), 400
        
        print(f"[*] Received file: {file.filename}")
        
        # ===== SAVE UPLOADED FILE =====
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"[*] File saved to: {filepath}")
        
        # ===== SEND PAYLOAD VIA SOCKET =====
        # This is where the binary transmission happens
        result = send_payload_via_socket(ip_address, port, filepath)
        
        # ===== CLEANUP =====
        try:
            os.remove(filepath)
            print(f"[*] Temporary file cleaned up")
        except:
            pass
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
        
    except Exception as e:
        print(f"[-] Server error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - verify server is running"""
    return jsonify({'status': 'ok', 'message': 'Payload sender is running'}), 200


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║        PS4/PS5 Payload Sender - Flask Server Started          ║
    ╚════════════════════════════════════════════════════════════════╝
    
    [+] Server is running on: http://localhost:5000
    [+] Open this URL in your browser to access the web interface
    
    [!] Features:
        • Web-based payload sending interface
        • Socket communication with PlayStation devices
        • File upload support (.elf, .bin, .js, .zip)
        • Real-time status feedback
    
    [!] Endpoints:
        • GET  /           → Main web interface
        • POST /send-payload → Send payload (requires IP, port, file)
        • GET  /health     → Health check
    
    [!] To stop the server, press Ctrl+C
    """)
    
    # Run Flask development server
    # For production, use: gunicorn -w 4 -b 0.0.0.0:5000 app.py
    app.run(debug=True, host='0.0.0.0', port=5000)
