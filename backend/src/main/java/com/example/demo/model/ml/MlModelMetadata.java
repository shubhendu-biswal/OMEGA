package com.example.demo.model.ml;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "ml_model_metadata")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MlModelMetadata {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "model_name", length = 100)
    private String modelName;

    @Column(name = "training_time")
    private LocalDateTime trainingTime;

    @Column(name = "records_count")
    private Long recordsCount;

    @Column(name = "accuracy")
    private Double accuracy;

    @Column(name = "status", length = 50)
    private String status;
}
