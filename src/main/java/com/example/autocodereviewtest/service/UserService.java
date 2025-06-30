package com.example.autocodereviewtest.service;

import com.example.autocodereviewtest.model.User;
import com.example.autocodereviewtest.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class UserService {
    
    // フィールドインジェクションを使用（推奨されない）
    @Autowired
    private UserRepository userRepository;
    
    // 例外処理が不十分
    public User createUser(String name, String email, String password) {
        // メール重複チェックなし
        User user = new User(name, email, password);
        return userRepository.save(user);
    }
    
    // 例外処理が不適切
    public User getUserById(Long id) {
        Optional<User> user = userRepository.findById(id);
        if (user.isPresent()) {
            return user.get();
        } else {
            // 適切な例外を投げていない
            return null;
        }
    }
    
    // パフォーマンス問題：N+1問題の可能性
    public List<User> getAllUsers() {
        List<User> users = userRepository.findAll();
        // 不要な処理を各ユーザーに対して実行
        for (User user : users) {
            // 何らかの重い処理を想定
            processUser(user);
        }
        return users;
    }
    
    // メソッド名が不適切
    public User updateUser(Long id, String name, String email) {
        User user = getUserById(id);
        if (user != null) {
            user.setName(name);
            user.setEmail(email);
            user.setUpdatedAt(LocalDateTime.now());
            return userRepository.save(user);
        }
        return null;
    }
    
    // 削除処理で例外処理が不十分
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
    
    // パスワード検証なし
    public User authenticateUser(String email, String password) {
        Optional<User> user = userRepository.findByEmail(email);
        if (user.isPresent() && user.get().getPassword().equals(password)) {
            return user.get();
        }
        return null;
    }
    
    // 検索機能（大文字小文字を考慮していない）
    public List<User> searchUsers(String name) {
        return userRepository.findByNameContaining(name);
    }
    
    // プライベートメソッド（重い処理を想定）
    private void processUser(User user) {
        // 何らかの重い処理
        try {
            Thread.sleep(10); // 実際の処理をシミュレート
        } catch (InterruptedException e) {
            // 例外処理が不適切
            e.printStackTrace();
        }
    }
    
    // パスワード変更（セキュリティ問題）
    public User changePassword(Long userId, String newPassword) {
        User user = getUserById(userId);
        if (user != null) {
            // パスワードの強度チェックなし
            // 現在のパスワード確認なし
            user.setPassword(newPassword);
            user.setUpdatedAt(LocalDateTime.now());
            return userRepository.save(user);
        }
        return null;
    }
} 
