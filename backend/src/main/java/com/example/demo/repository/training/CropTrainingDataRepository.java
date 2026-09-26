package com.example.demo.repository.training;

import com.example.demo.model.training.CropTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface CropTrainingDataRepository extends JpaRepository<CropTrainingData, Long> {
    List<CropTrainingData> findBySoilType(String soilType);
    List<CropTrainingData> findByCrop(String crop);
}
