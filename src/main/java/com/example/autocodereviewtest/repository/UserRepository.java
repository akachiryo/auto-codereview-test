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
    
    /**
 * Retrieves a user by their exact email address.
 *
 * @param email the email address to search for
 * @return an Optional containing the user if found, or empty if not found
 */
Optional<User> findByEmail(String email);
    
    /**
 * Retrieves a list of users whose names contain the specified substring.
 *
 * @param name the substring to search for within user names
 * @return a list of users whose names contain the given substring
 */
List<User> findByNameContaining(String name);
    
    /**
     * Retrieves a list of users whose names contain the specified substring using a JPQL LIKE query.
     *
     * @param name the substring to search for within user names
     * @return a list of users whose names match the given pattern
     */
    @Query("SELECT u FROM User u WHERE u.name LIKE %:name%")
    List<User> findUsersByNameLike(@Param("name") String name);
    
    /**
     * Retrieves a list of users whose name exactly matches the specified value using a native SQL query.
     *
     * @param name the exact name to search for
     * @return a list of users with the specified name
     * 
     * <p><b>Note:</b> This method uses a native query and may be vulnerable to SQL injection if not used carefully.</p>
     */
    @Query(value = "SELECT * FROM users WHERE name = ?1", nativeQuery = true)
    List<User> findUsersByNameNative(String name);
} 
