package com.example.demo.repository;

import com.example.demo.model.DialogTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface DialogTrainingDataRepository extends JpaRepository<DialogTrainingData, Long> {
    List<DialogTrainingData> findByDialogIdOrderByTurnNumberAsc(String dialogId);
}
