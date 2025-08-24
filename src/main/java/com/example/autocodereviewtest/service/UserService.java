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
    
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public User createUser(String name, String email, String password) {
        if (userRepository.findByEmail(email).isPresent()) {
            throw new IllegalArgumentException("指定されたメールアドレスは既に使用されています");
        }
        User user = new User(name, email, password);
        return userRepository.save(user);
    }
    
    public User getUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("ユーザーが見つかりません: " + id));
    }
    
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    public User updateUser(Long id, String name, String email) {
        User user = getUserById(id);
        user.setName(name);
        user.setEmail(email);
        user.setUpdatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }
    
    public void deleteUser(Long id) {
        if (!userRepository.existsById(id)) {
            throw new IllegalArgumentException("ユーザーが見つかりません: " + id);
        }
        userRepository.deleteById(id);
    }
    
    public User authenticateUser(String email, String password) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("認証に失敗しました"));
        
        if (!com.example.autocodereviewtest.util.PasswordUtil.verifyPassword(password, user.getPassword())) {
            throw new IllegalArgumentException("認証に失敗しました");
        }
        return user;
    }
    
    public List<User> searchUsers(String name) {
        return userRepository.findByNameContainingIgnoreCase(name);
    }
    
    
    public User changePassword(Long userId, String currentPassword, String newPassword) {
        User user = getUserById(userId);
        
        if (!com.example.autocodereviewtest.util.PasswordUtil.verifyPassword(currentPassword, user.getPassword())) {
            throw new IllegalArgumentException("現在のパスワードが正しくありません");
        }
        
        if (!com.example.autocodereviewtest.util.PasswordUtil.isStrongPassword(newPassword)) {
            throw new IllegalArgumentException("パスワードが弱すぎます。大文字、小文字、数字、特殊文字を含む８文字以上にしてください");
        }
        
        user.setPassword(com.example.autocodereviewtest.util.PasswordUtil.hashPassword(newPassword));
        user.setUpdatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }
} 
