package com.example.autocodereviewtest.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

// DTOクラスだが、一部のベストプラクティスが欠けている
public class UserDto {
    
    private Long id;
    
    @NotBlank(message = "名前は必須です")
    @Size(min = 2, max = 50, message = "名前は2文字以上50文字以下で入力してください")
    private String name;
    
    @Email(message = "有効なメールアドレスを入力してください")
    @NotBlank(message = "メールアドレスは必須です")
    private String email;
    
    // パスワードをDTOに含めている（セキュリティ上の問題）
    @NotBlank(message = "パスワードは必須です")
    @Size(min = 6, message = "パスワードは6文字以上で入力してください")
    private String password;
    
    /**
 * Constructs a new UserDto with default values for all fields.
 */
    public UserDto() {}
    
    /**
     * Constructs a UserDto with the specified id, name, email, and password.
     *
     * @param id       the unique identifier of the user
     * @param name     the user's name
     * @param email    the user's email address
     * @param password the user's password
     */
    public UserDto(Long id, String name, String email, String password) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.password = password;
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
     * Sets the user identifier.
     *
     * @param id the unique identifier for the user
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
     * Returns the user's email address.
     *
     * @return the email address of the user
     */
    public String getEmail() {
        return email;
    }
    
    /**
     * Sets the user's email address.
     *
     * @param email the email address to assign to the user
     */
    public void setEmail(String email) {
        this.email = email;
    }
    
    /**
     * Retrieves the user's password.
     *
     * @return the password associated with the user
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
     * Returns a string representation of the UserDto, including all fields.
     *
     * <p><b>Security Note:</b> The returned string includes the password field, which may expose sensitive information if logged or displayed.</p>
     *
     * @return a string containing the values of id, name, email, and password
     */
    @Override
    public String toString() {
        return "UserDto{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", email='" + email + '\'' +
                ", password='" + password + '\'' +
                '}';
    }
    
    // equals()とhashCode()が実装されていない
} 
