package com.example.demo.repository;

import com.example.demo.model.IndiaGkData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface IndiaGkDataRepository extends JpaRepository<IndiaGkData, Long> {
    List<IndiaGkData> findByCategory(String category);

    @Query(
        value = "SELECT * FROM (SELECT * FROM india_gk_data WHERE CONTAINS(question, :searchQuery, 1) > 0 ORDER BY SCORE(1) DESC) WHERE ROWNUM <= :limit",
        nativeQuery = true
    )
    List<IndiaGkData> searchByQuestionText(@Param("searchQuery") String searchQuery, @Param("limit") int limit);
}
