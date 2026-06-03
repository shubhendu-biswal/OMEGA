package com.example.demo;

import lombok.Data;

@Data
public class ChatRequest {
    private String prompt;
    private String agent;
}
