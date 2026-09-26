package com.example.demo.model.workspace;

public class TaskItem {
    private final String id;
    private final String title;
    private boolean completed;
    private final long createdAt;

    public TaskItem(String id, String title) {
        this.id = id;
        this.title = title;
        this.completed = false;
        this.createdAt = System.currentTimeMillis();
    }

    public String getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public boolean isCompleted() {
        return completed;
    }

    public void setCompleted(boolean completed) {
        this.completed = completed;
    }

    public long getCreatedAt() {
        return createdAt;
    }
}
