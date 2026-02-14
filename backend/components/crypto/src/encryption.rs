use aes_gcm::{
    aead::{Aead, KeyInit, Payload},
    Aes256Gcm, Nonce as AesNonce,
};
use chacha20poly1305::{ChaCha20Poly1305, Nonce as ChachaNonce};
use rand::RngCore;

use crate::config::{AES_KEY_SIZE, AES_NONCE_SIZE, CHACHA_KEY_SIZE, CHACHA_NONCE_SIZE};
use crate::error::CryptoError;

pub fn encrypt_aes_gcm(
    plaintext: &[u8],
    key: &[u8],
    aad: Option<&[u8]>,
) -> Result<(Vec<u8>, Vec<u8>), CryptoError> {
    if key.len() != AES_KEY_SIZE {
        return Err(CryptoError::InvalidKeyLength {
            expected: AES_KEY_SIZE,
            actual: key.len(),
        });
    }

    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| CryptoError::EncryptionFailed(e.to_string()))?;

    let mut nonce_bytes = [0u8; AES_NONCE_SIZE];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = AesNonce::from_slice(&nonce_bytes);

    let ciphertext = match aad {
        Some(aad_data) => {
            let payload = Payload {
                msg: plaintext,
                aad: aad_data,
            };
            cipher
                .encrypt(nonce, payload)
                .map_err(|e| CryptoError::EncryptionFailed(e.to_string()))?
        }
        None => cipher
            .encrypt(nonce, plaintext)
            .map_err(|e| CryptoError::EncryptionFailed(e.to_string()))?,
    };

    Ok((ciphertext, nonce_bytes.to_vec()))
}

pub fn decrypt_aes_gcm(
    ciphertext: &[u8],
    key: &[u8],
    nonce: &[u8],
    aad: Option<&[u8]>,
) -> Result<Vec<u8>, CryptoError> {
    if key.len() != AES_KEY_SIZE {
        return Err(CryptoError::InvalidKeyLength {
            expected: AES_KEY_SIZE,
            actual: key.len(),
        });
    }

    if nonce.len() != AES_NONCE_SIZE {
        return Err(CryptoError::InvalidNonceLength {
            expected: AES_NONCE_SIZE,
            actual: nonce.len(),
        });
    }

    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|e| CryptoError::DecryptionFailed(e.to_string()))?;

    let nonce = AesNonce::from_slice(nonce);

    let plaintext = match aad {
        Some(aad_data) => {
            let payload = Payload {
                msg: ciphertext,
                aad: aad_data,
            };
            cipher
                .decrypt(nonce, payload)
                .map_err(|_| CryptoError::DecryptionFailed("Authentication failed".to_string()))?
        }
        None => cipher
            .decrypt(nonce, ciphertext)
            .map_err(|_| CryptoError::DecryptionFailed("Authentication failed".to_string()))?,
    };

    Ok(plaintext)
}

pub fn encrypt_chacha(
    plaintext: &[u8],
    key: &[u8],
    aad: Option<&[u8]>,
) -> Result<(Vec<u8>, Vec<u8>), CryptoError> {
    if key.len() != CHACHA_KEY_SIZE {
        return Err(CryptoError::InvalidKeyLength {
            expected: CHACHA_KEY_SIZE,
            actual: key.len(),
        });
    }

    let cipher = ChaCha20Poly1305::new_from_slice(key)
        .map_err(|e| CryptoError::EncryptionFailed(e.to_string()))?;

    let mut nonce_bytes = [0u8; CHACHA_NONCE_SIZE];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = ChachaNonce::from_slice(&nonce_bytes);

    let ciphertext = match aad {
        Some(aad_data) => {
            let payload = Payload {
                msg: plaintext,
                aad: aad_data,
            };
            cipher
                .encrypt(nonce, payload)
                .map_err(|e| CryptoError::EncryptionFailed(e.to_string()))?
        }
        None => cipher
            .encrypt(nonce, plaintext)
            .map_err(|e| CryptoError::EncryptionFailed(e.to_string()))?,
    };

    Ok((ciphertext, nonce_bytes.to_vec()))
}

pub fn decrypt_chacha(
    ciphertext: &[u8],
    key: &[u8],
    nonce: &[u8],
    aad: Option<&[u8]>,
) -> Result<Vec<u8>, CryptoError> {
    if key.len() != CHACHA_KEY_SIZE {
        return Err(CryptoError::InvalidKeyLength {
            expected: CHACHA_KEY_SIZE,
            actual: key.len(),
        });
    }

    if nonce.len() != CHACHA_NONCE_SIZE {
        return Err(CryptoError::InvalidNonceLength {
            expected: CHACHA_NONCE_SIZE,
            actual: nonce.len(),
        });
    }

    let cipher = ChaCha20Poly1305::new_from_slice(key)
        .map_err(|e| CryptoError::DecryptionFailed(e.to_string()))?;

    let nonce = ChachaNonce::from_slice(nonce);

    let plaintext = match aad {
        Some(aad_data) => {
            let payload = Payload {
                msg: ciphertext,
                aad: aad_data,
            };
            cipher
                .decrypt(nonce, payload)
                .map_err(|_| CryptoError::DecryptionFailed("Authentication failed".to_string()))?
        }
        None => cipher
            .decrypt(nonce, ciphertext)
            .map_err(|_| CryptoError::DecryptionFailed("Authentication failed".to_string()))?,
    };

    Ok(plaintext)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_aes_gcm_encrypt_decrypt() {
        let key = [0u8; 32];
        let plaintext = b"hello world";

        let (ciphertext, nonce) = encrypt_aes_gcm(plaintext, &key, None).unwrap();
        let decrypted = decrypt_aes_gcm(&ciphertext, &key, &nonce, None).unwrap();

        assert_eq!(plaintext.to_vec(), decrypted);
    }

    #[test]
    fn test_aes_gcm_with_aad() {
        let key = [0u8; 32];
        let plaintext = b"hello world";
        let aad = b"user:123";

        let (ciphertext, nonce) = encrypt_aes_gcm(plaintext, &key, Some(aad)).unwrap();
        let decrypted = decrypt_aes_gcm(&ciphertext, &key, &nonce, Some(aad)).unwrap();

        assert_eq!(plaintext.to_vec(), decrypted);

        // Wrong AAD should fail
        let wrong_aad = b"user:456";
        let result = decrypt_aes_gcm(&ciphertext, &key, &nonce, Some(wrong_aad));
        assert!(result.is_err());
    }

    #[test]
    fn test_chacha_encrypt_decrypt() {
        let key = [0u8; 32];
        let plaintext = b"hello world";

        let (ciphertext, nonce) = encrypt_chacha(plaintext, &key, None).unwrap();
        let decrypted = decrypt_chacha(&ciphertext, &key, &nonce, None).unwrap();

        assert_eq!(plaintext.to_vec(), decrypted);
    }

    #[test]
    fn test_chacha_with_aad() {
        let key = [0u8; 32];
        let plaintext = b"hello world";
        let aad = b"context:binding";

        let (ciphertext, nonce) = encrypt_chacha(plaintext, &key, Some(aad)).unwrap();
        let decrypted = decrypt_chacha(&ciphertext, &key, &nonce, Some(aad)).unwrap();

        assert_eq!(plaintext.to_vec(), decrypted);
    }
}
