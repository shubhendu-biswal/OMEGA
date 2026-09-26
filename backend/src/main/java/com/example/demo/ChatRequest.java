package com.example.demo;

import lombok.Data;

@Data
public class ChatRequest {
    private String prompt;
    private String agent;
    private Integer wordLimit;
    private String sessionId;

    public String getPrompt() { return prompt; }
    public void setPrompt(String prompt) { this.prompt = prompt; }

    public String getAgent() { return agent; }
    public void setAgent(String agent) { this.agent = agent; }

    public Integer getWordLimit() { return wordLimit; }
    public void setWordLimit(Integer wordLimit) { this.wordLimit = wordLimit; }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }
}
