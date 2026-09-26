package com.example.demo.repository.ml;

import com.example.demo.model.ml.MlModelMetadata;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface MlModelMetadataRepository extends JpaRepository<MlModelMetadata, Long> {
    List<MlModelMetadata> findByModelNameOrderByTrainingTimeDesc(String modelName);
    Optional<MlModelMetadata> findFirstByModelNameOrderByTrainingTimeDesc(String modelName);
}
