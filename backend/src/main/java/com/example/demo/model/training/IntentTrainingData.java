package com.example.demo.model.training;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "intent_training_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class IntentTrainingData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "utterance")
    private String utterance;

    @Column(name = "intent")
    private String intent;

    @Column(name = "entities")
    private String entities;
}
