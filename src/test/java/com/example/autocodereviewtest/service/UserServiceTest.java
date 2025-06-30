package com.example.autocodereviewtest.service;

import com.example.autocodereviewtest.model.User;
import com.example.autocodereviewtest.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.Optional;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

// テストクラス（不完全なテスト）
public class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @InjectMocks
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }
    
    // 基本的なテストケースのみ
    @Test
    void testCreateUser() {
        // Arrange
        String name = "テストユーザー";
        String email = "test@example.com";
        String password = "password123";
        User savedUser = new User(name, email, password);
        savedUser.setId(1L);
        
        when(userRepository.save(any(User.class))).thenReturn(savedUser);
        
        // Act
        User result = userService.createUser(name, email, password);
        
        // Assert
        assertNotNull(result);
        assertEquals(name, result.getName());
        assertEquals(email, result.getEmail());
        // パスワードをそのまま比較（セキュリティテストが不十分）
        assertEquals(password, result.getPassword());
    }
    
    // エッジケースのテストが不足
    @Test
    void testGetUserById() {
        // Arrange
        Long userId = 1L;
        User user = new User("テストユーザー", "test@example.com", "password");
        user.setId(userId);
        
        when(userRepository.findById(userId)).thenReturn(Optional.of(user));
        
        // Act
        User result = userService.getUserById(userId);
        
        // Assert
        assertNotNull(result);
        assertEquals(userId, result.getId());
    }
    
    // 例外ケースのテストがない
    @Test
    void testGetAllUsers() {
        // Arrange
        List<User> users = Arrays.asList(
            new User("ユーザー1", "user1@example.com", "pass1"),
            new User("ユーザー2", "user2@example.com", "pass2")
        );
        
        when(userRepository.findAll()).thenReturn(users);
        
        // Act
        List<User> result = userService.getAllUsers();
        
        // Assert
        assertEquals(2, result.size());
        // パフォーマンステストが不足
    }
    
    // 認証テスト（セキュリティテストが不十分）
    @Test
    void testAuthenticateUser() {
        // Arrange
        String email = "test@example.com";
        String password = "password123";
        User user = new User("テストユーザー", email, password);
        
        when(userRepository.findByEmail(email)).thenReturn(Optional.of(user));
        
        // Act
        User result = userService.authenticateUser(email, password);
        
        // Assert
        assertNotNull(result);
        assertEquals(email, result.getEmail());
        // パスワードハッシュ化のテストがない
    }
    
    // 削除テスト（例外処理のテストなし）
    @Test
    void testDeleteUser() {
        // Arrange
        Long userId = 1L;
        
        // Act
        userService.deleteUser(userId);
        
        // Assert
        verify(userRepository, times(1)).deleteById(userId);
        // 削除できない場合のテストがない
    }
    
    // バリデーションテストが不足
    // パフォーマンステストがない
    // 統合テストがない
    // セキュリティテストが不十分
} 
