package com.example.demo.repository.training;

import com.example.demo.model.training.ConversationTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ConversationTrainingDataRepository extends JpaRepository<ConversationTrainingData, Long> {
    List<ConversationTrainingData> findByCategory(String category);
    List<ConversationTrainingData> findByDifficulty(String difficulty);
}
