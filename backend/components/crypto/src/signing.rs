use ed25519_dalek::{Signature, Signer, SigningKey, Verifier, VerifyingKey};
use hmac::{Hmac, Mac};
use sha2::Sha256;

use crate::config::{ED25519_PRIVATE_KEY_SIZE, ED25519_PUBLIC_KEY_SIZE, ED25519_SIGNATURE_SIZE};
use crate::error::CryptoError;

type HmacSha256 = Hmac<Sha256>;

pub fn sign_hmac(data: &[u8], key: &[u8]) -> Vec<u8> {
    let mut mac = HmacSha256::new_from_slice(key).expect("HMAC can take key of any size");
    mac.update(data);
    mac.finalize().into_bytes().to_vec()
}

pub fn verify_hmac(data: &[u8], signature: &[u8], key: &[u8]) -> bool {
    let mut mac = HmacSha256::new_from_slice(key).expect("HMAC can take key of any size");
    mac.update(data);
    mac.verify_slice(signature).is_ok()
}

pub fn sign_ed25519(data: &[u8], private_key: &[u8]) -> Result<Vec<u8>, CryptoError> {
    if private_key.len() != ED25519_PRIVATE_KEY_SIZE {
        return Err(CryptoError::InvalidKeyLength {
            expected: ED25519_PRIVATE_KEY_SIZE,
            actual: private_key.len(),
        });
    }

    let key_bytes: [u8; ED25519_PRIVATE_KEY_SIZE] = private_key
        .try_into()
        .map_err(|_| CryptoError::InvalidPrivateKey)?;

    let signing_key = SigningKey::from_bytes(&key_bytes);
    let signature = signing_key.sign(data);

    Ok(signature.to_bytes().to_vec())
}

pub fn verify_ed25519(data: &[u8], signature: &[u8], public_key: &[u8]) -> Result<bool, CryptoError> {
    if public_key.len() != ED25519_PUBLIC_KEY_SIZE {
        return Err(CryptoError::InvalidKeyLength {
            expected: ED25519_PUBLIC_KEY_SIZE,
            actual: public_key.len(),
        });
    }

    if signature.len() != ED25519_SIGNATURE_SIZE {
        return Err(CryptoError::InvalidSignatureLength);
    }

    let key_bytes: [u8; ED25519_PUBLIC_KEY_SIZE] = public_key
        .try_into()
        .map_err(|_| CryptoError::InvalidPublicKey)?;

    let sig_bytes: [u8; ED25519_SIGNATURE_SIZE] = signature
        .try_into()
        .map_err(|_| CryptoError::InvalidSignatureLength)?;

    let verifying_key =
        VerifyingKey::from_bytes(&key_bytes).map_err(|_| CryptoError::InvalidPublicKey)?;

    let sig = Signature::from_bytes(&sig_bytes);

    Ok(verifying_key.verify(data, &sig).is_ok())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hmac_sign_verify() {
        let key = b"secret_key";
        let data = b"hello world";

        let signature = sign_hmac(data, key);
        assert!(verify_hmac(data, &signature, key));
        assert!(!verify_hmac(b"wrong data", &signature, key));
        assert!(!verify_hmac(data, &signature, b"wrong_key"));
    }

    #[test]
    fn test_ed25519_sign_verify() {
        use ed25519_dalek::SigningKey;
        use rand::rngs::OsRng;

        let signing_key = SigningKey::generate(&mut OsRng);
        let verifying_key = signing_key.verifying_key();

        let private_key = signing_key.to_bytes().to_vec();
        let public_key = verifying_key.to_bytes().to_vec();

        let data = b"hello world";
        let signature = sign_ed25519(data, &private_key).unwrap();

        assert!(verify_ed25519(data, &signature, &public_key).unwrap());
        assert!(!verify_ed25519(b"wrong data", &signature, &public_key).unwrap());
    }
}
