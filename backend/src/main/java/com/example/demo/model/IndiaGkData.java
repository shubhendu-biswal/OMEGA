package com.example.demo.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "india_gk_data")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class IndiaGkData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "category")
    private String category;

    @Column(name = "question", columnDefinition = "CLOB")
    @Lob
    private String question;

    @Column(name = "answer", columnDefinition = "CLOB")
    @Lob
    private String answer;

    @Column(name = "difficulty")
    private String difficulty;
}
