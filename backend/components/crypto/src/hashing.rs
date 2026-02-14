use argon2::{
    password_hash::{rand_core::OsRng, PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Algorithm, Argon2, Params, Version,
};
use blake3::Hasher as Blake3Hasher;
use sha3::{Digest, Sha3_256};

use crate::config::{ARGON2_OUTPUT_SIZE, ARGON2_SALT_SIZE};
use crate::error::CryptoError;

pub fn hash_argon2(
    password: &str,
    memory_cost: u32,
    time_cost: u32,
    parallelism: u32,
    salt: Option<Vec<u8>>,
) -> Result<String, CryptoError> {
    let params = Params::new(memory_cost, time_cost, parallelism, Some(ARGON2_OUTPUT_SIZE))
        .map_err(|e| CryptoError::HashingFailed(e.to_string()))?;

    let argon2 = Argon2::new(Algorithm::Argon2id, Version::V0x13, params);

    let salt_string = match salt {
        Some(s) => {
            if s.len() < ARGON2_SALT_SIZE {
                return Err(CryptoError::HashingFailed(format!(
                    "Salt too short: expected at least {} bytes",
                    ARGON2_SALT_SIZE
                )));
            }
            SaltString::encode_b64(&s[..ARGON2_SALT_SIZE])
                .map_err(|e| CryptoError::HashingFailed(e.to_string()))?
        }
        None => SaltString::generate(&mut OsRng),
    };

    let hash = argon2
        .hash_password(password.as_bytes(), &salt_string)
        .map_err(|e| CryptoError::HashingFailed(e.to_string()))?;

    Ok(hash.to_string())
}

pub fn verify_argon2(password: &str, hash: &str) -> Result<bool, CryptoError> {
    let parsed_hash =
        PasswordHash::new(hash).map_err(|e| CryptoError::HashingFailed(e.to_string()))?;

    let argon2 = Argon2::default();

    Ok(argon2
        .verify_password(password.as_bytes(), &parsed_hash)
        .is_ok())
}

pub fn hash_blake3(data: &[u8]) -> Vec<u8> {
    let mut hasher = Blake3Hasher::new();
    hasher.update(data);
    hasher.finalize().as_bytes().to_vec()
}

pub fn hash_sha3(data: &[u8]) -> Vec<u8> {
    let mut hasher = Sha3_256::new();
    hasher.update(data);
    hasher.finalize().to_vec()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_argon2_hash_verify() {
        let password = "test_password_123";
        let hash = hash_argon2(password, 65536, 3, 4, None).unwrap();
        assert!(verify_argon2(password, &hash).unwrap());
        assert!(!verify_argon2("wrong_password", &hash).unwrap());
    }

    #[test]
    fn test_blake3() {
        let data = b"hello world";
        let hash1 = hash_blake3(data);
        let hash2 = hash_blake3(data);
        assert_eq!(hash1, hash2);
        assert_eq!(hash1.len(), 32);
    }

    #[test]
    fn test_sha3() {
        let data = b"hello world";
        let hash1 = hash_sha3(data);
        let hash2 = hash_sha3(data);
        assert_eq!(hash1, hash2);
        assert_eq!(hash1.len(), 32);
    }
}
