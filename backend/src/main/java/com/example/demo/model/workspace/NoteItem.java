package com.example.demo.model.workspace;

public class NoteItem {
    private final String id;
    private final String content;
    private final long createdAt;

    public NoteItem(String id, String content) {
        this.id = id;
        this.content = content;
        this.createdAt = System.currentTimeMillis();
    }

    public String getId() {
        return id;
    }

    public String getContent() {
        return content;
    }

    public long getCreatedAt() {
        return createdAt;
    }
}
