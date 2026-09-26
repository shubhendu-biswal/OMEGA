package com.example.demo.repository.training;

import com.example.demo.model.training.FertilizerTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface FertilizerTrainingDataRepository extends JpaRepository<FertilizerTrainingData, Long> {
    List<FertilizerTrainingData> findBySoilTypeAndPredictedCrop(String soilType, String predictedCrop);
}
