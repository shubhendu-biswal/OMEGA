package com.example.demo.model.training;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "fertilizer_training_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class FertilizerTrainingData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "temperature")
    private Double temperature;

    @Column(name = "soil_type")
    private String soilType;

    @Column(name = "predicted_crop")
    private String predictedCrop;

    @Column(name = "fertilizer")
    private String fertilizer;
}
