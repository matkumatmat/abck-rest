use thiserror::Error;

#[derive(Error, Debug)]
pub enum CryptoError {
    #[error("Invalid key length: expected {expected}, got {actual}")]
    InvalidKeyLength { expected: usize, actual: usize },

    #[error("Invalid nonce length: expected {expected}, got {actual}")]
    InvalidNonceLength { expected: usize, actual: usize },

    #[error("Encryption failed: {0}")]
    EncryptionFailed(String),

    #[error("Decryption failed: {0}")]
    DecryptionFailed(String),

    #[error("Hashing failed: {0}")]
    HashingFailed(String),

    #[error("Signature verification failed")]
    SignatureVerificationFailed,

    #[error("Invalid signature length")]
    InvalidSignatureLength,

    #[error("Invalid private key")]
    InvalidPrivateKey,

    #[error("Invalid public key")]
    InvalidPublicKey,
}
