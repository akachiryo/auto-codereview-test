package com.example.autocodereviewtest.controller;

import com.example.autocodereviewtest.model.User;
import com.example.autocodereviewtest.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    // フィールドインジェクション（推奨されない）
    @Autowired
    private UserService userService;
    
    // エラーハンドリングが不十分
    @GetMapping
    public List<User> getAllUsers() {
        return userService.getAllUsers();
    }
    
    // パスワードを含むユーザー情報を返している（セキュリティ問題）
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        return userService.getUserById(id);
    }
    
    // バリデーションが不十分
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.createUser(user.getName(), user.getEmail(), user.getPassword());
    }
    
    // 部分更新ができない
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User user) {
        return userService.updateUser(id, user.getName(), user.getEmail());
    }
    
    // エラーハンドリングなし
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
    }
    
    // 認証エンドポイント（セキュリティ問題多数）
    @PostMapping("/login")
    public User login(@RequestParam String email, @RequestParam String password) {
        // パスワードがログに出力される可能性
        System.out.println("Login attempt for: " + email + " with password: " + password);
        return userService.authenticateUser(email, password);
    }
    
    // 検索機能（SQLインジェクションの可能性）
    @GetMapping("/search")
    public List<User> searchUsers(@RequestParam String name) {
        return userService.searchUsers(name);
    }
    
    // パスワード変更エンドポイント（セキュリティ問題）
    @PostMapping("/{id}/change-password")
    public User changePassword(@PathVariable Long id, @RequestParam String newPassword) {
        return userService.changePassword(id, newPassword);
    }
    
    // 管理者用エンドポイント（認可チェックなし）
    @GetMapping("/admin/all")
    public List<User> getAllUsersForAdmin() {
        return userService.getAllUsers();
    }
    
    // CORS設定なし、HTTPメソッドの使い方が不適切
    @RequestMapping(value = "/bulk-delete", method = {RequestMethod.GET, RequestMethod.POST})
    public String bulkDelete(@RequestParam List<Long> ids) {
        for (Long id : ids) {
            userService.deleteUser(id);
        }
        return "Deleted " + ids.size() + " users";
    }
    
    // エラー情報を詳細に返しすぎる
    @GetMapping("/debug/{id}")
    public ResponseEntity<?> debugUser(@PathVariable Long id) {
        try {
            User user = userService.getUserById(id);
            if (user == null) {
                return ResponseEntity.notFound().build();
            }
            return ResponseEntity.ok(user);
        } catch (Exception e) {
            // スタックトレース全体を返している
            return ResponseEntity.badRequest().body("Error: " + e.getMessage() + "\nStack trace: " + e.getStackTrace());
        }
    }
} 
