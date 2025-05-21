-- SELECT COUNT(DISTINCT loan_id) AS total_unique_loans
-- FROM loan_data;
-- WHERE source = 'orgain';
-- SELECT table_name
-- FROM information_schema.tables
-- WHERE table_schema = 'public';


-- SELECT
--     CAST(SUM(CASE WHEN utm_source = 'organic' THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*)
-- FROM 
--     loan_data; 
--     -- Replace loan_table with the actual table name containing utm_source
-- SELECT
--     CAST(SUM(CASE WHEN utm_source = 'organic' THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*) AS percentage_organic
-- FROM
--     loan_data;



SELECT CAST(SUM(CASE WHEN loan_status_type = 'Under Processing' THEN 1 ELSE 0 END) AS FLOAT) * 100 / COUNT(*) AS percentage_under_processing FROM loan_data;