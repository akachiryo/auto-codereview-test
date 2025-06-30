package com.example.autocodereviewtest.repository;

import com.example.autocodereviewtest.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByEmail(String email);
    
    List<User> findByNameContaining(String name);
    
    // 非効率なクエリ（N+1問題の可能性）
    @Query("SELECT u FROM User u WHERE u.name LIKE %:name%")
    List<User> findUsersByNameLike(@Param("name") String name);
    
    // SQLインジェクションの脆弱性がある可能性のあるクエリ
    @Query(value = "SELECT * FROM users WHERE name = ?1", nativeQuery = true)
    List<User> findUsersByNameNative(String name);
} 
