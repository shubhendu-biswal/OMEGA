package com.example.demo.model.training;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "agri_knowledge_base")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AgriKnowledgeBase {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "topic")
    private String topic;

    @Column(name = "domain")
    private String domain;

    @Column(name = "content", columnDefinition = "CLOB")
    @Lob
    private String content;

    @Column(name = "keywords")
    private String keywords;
}
