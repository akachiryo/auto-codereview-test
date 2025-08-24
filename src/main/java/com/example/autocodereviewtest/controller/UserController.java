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
    
    private final UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        return ResponseEntity.ok(userService.getAllUsers());
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        try {
            return ResponseEntity.ok(userService.getUserById(id));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        try {
            String hashedPassword = com.example.autocodereviewtest.util.PasswordUtil.hashPassword(user.getPassword());
            return ResponseEntity.ok(userService.createUser(user.getName(), user.getEmail(), hashedPassword));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody User user) {
        try {
            return ResponseEntity.ok(userService.updateUser(id, user.getName(), user.getEmail()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        try {
            userService.deleteUser(id);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    @PostMapping("/login")
    public ResponseEntity<User> login(@RequestParam String email, @RequestParam String password) {
        try {
            return ResponseEntity.ok(userService.authenticateUser(email, password));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(401).build();
        }
    }
    
    @GetMapping("/search")
    public ResponseEntity<List<User>> searchUsers(@RequestParam String name) {
        return ResponseEntity.ok(userService.searchUsers(name));
    }
    
    @PostMapping("/{id}/change-password")
    public ResponseEntity<User> changePassword(
            @PathVariable Long id,
            @RequestParam String currentPassword,
            @RequestParam String newPassword) {
        try {
            return ResponseEntity.ok(userService.changePassword(id, currentPassword, newPassword));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    
    @DeleteMapping("/bulk")
    public ResponseEntity<String> bulkDelete(@RequestBody List<Long> ids) {
        int deletedCount = 0;
        for (Long id : ids) {
            try {
                userService.deleteUser(id);
                deletedCount++;
            } catch (IllegalArgumentException e) {
                // スキップ
            }
        }
        return ResponseEntity.ok("Deleted " + deletedCount + " users");
    }
    
} 
