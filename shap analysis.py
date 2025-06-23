WITH exploded_shap AS (
  SELECT
    record_id,  -- Unique ID per row if available
    feature_value,
    REGEXP_EXTRACT(feature_value, r'^([^()]+)') AS feature_name,
    SAFE_CAST(REGEXP_EXTRACT(feature_value, r'\(([^()]+)\)') AS FLOAT64) AS shap_value
  FROM (
    SELECT
      record_id,
      TRIM(value) AS feature_value
    FROM `project.dataset.ml_output_table`,
    UNNEST(SPLIT(feature_importance, ',')) AS value
  )
)