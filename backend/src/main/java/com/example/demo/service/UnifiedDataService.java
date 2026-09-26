package com.example.demo.service;

import org.springframework.stereotype.Service;
import com.example.demo.model.workspace.TaskItem;
import com.example.demo.model.workspace.NoteItem;
import com.example.demo.model.workspace.LogItem;

import java.util.*;

@Service
public class UnifiedDataService {

    private final List<TaskItem> tasks = Collections.synchronizedList(new ArrayList<>());
    private final List<NoteItem> notes = Collections.synchronizedList(new ArrayList<>());
    private final List<LogItem> logs = Collections.synchronizedList(new ArrayList<>());

    // Tasks Management
    public TaskItem addTask(String title) {
        String id = "task-" + (tasks.size() + 1);
        TaskItem item = new TaskItem(id, title);
        tasks.add(item);
        return item;
    }

    public List<TaskItem> getPendingTasks() {
        synchronized (tasks) {
            List<TaskItem> pending = new ArrayList<>();
            for (TaskItem t : tasks) {
                if (!t.isCompleted()) {
                    pending.add(t);
                }
            }
            return pending;
        }
    }

    public List<TaskItem> getAllTasks() {
        synchronized (tasks) {
            return new ArrayList<>(tasks);
        }
    }

    public boolean completeTask(String query) {
        synchronized (tasks) {
            String target = query.trim().toLowerCase();
            for (TaskItem t : tasks) {
                if (!t.isCompleted()) {
                    if (t.getId().equalsIgnoreCase(target) || t.getTitle().toLowerCase().contains(target)) {
                        t.setCompleted(true);
                        return true;
                    }
                }
            }
        }
        return false;
    }

    // Notes Management
    public NoteItem addNote(String content) {
        String id = "note-" + (notes.size() + 1);
        NoteItem item = new NoteItem(id, content);
        notes.add(item);
        return item;
    }

    public List<NoteItem> getNotes() {
        synchronized (notes) {
            return new ArrayList<>(notes);
        }
    }

    // Automatic Chat Logging
    public LogItem logChat(String userQuery, String aiResponse) {
        String id = "log-" + (logs.size() + 1);
        LogItem item = new LogItem(id, userQuery, aiResponse);
        logs.add(item);
        return item;
    }

    public List<LogItem> getRecentLogs(int limit) {
        synchronized (logs) {
            int size = logs.size();
            if (size == 0) return Collections.emptyList();
            int fromIndex = Math.max(0, size - limit);
            List<LogItem> subList = new ArrayList<>(logs.subList(fromIndex, size));
            Collections.reverse(subList);
            return subList;
        }
    }
}
