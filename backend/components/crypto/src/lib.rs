use pyo3::prelude::*;

mod config;
mod encryption;
mod error;
mod hashing;
mod signing;

use encryption::{decrypt_aes_gcm, decrypt_chacha, encrypt_aes_gcm, encrypt_chacha};
use hashing::{hash_argon2, hash_blake3, hash_sha3, verify_argon2};
use signing::{sign_ed25519, sign_hmac, verify_ed25519, verify_hmac};

#[pymodule]
fn k_crypto(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Hashing
    m.add_function(wrap_pyfunction!(hash_password, m)?)?;
    m.add_function(wrap_pyfunction!(verify_password, m)?)?;
    m.add_function(wrap_pyfunction!(hash_data, m)?)?;
    m.add_function(wrap_pyfunction!(hash_data_hex, m)?)?;

    // Encryption
    m.add_function(wrap_pyfunction!(encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(decrypt, m)?)?;

    // Signing
    m.add_function(wrap_pyfunction!(sign, m)?)?;
    m.add_function(wrap_pyfunction!(verify_signature, m)?)?;

    // Key generation
    m.add_function(wrap_pyfunction!(generate_key, m)?)?;
    m.add_function(wrap_pyfunction!(generate_salt, m)?)?;
    m.add_function(wrap_pyfunction!(generate_keypair_ed25519, m)?)?;

    // Version
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    Ok(())
}

// ============================================================================
// HASHING FUNCTIONS
// ============================================================================

#[pyfunction]
#[pyo3(signature = (password, memory_cost=65536, time_cost=3, parallelism=4, salt=None))]
fn hash_password(
    password: &str,
    memory_cost: u32,
    time_cost: u32,
    parallelism: u32,
    salt: Option<Vec<u8>>,
) -> PyResult<String> {
    hash_argon2(password, memory_cost, time_cost, parallelism, salt)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
}

#[pyfunction]
fn verify_password(password: &str, hash: &str) -> PyResult<bool> {
    verify_argon2(password, hash)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
}

#[pyfunction]
#[pyo3(signature = (data, algorithm="blake3"))]
fn hash_data(data: &[u8], algorithm: &str) -> PyResult<Vec<u8>> {
    match algorithm.to_lowercase().as_str() {
        "blake3" => Ok(hash_blake3(data)),
        "sha3" | "sha3_256" => Ok(hash_sha3(data)),
        _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
            "Unknown hash algorithm: {}. Supported: blake3, sha3, sha3_256",
            algorithm
        ))),
    }
}

#[pyfunction]
#[pyo3(signature = (data, algorithm="blake3"))]
fn hash_data_hex(data: &[u8], algorithm: &str) -> PyResult<String> {
    let hash = hash_data(data, algorithm)?;
    Ok(hex::encode(hash))
}

// ============================================================================
// ENCRYPTION FUNCTIONS
// ============================================================================

#[pyfunction]
#[pyo3(signature = (plaintext, key, aad=None, algorithm="aes256gcm"))]
fn encrypt(
    plaintext: &[u8],
    key: &[u8],
    aad: Option<&[u8]>,
    algorithm: &str,
) -> PyResult<(Vec<u8>, Vec<u8>)> {
    match algorithm.to_lowercase().as_str() {
        "aes256gcm" | "aes-256-gcm" => encrypt_aes_gcm(plaintext, key, aad)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())),
        "chacha20poly1305" | "chacha20-poly1305" => encrypt_chacha(plaintext, key, aad)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())),
        _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
            "Unknown encryption algorithm: {}. Supported: aes256gcm, chacha20poly1305",
            algorithm
        ))),
    }
}

#[pyfunction]
#[pyo3(signature = (ciphertext, key, nonce, aad=None, algorithm="aes256gcm"))]
fn decrypt(
    ciphertext: &[u8],
    key: &[u8],
    nonce: &[u8],
    aad: Option<&[u8]>,
    algorithm: &str,
) -> PyResult<Vec<u8>> {
    match algorithm.to_lowercase().as_str() {
        "aes256gcm" | "aes-256-gcm" => decrypt_aes_gcm(ciphertext, key, nonce, aad)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())),
        "chacha20poly1305" | "chacha20-poly1305" => decrypt_chacha(ciphertext, key, nonce, aad)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())),
        _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
            "Unknown decryption algorithm: {}. Supported: aes256gcm, chacha20poly1305",
            algorithm
        ))),
    }
}

// ============================================================================
// SIGNING FUNCTIONS
// ============================================================================

#[pyfunction]
#[pyo3(signature = (data, key, algorithm="hmac_sha256"))]
fn sign(data: &[u8], key: &[u8], algorithm: &str) -> PyResult<Vec<u8>> {
    match algorithm.to_lowercase().as_str() {
        "hmac_sha256" | "hmac-sha256" => Ok(sign_hmac(data, key)),
        "ed25519" => sign_ed25519(data, key)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())),
        _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
            "Unknown signing algorithm: {}. Supported: hmac_sha256, ed25519",
            algorithm
        ))),
    }
}

#[pyfunction]
#[pyo3(signature = (data, signature, key, algorithm="hmac_sha256"))]
fn verify_signature(data: &[u8], signature: &[u8], key: &[u8], algorithm: &str) -> PyResult<bool> {
    match algorithm.to_lowercase().as_str() {
        "hmac_sha256" | "hmac-sha256" => Ok(verify_hmac(data, signature, key)),
        "ed25519" => verify_ed25519(data, signature, key)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string())),
        _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
            "Unknown signing algorithm: {}. Supported: hmac_sha256, ed25519",
            algorithm
        ))),
    }
}

// ============================================================================
// KEY GENERATION
// ============================================================================

#[pyfunction]
#[pyo3(signature = (length=32))]
fn generate_key(length: usize) -> Vec<u8> {
    use rand::RngCore;
    let mut key = vec![0u8; length];
    rand::thread_rng().fill_bytes(&mut key);
    key
}

#[pyfunction]
#[pyo3(signature = (length=16))]
fn generate_salt(length: usize) -> Vec<u8> {
    generate_key(length)
}

#[pyfunction]
fn generate_keypair_ed25519() -> PyResult<(Vec<u8>, Vec<u8>)> {
    use ed25519_dalek::SigningKey;
    use rand::rngs::OsRng;

    let signing_key = SigningKey::generate(&mut OsRng);
    let verifying_key = signing_key.verifying_key();

    Ok((signing_key.to_bytes().to_vec(), verifying_key.to_bytes().to_vec()))
}
