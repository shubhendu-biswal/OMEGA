package com.example.demo.repository.training;

import com.example.demo.model.training.FeedbackTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface FeedbackTrainingDataRepository extends JpaRepository<FeedbackTrainingData, Long> {
    List<FeedbackTrainingData> findBySentiment(String sentiment);
    List<FeedbackTrainingData> findByRatingGreaterThanEqual(Integer rating);
}
