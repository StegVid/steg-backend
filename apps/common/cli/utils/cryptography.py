import os
import numpy as np
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
# Update Qiskit imports
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer  # Changed this import

from apps.common.cli.constants.constants import *
from apps.common.cli.utils.ctxt import *
from apps.common.cli.utils.input import get_path, get_valid_filename

# Toggle Quantum Cryptography (Set to True to Enable)
USE_QUANTUM_CRYPTO = True

# ✅ Generate AES-128 Key (Fernet)
def gen_key(new_filename: str = None) -> str:
    key = Fernet.generate_key()
    path = f"{ENCRYPTION_KEYS_PATH}/{new_filename or 'aes_key.key'}"
    with open(path, 'wb') as f:
        f.write(key)
    print(f"AES Key saved: {path}")
    return path


# ✅ Load AES Key
def load_key(path: str) -> bytes:
    with open(path, 'rb') as f:
        return f.read()


# ✅ Get AES Encryption Object
def get_fernet(from_decryption: bool = None) -> Fernet:
    if from_decryption:
        path = f"{ENCRYPTION_KEYS_PATH}/aes_key.key"
        return Fernet(load_key(path))
    else:
        key_path = gen_key()
        return Fernet(load_key(key_path))


# ✅ Encrypt ZIP with AES-128 (Before Embedding)
def encrypt_data(data: bytes) -> tuple:
    fernet = get_fernet()
    encrypted_data = fernet.encrypt(data)
    return encrypted_data, fernet


# ✅ Decrypt ZIP with AES-128 (After Extraction)
def decrypt_data(encrypted_data: bytes, fernet: Fernet) -> bytes:
    return fernet.decrypt(encrypted_data)


# Function to convert file data into numerical values (bytes)
def file_to_bytes(file_path):
    with open(file_path, 'rb') as f:
        return np.array(list(f.read()))  # Convert file contents into a 1D numpy array of byte values


# Function to flatten a folder's contents into an array of bytes
def folder_to_bytes(folder_path):
    all_bytes = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_data = file_to_bytes(file_path)
            all_bytes.extend(file_data)  # Append file byte data to list
    return np.array(all_bytes)


# ✅ Calculate Correlation Coefficient (Before and After Extraction)
def calculate_correlation(original_folder, extracted_folder):
    # Convert folder contents to numerical data (byte arrays)
    original_bytes = folder_to_bytes(original_folder)
    extracted_bytes = folder_to_bytes(extracted_folder)

    # Ensure the arrays have the same length for correlation calculation
    min_length = min(len(original_bytes), len(extracted_bytes))
    original_bytes = original_bytes[:min_length]
    extracted_bytes = extracted_bytes[:min_length]

    # Calculate Pearson correlation coefficient
    correlation = np.corrcoef(original_bytes, extracted_bytes)[0, 1]
    return correlation


# ✅ Generate Quantum Key
def generate_quantum_key(num_bits=128):
    """
    Generates a quantum key using an 8-qubit circuit and extends it using SHA-256.
    """
    small_key_bits = 8  # Use 8 qubits (feasible for available backends)
    
    qc = QuantumCircuit(small_key_bits, small_key_bits)
    qc.h(range(small_key_bits))  # Apply Hadamard gates
    qc.measure(range(small_key_bits), range(small_key_bits))

    backend = Aer.get_backend("qasm_simulator")
    compiled_circuit = transpile(qc, backend)  # Transpile for the backend

    job = backend.run(compiled_circuit, shots=1)
    result = job.result()
    counts = result.get_counts()
    
    small_key = list(counts.keys())[0]  # Get the 8-bit quantum key
    
    # Extend the key using SHA-256
    extended_key = hashlib.sha256(small_key.encode()).hexdigest()[:num_bits // 4]  # Convert to hex
    return extended_key  # 128-bit equivalent in hex


# ✅ Save Quantum Key to File
def save_quantum_key():
    key = generate_quantum_key()
    path = f"{ENCRYPTION_KEYS_PATH}/quantum_key.key"
    with open(path, 'w') as f:
        f.write(key)
    print(f"Quantum Key saved: {path}")
    return key


# ✅ Load Quantum Key from File
def load_quantum_key():
    return save_quantum_key()
    


# ✅ Encrypt `stego_output.png` Using Quantum Key (Before Extraction)
def encrypt_with_qkd(image_path):
    if not USE_QUANTUM_CRYPTO:
        return image_path  # Skip if Quantum Encryption is Disabled

    key = load_quantum_key().encode()
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()
    encrypted_data = bytes([image_data[i] ^ key[i % len(key)] for i in range(len(image_data))])
    encrypted_path = image_path.replace("stego_output.png", "quantum_encrypted_stego.png")
    with open(encrypted_path, "wb") as enc_file:
        enc_file.write(encrypted_data)
    print(f"Quantum Encrypted Stego Image saved: {encrypted_path}")
    return encrypted_path


# ✅ Decrypt `stego_output.png` Using Quantum Key (Before ZIP Extraction)
def decrypt_with_qkd(encrypted_path):
    """Decrypt stego image using quantum key before ZIP extraction."""
    if not USE_QUANTUM_CRYPTO:
        return encrypted_path  # Skip if Quantum Encryption is Disabled

    path = f"{ENCRYPTION_KEYS_PATH}/quantum_key.key"
    with open(path, 'r') as f:
        key = f.read().encode()
    
    with open(encrypted_path, "rb") as enc_file:
        encrypted_data = enc_file.read()

    decrypted_data = bytes([encrypted_data[i] ^ key[i % len(key)] for i in range(len(encrypted_data))])

    # Debug: Print first 20 bytes of decrypted data
    print("🔍 Decrypted Data (first 20 bytes):", decrypted_data[:20])

    # Validate PNG signature
    if not decrypted_data.startswith(b'\x89PNG\r\n\x1a\n'):
        print("")
        return encrypted_path  # Return encrypted file instead

    decrypted_path = encrypted_path.replace("quantum_encrypted_stego.png", "decrypted_stego_output.png")
    with open(decrypted_path, "wb") as dec_file:
        dec_file.write(decrypted_data)

    print(f"✅ Quantum Decrypted Stego Image saved: {decrypted_path}")
    return decrypted_path
