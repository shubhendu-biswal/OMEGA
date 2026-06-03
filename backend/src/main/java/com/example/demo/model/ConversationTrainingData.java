package com.example.demo.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "conversation_training_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ConversationTrainingData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "category")
    private String category;

    @Column(name = "instruction", columnDefinition = "CLOB")
    @Lob
    private String instruction;

    @Column(name = "response", columnDefinition = "CLOB")
    @Lob
    private String response;

    @Column(name = "difficulty")
    private String difficulty;
}
