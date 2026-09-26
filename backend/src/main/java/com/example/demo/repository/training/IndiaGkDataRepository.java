package com.example.demo.repository.training;

import com.example.demo.model.training.IndiaGkData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface IndiaGkDataRepository extends JpaRepository<IndiaGkData, Long> {
    List<IndiaGkData> findByCategory(String category);
    List<IndiaGkData> findByDifficulty(String difficulty);
}
