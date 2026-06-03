package com.example.demo.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "feedback_training_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class FeedbackTrainingData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_query")
    private String userQuery;

    @Column(name = "ai_response", columnDefinition = "CLOB")
    @Lob
    private String aiResponse;

    @Column(name = "rating")
    private Integer rating;

    @Column(name = "sentiment")
    private String sentiment;
}
