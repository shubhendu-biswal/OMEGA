package com.example.demo.model.training;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "dialog_training_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DialogTrainingData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "dialog_id")
    private String dialogId;

    @Column(name = "turn_number")
    private Integer turnNumber;

    @Column(name = "role")
    private String role;

    @Column(name = "message", columnDefinition = "CLOB")
    @Lob
    private String message;
}
