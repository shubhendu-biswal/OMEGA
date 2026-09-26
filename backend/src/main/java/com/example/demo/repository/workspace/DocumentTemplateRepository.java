package com.example.demo.repository.workspace;

import com.example.demo.model.workspace.DocumentTemplate;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface DocumentTemplateRepository extends JpaRepository<DocumentTemplate, Long> {
    List<DocumentTemplate> findByDocType(String docType);
    List<DocumentTemplate> findByDocTypeAndCategory(String docType, String category);
}
