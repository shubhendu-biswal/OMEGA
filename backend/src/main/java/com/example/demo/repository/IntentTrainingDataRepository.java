package com.example.demo.repository;

import com.example.demo.model.IntentTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface IntentTrainingDataRepository extends JpaRepository<IntentTrainingData, Long> {
    List<IntentTrainingData> findByIntent(String intent);
}
