package com.example.demo.repository.training;

import com.example.demo.model.training.DialogTrainingData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface DialogTrainingDataRepository extends JpaRepository<DialogTrainingData, Long> {
    List<DialogTrainingData> findByDialogIdOrderByTurnNumberAsc(String dialogId);
}
