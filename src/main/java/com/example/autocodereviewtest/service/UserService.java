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
    
    /**
     * Creates and saves a new user with the specified name, email, and password.
     *
     * @param name the user's name
     * @param email the user's email address
     * @param password the user's password
     * @return the newly created user
     */
    public User createUser(String name, String email, String password) {
        // メール重複チェックなし
        User user = new User(name, email, password);
        return userRepository.save(user);
    }
    
    /**
     * Retrieves a user by their unique ID.
     *
     * @param id the unique identifier of the user to retrieve
     * @return the user with the specified ID, or {@code null} if no such user exists
     */
    public User getUserById(Long id) {
        Optional<User> user = userRepository.findById(id);
        if (user.isPresent()) {
            return user.get();
        } else {
            // 適切な例外を投げていない
            return null;
        }
    }
    
    /**
     * Retrieves all users and performs additional processing on each user.
     *
     * @return a list of all users after processing
     */
    public List<User> getAllUsers() {
        List<User> users = userRepository.findAll();
        // 不要な処理を各ユーザーに対して実行
        for (User user : users) {
            // 何らかの重い処理を想定
            processUser(user);
        }
        return users;
    }
    
    /**
     * Updates the name and email of an existing user identified by the given ID.
     *
     * @param id    the ID of the user to update
     * @param name  the new name for the user
     * @param email the new email for the user
     * @return the updated User if found, or {@code null} if no user with the given ID exists
     */
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
    
    /**
     * Deletes the user with the specified ID from the repository.
     *
     * If the user does not exist, no action is taken.
     */
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
    
    /**
     * Authenticates a user by matching the provided email and password.
     *
     * Returns the user if the email exists and the password matches exactly; otherwise, returns {@code null}.
     * Passwords are compared in plain text without hashing or secure verification.
     *
     * @param email the user's email address
     * @param password the user's password
     * @return the authenticated user if credentials match; {@code null} otherwise
     */
    public User authenticateUser(String email, String password) {
        Optional<User> user = userRepository.findByEmail(email);
        if (user.isPresent() && user.get().getPassword().equals(password)) {
            return user.get();
        }
        return null;
    }
    
    /**
     * Searches for users whose names contain the specified string, ignoring case sensitivity.
     *
     * @param name the substring to search for within user names
     * @return a list of users whose names contain the given substring
     */
    public List<User> searchUsers(String name) {
        return userRepository.findByNameContaining(name);
    }
    
    /**
     * Simulates a heavy processing task for the given user by introducing a brief delay.
     *
     * This method pauses execution for 10 milliseconds to mimic time-consuming operations.
     * If interrupted, the stack trace of the exception is printed.
     *
     * @param user the user to process
     */
    private void processUser(User user) {
        // 何らかの重い処理
        try {
            Thread.sleep(10); // 実際の処理をシミュレート
        } catch (InterruptedException e) {
            // 例外処理が不適切
            e.printStackTrace();
        }
    }
    
    /**
     * Changes the password of a user identified by the given user ID.
     *
     * Updates the user's password to the specified new value and sets the update timestamp.
     * Does not verify the current password or enforce password strength requirements.
     *
     * @param userId the ID of the user whose password is to be changed
     * @param newPassword the new password to set
     * @return the updated User if found, or {@code null} if the user does not exist
     */
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
