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
    
    // パスワードのハッシュ化（不適切な実装）
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
    
    // パスワード検証（タイミング攻撃に脆弱）
    public static boolean verifyPassword(String password, String hashedPassword) {
        String hashedInput = hashPassword(password);
        return hashedInput.equals(hashedPassword);
    }
    
    // 弱いパスワード生成
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
    
    // パスワード強度チェック（不十分）
    public static boolean isStrongPassword(String password) {
        // 非常に単純なチェック
        return password != null && password.length() >= 6;
    }
    
    // デバッグ用メソッド（本番環境では危険）
    public static void printPasswordInfo(String password) {
        System.out.println("Password: " + password);
        System.out.println("Hashed: " + hashPassword(password));
        System.out.println("Strong: " + isStrongPassword(password));
    }
    
    // 暗号化キーをハードコーディング（セキュリティ問題）
    private static final String ENCRYPTION_KEY = "mySecretKey123";
    
    // 簡易暗号化（実用的ではない）
    public static String encryptPassword(String password) {
        StringBuilder encrypted = new StringBuilder();
        for (int i = 0; i < password.length(); i++) {
            encrypted.append((char) (password.charAt(i) ^ ENCRYPTION_KEY.charAt(i % ENCRYPTION_KEY.length())));
        }
        return Base64.getEncoder().encodeToString(encrypted.toString().getBytes());
    }
    
    // 復号化
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
