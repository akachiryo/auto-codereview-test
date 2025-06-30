package com.example.autocodereviewtest.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
public class WelcomeController {
    
    /**
     * Handles GET requests to the root path and returns application metadata, available API endpoints, and sample request examples.
     *
     * @return a map containing application information, a list of API endpoints with descriptions, and example curl commands.
     */
    @GetMapping("/")
    public Map<String, Object> welcome() {
        Map<String, Object> response = new HashMap<>();
        response.put("application", "Gemini Code Assist テスト用サンプルプロジェクト");
        response.put("description", "Java Spring Boot アプリケーション");
        response.put("version", "1.0.0");
        response.put("timestamp", LocalDateTime.now());
        response.put("status", "running");
        
        // API エンドポイント一覧
        Map<String, Object> endpoints = new HashMap<>();
        endpoints.put("users_list", "GET /api/users - 全ユーザー取得");
        endpoints.put("user_detail", "GET /api/users/{id} - 特定ユーザー取得");
        endpoints.put("user_create", "POST /api/users - ユーザー作成");
        endpoints.put("user_update", "PUT /api/users/{id} - ユーザー更新");
        endpoints.put("user_delete", "DELETE /api/users/{id} - ユーザー削除");
        endpoints.put("user_login", "POST /api/users/login - ユーザー認証");
        endpoints.put("user_search", "GET /api/users/search?name={name} - ユーザー検索");
        endpoints.put("h2_console", "GET /h2-console - H2データベースコンソール");
        
        response.put("available_endpoints", endpoints);
        
        // サンプルリクエスト
        Map<String, String> samples = new HashMap<>();
        samples.put("create_user", "curl -X POST http://localhost:8080/api/users -H 'Content-Type: application/json' -d '{\"name\":\"テストユーザー\",\"email\":\"test@example.com\",\"password\":\"password123\"}'");
        samples.put("get_users", "curl http://localhost:8080/api/users");
        
        response.put("sample_requests", samples);
        
        return response;
    }
    
    /**
     * Handles HTTP GET requests to the /health endpoint and returns the application's health status.
     *
     * @return a map containing the status ("UP"), current timestamp, and application identifier.
     */
    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("timestamp", LocalDateTime.now());
        response.put("application", "auto-codereview-test");
        return response;
    }
} 
