package com.example.demo.repository.training;

import com.example.demo.model.training.MathTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface MathTrainingDataRepository extends JpaRepository<MathTrainingData, Long> {
    List<MathTrainingData> findByTopic(String topic);
    List<MathTrainingData> findByDifficulty(String difficulty);
}
