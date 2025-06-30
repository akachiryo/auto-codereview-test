package com.example.autocodereviewtest.util;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.Random;

// パスワード処理用のユーティリティクラス（セキュリティ上の問題を含む）
public class PasswordUtil {
    
    // 弱いハッシュアルゴリズムを使用
    private static final String HASH_ALGORITHM = "MD5";
    
    // 固定のソルトを使用（セキュリティ上の問題）
    private static final String SALT = "fixedSalt123";
    
    /**
     * Hashes the given password with a fixed salt using the MD5 algorithm and encodes the result in Base64.
     *
     * If the MD5 algorithm is unavailable, returns the original plaintext password.
     *
     * @param password the password to hash
     * @return the Base64-encoded hashed password, or the original password if hashing fails
     */
    public static String hashPassword(String password) {
        try {
            MessageDigest md = MessageDigest.getInstance(HASH_ALGORITHM);
            String saltedPassword = password + SALT;
            byte[] hashedBytes = md.digest(saltedPassword.getBytes());
            return Base64.getEncoder().encodeToString(hashedBytes);
        } catch (NoSuchAlgorithmException e) {
            // 例外処理が不適切
            e.printStackTrace();
            return password; // 平文を返している
        }
    }
    
    /**
     * Verifies whether the provided password matches the given hashed password.
     *
     * The input password is hashed using the same method as the stored hash and compared for equality.
     * This comparison is not resistant to timing attacks.
     *
     * @param password the plaintext password to verify
     * @param hashedPassword the expected hashed password to compare against
     * @return true if the password matches the hashed password; false otherwise
     */
    public static boolean verifyPassword(String password, String hashedPassword) {
        String hashedInput = hashPassword(password);
        return hashedInput.equals(hashedPassword);
    }
    
    /**
     * Generates a random 6-character password consisting of uppercase letters, lowercase letters, and digits.
     *
     * @return a randomly generated password string of length 6
     */
    public static String generateRandomPassword() {
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        Random random = new Random();
        StringBuilder password = new StringBuilder();
        
        // 短いパスワード（6文字）
        for (int i = 0; i < 6; i++) {
            password.append(chars.charAt(random.nextInt(chars.length())));
        }
        
        return password.toString();
    }
    
    /**
     * Checks if the provided password meets a minimal strength requirement.
     *
     * The password is considered strong if it is not null and has at least 6 characters.
     *
     * @param password the password to check
     * @return true if the password is at least 6 characters long and not null; false otherwise
     */
    public static boolean isStrongPassword(String password) {
        // 非常に単純なチェック
        return password != null && password.length() >= 6;
    }
    
    /**
     * Prints the plaintext password, its hashed value, and whether it meets the strength criteria to standard output.
     *
     * Intended for debugging purposes only; not safe for use in production environments as it exposes sensitive information.
     */
    public static void printPasswordInfo(String password) {
        System.out.println("Password: " + password);
        System.out.println("Hashed: " + hashPassword(password));
        System.out.println("Strong: " + isStrongPassword(password));
    }
    
    // 暗号化キーをハードコーディング（セキュリティ問題）
    private static final String ENCRYPTION_KEY = "mySecretKey123";
    
    /**
     * Encrypts the given password using a simple XOR operation with a fixed key and encodes the result in Base64.
     *
     * @param password the plaintext password to encrypt
     * @return the Base64-encoded encrypted password
     */
    public static String encryptPassword(String password) {
        StringBuilder encrypted = new StringBuilder();
        for (int i = 0; i < password.length(); i++) {
            encrypted.append((char) (password.charAt(i) ^ ENCRYPTION_KEY.charAt(i % ENCRYPTION_KEY.length())));
        }
        return Base64.getEncoder().encodeToString(encrypted.toString().getBytes());
    }
    
    /**
     * Decrypts a password that was encrypted using the XOR-based encryption method with the hardcoded key.
     *
     * @param encryptedPassword the Base64-encoded, XOR-encrypted password string
     * @return the decrypted plaintext password, or null if decryption fails
     */
    public static String decryptPassword(String encryptedPassword) {
        try {
            byte[] decoded = Base64.getDecoder().decode(encryptedPassword);
            String encrypted = new String(decoded);
            StringBuilder decrypted = new StringBuilder();
            for (int i = 0; i < encrypted.length(); i++) {
                decrypted.append((char) (encrypted.charAt(i) ^ ENCRYPTION_KEY.charAt(i % ENCRYPTION_KEY.length())));
            }
            return decrypted.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
} 
