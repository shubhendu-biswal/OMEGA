package com.example.demo.repository;

import com.example.demo.model.AgriKnowledgeBase;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface AgriKnowledgeBaseRepository extends JpaRepository<AgriKnowledgeBase, Long> {
    List<AgriKnowledgeBase> findByDomain(String domain);
    List<AgriKnowledgeBase> findByTopicContainingIgnoreCase(String topic);
}
