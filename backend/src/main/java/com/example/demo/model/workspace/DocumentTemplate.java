package com.example.demo.model.workspace;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "document_templates")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DocumentTemplate {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "doc_type", length = 50)
    private String docType;

    @Column(name = "category", length = 100)
    private String category;

    @Column(name = "section", length = 50)
    private String section;

    @Column(name = "template_text", length = 2000)
    private String templateText;
}
