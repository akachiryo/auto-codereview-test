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
    
    // デフォルトコンストラクタ
    public UserDto() {}
    
    // 全フィールドコンストラクタ
    public UserDto(Long id, String name, String email, String password) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.password = password;
    }
    
    // Getter/Setter
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
    
    // toString()にパスワードを含めている
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
