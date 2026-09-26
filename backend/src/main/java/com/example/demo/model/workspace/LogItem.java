package com.example.demo.model.workspace;

public class LogItem {
    private final String id;
    private final String userQuery;
    private final String aiResponse;
    private final long timestamp;

    public LogItem(String id, String userQuery, String aiResponse) {
        this.id = id;
        this.userQuery = userQuery;
        this.aiResponse = aiResponse;
        this.timestamp = System.currentTimeMillis();
    }

    public String getId() {
        return id;
    }

    public String getUserQuery() {
        return userQuery;
    }

    public String getAiResponse() {
        return aiResponse;
    }

    public long getTimestamp() {
        return timestamp;
    }
}
