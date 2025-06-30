package com.example.autocodereviewtest.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "名前は必須です")
    @Column(nullable = false)
    private String name;
    
    @Email(message = "有効なメールアドレスを入力してください")
    @Column(nullable = false, unique = true)
    private String email;
    
    // パスワードをプレーンテキストで保存（セキュリティ上の問題あり）
    @Column(nullable = false)
    private String password;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    /**
 * Constructs a new User with default values.
 */
    public User() {}
    
    /**
     * Constructs a new User with the specified name, email, and password, setting creation and update timestamps to the current time.
     *
     * @param name the user's name
     * @param email the user's email address
     * @param password the user's password in plain text
     */
    public User(String name, String email, String password) {
        this.name = name;
        this.email = email;
        this.password = password;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    /**
     * Returns the unique identifier of the user.
     *
     * @return the user's ID
     */
    public Long getId() {
        return id;
    }
    
    /**
     * Sets the unique identifier for the user.
     *
     * @param id the unique identifier to assign
     */
    public void setId(Long id) {
        this.id = id;
    }
    
    /**
     * Returns the user's name.
     *
     * @return the name of the user
     */
    public String getName() {
        return name;
    }
    
    /**
     * Sets the user's name.
     *
     * @param name the name to assign to the user
     */
    public void setName(String name) {
        this.name = name;
    }
    
    /**
     * Returns the email address of the user.
     *
     * @return the user's email address
     */
    public String getEmail() {
        return email;
    }
    
    /**
     * Sets the email address for the user.
     *
     * @param email the email address to assign to the user
     */
    public void setEmail(String email) {
        this.email = email;
    }
    
    /**
     * Returns the user's password.
     *
     * @return the password in plain text
     */
    public String getPassword() {
        return password;
    }
    
    /**
     * Sets the user's password.
     *
     * @param password the password to assign to the user
     */
    public void setPassword(String password) {
        this.password = password;
    }
    
    /**
     * Returns the timestamp when the user was created.
     *
     * @return the creation time of the user
     */
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    /**
     * Sets the creation timestamp for the user.
     *
     * @param createdAt the date and time when the user was created
     */
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    /**
     * Returns the timestamp of the last update to the user.
     *
     * @return the date and time when the user was last updated
     */
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    /**
     * Sets the timestamp indicating when the user was last updated.
     *
     * @param updatedAt the new update timestamp
     */
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    /**
     * Returns a string representation of the User object, including all fields such as id, name, email, password, createdAt, and updatedAt.
     *
     * <p><b>Note:</b> The returned string includes the password in plain text, which may pose a security risk if logged or exposed.</p>
     *
     * @return a string representation of the User object with all field values
     */
    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", email='" + email + '\'' +
                ", password='" + password + '\'' +
                ", createdAt=" + createdAt +
                ", updatedAt=" + updatedAt +
                '}';
    }
} 
