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
    
    /**
     * Retrieves a list of all users.
     *
     * @return a list containing all user entities
     */
    @GetMapping
    public List<User> getAllUsers() {
        return userService.getAllUsers();
    }
    
    /**
     * Retrieves user information by ID, including sensitive fields such as the password.
     *
     * @param id the unique identifier of the user to retrieve
     * @return the user corresponding to the specified ID, including password information
     */
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        return userService.getUserById(id);
    }
    
    /**
     * Creates a new user with the provided name, email, and password.
     *
     * @param user the user details from the request body
     * @return the created user
     */
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.createUser(user.getName(), user.getEmail(), user.getPassword());
    }
    
    /**
     * Updates the name and email of a user identified by the given ID.
     *
     * @param id the ID of the user to update
     * @param user the user object containing the new name and email
     * @return the updated user
     */
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User user) {
        return userService.updateUser(id, user.getName(), user.getEmail());
    }
    
    /**
     * Deletes a user by their unique identifier.
     *
     * @param id the ID of the user to delete
     */
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
    }
    
    /**
     * Authenticates a user using the provided email and password.
     *
     * @param email the user's email address
     * @param password the user's password
     * @return the authenticated User object if credentials are valid; otherwise, returns null or an unauthenticated user
     */
    @PostMapping("/login")
    public User login(@RequestParam String email, @RequestParam String password) {
        // パスワードがログに出力される可能性
        System.out.println("Login attempt for: " + email + " with password: " + password);
        return userService.authenticateUser(email, password);
    }
    
    /**
     * Searches for users whose names match the specified value.
     *
     * @param name the name to search for
     * @return a list of users matching the given name
     */
    @GetMapping("/search")
    public List<User> searchUsers(@RequestParam String name) {
        return userService.searchUsers(name);
    }
    
    /**
     * Changes the password for the user with the specified ID.
     *
     * @param id the ID of the user whose password will be changed
     * @param newPassword the new password to set for the user
     * @return the updated User object after the password change
     */
    @PostMapping("/{id}/change-password")
    public User changePassword(@PathVariable Long id, @RequestParam String newPassword) {
        return userService.changePassword(id, newPassword);
    }
    
    /**
     * Retrieves a list of all users for administrative purposes.
     *
     * @return a list of all users
     */
    @GetMapping("/admin/all")
    public List<User> getAllUsersForAdmin() {
        return userService.getAllUsers();
    }
    
    /**
     * Deletes multiple users by their IDs and returns a summary message.
     *
     * @param ids the list of user IDs to delete
     * @return a message indicating how many users were deleted
     */
    @RequestMapping(value = "/bulk-delete", method = {RequestMethod.GET, RequestMethod.POST})
    public String bulkDelete(@RequestParam List<Long> ids) {
        for (Long id : ids) {
            userService.deleteUser(id);
        }
        return "Deleted " + ids.size() + " users";
    }
    
    /**
     * Retrieves user details by ID for debugging purposes, returning detailed error information including stack traces if an exception occurs.
     *
     * @param id the ID of the user to retrieve
     * @return a ResponseEntity containing the user details if found, a 404 response if not found, or detailed error information on failure
     */
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
