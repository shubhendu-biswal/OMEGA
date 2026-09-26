package com.example.demo.model.training;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "math_training_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MathTrainingData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "question", length = 1000)
    private String question;

    @Column(name = "formula", length = 500)
    private String formula;

    @Column(name = "solution", length = 2000)
    private String solution;

    @Column(name = "topic", length = 100)
    private String topic;

    @Column(name = "difficulty", length = 50)
    private String difficulty;
}
