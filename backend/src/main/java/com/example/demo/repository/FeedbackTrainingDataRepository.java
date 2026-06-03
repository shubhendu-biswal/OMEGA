package com.example.demo.repository;

import com.example.demo.model.FeedbackTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface FeedbackTrainingDataRepository extends JpaRepository<FeedbackTrainingData, Long> {
    List<FeedbackTrainingData> findBySentiment(String sentiment);
    List<FeedbackTrainingData> findByRatingGreaterThanEqual(Integer rating);
}
