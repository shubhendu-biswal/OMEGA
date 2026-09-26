package com.example.demo.repository.training;

import com.example.demo.model.training.IntentTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface IntentTrainingDataRepository extends JpaRepository<IntentTrainingData, Long> {
    List<IntentTrainingData> findByIntent(String intent);
}
