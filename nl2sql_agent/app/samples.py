
SQL_SAMPLES = [
    {
        "question": "Show incomplete leads by breakdown of lead status and loan status",
        "sql": """for lead status
                WITH MonthlyCounts AS (
                    SELECT
                        lead_status_type,
                        COUNT(CASE WHEN EXTRACT(YEAR FROM loan_creation_date) = 2024 AND EXTRACT(MONTH FROM loan_creation_date) = 4 THEN loan_id END) AS apr_2024_count,
                        COUNT(CASE WHEN EXTRACT(YEAR FROM loan_creation_date) = 2025 AND EXTRACT(MONTH FROM loan_creation_date) = 3 THEN loan_id END) AS mar_2025_count,
                        COUNT(CASE WHEN EXTRACT(YEAR FROM loan_creation_date) = 2025 AND EXTRACT(MONTH FROM loan_creation_date) = 4 THEN loan_id END) AS apr_2025_count
                    FROM
                        investor.funnel_leads_data_2
                    WHERE
                        -- Filter for relevant months to optimize performance
                        (EXTRACT(YEAR FROM loan_creation_date) = 2024 AND EXTRACT(MONTH FROM loan_creation_date) = 4)
                        OR (EXTRACT(YEAR FROM loan_creation_date) = 2025 AND EXTRACT(MONTH FROM loan_creation_date) IN (3, 4))
                    GROUP BY
                        lead_status_type
                )
                SELECT
                    mc.lead_status_type,
                    mc.apr_2024_count,
                    mc.mar_2025_count,
                    mc.apr_2025_count,
                    -- Calculate Month-over-Month Change (March 2025 to April 2025)
                    -- Using NULLIF to prevent division by zero, resulting in NULL for percentage if denominator is 0
                    ROUND(
                        (mc.apr_2025_count - mc.mar_2025_count) * 100.0 / NULLIF(mc.mar_2025_count, 0),
                        2
                    ) AS mom_change_percentage,
                    -- Calculate Year-over-Year Change (April 2024 to April 2025)
                    -- Using NULLIF to prevent division by zero, resulting in NULL for percentage if denominator is 0
                    ROUND(
                        (mc.apr_2025_count - mc.apr_2024_count) * 100.0 / NULLIF(mc.apr_2024_count, 0),
                        2
                    ) AS yoy_change_percentage
                FROM
                    MonthlyCounts mc
                ORDER BY
                    mc.lead_status_type;

                for loan status

                WITH MonthlyCounts AS (
                    SELECT
                        loan_status_type, -- Changed from lead_status_type
                        COUNT(CASE WHEN EXTRACT(YEAR FROM loan_creation_date) = 2024 AND EXTRACT(MONTH FROM loan_creation_date) = 4 THEN loan_id END) AS apr_2024_count,
                        COUNT(CASE WHEN EXTRACT(YEAR FROM loan_creation_date) = 2025 AND EXTRACT(MONTH FROM loan_creation_date) = 3 THEN loan_id END) AS mar_2025_count,
                        COUNT(CASE WHEN EXTRACT(YEAR FROM loan_creation_date) = 2025 AND EXTRACT(MONTH FROM loan_creation_date) = 4 THEN loan_id END) AS apr_2025_count
                    FROM
                        investor.funnel_leads_data_2
                    WHERE
                        -- Filter for relevant months to optimize performance
                        (EXTRACT(YEAR FROM loan_creation_date) = 2024 AND EXTRACT(MONTH FROM loan_creation_date) = 4)
                        OR (EXTRACT(YEAR FROM loan_creation_date) = 2025 AND EXTRACT(MONTH FROM loan_creation_date) IN (3, 4))
                    GROUP BY
                        loan_status_type -- Changed from lead_status_type
                )
                SELECT
                    mc.loan_status_type, -- Changed from lead_status_type
                    mc.apr_2024_count,
                    mc.mar_2025_count,
                    mc.apr_2025_count,
                    -- Calculate Month-over-Month Change (March 2025 to April 2025)
                    -- Using NULLIF to prevent division by zero, resulting in NULL for percentage if denominator is 0
                    ROUND(
                        (mc.apr_2025_count - mc.mar_2025_count) * 100.0 / NULLIF(mc.mar_2025_count, 0),
                        2
                    ) AS mom_change_percentage,
                    -- Calculate Year-over-Year Change (April 2024 to April 2025)
                    -- Using NULLIF to prevent division by zero, resulting in NULL for percentage if denominator is 0
                    ROUND(
                        (mc.apr_2025_count - mc.apr_2024_count) * 100.0 / NULLIF(mc.apr_2024_count, 0),
                        2
                    ) AS yoy_change_percentage
                FROM
                    MonthlyCounts mc
                ORDER BY
                    mc.loan_status_type; -- Changed from lead_status_type"""
    },
    {
        "question": "Count of leads and Rejection of leads by customer_UTM, stages, reason",
        "sql": """  
                count of leads
                    WITH
                    -- Step 1: Aggregate lead counts by customer_utm_type and month
                    monthly_leads AS (
                        SELECT
                        customer_utm_type,
                        -- Extract year and month for easier filtering and pivoting
                        TO_CHAR(loan_creation_date, 'YYYY-MM') AS lead_month_year,
                        -- Count unique loan_ids as leads
                        COUNT(DISTINCT loan_id) AS lead_count
                        FROM
                        investor.funnel_leads_data_2
                        WHERE
                        -- Filter for the specific months relevant to the report
                        -- (April 2024 for YoY, March 2025 for MoM, April 2025 for current)
                        TO_CHAR(loan_creation_date, 'YYYY-MM') IN ('2024-04', '2025-03', '2025-04')
                        GROUP BY
                        customer_utm_type,
                        TO_CHAR(loan_creation_date, 'YYYY-MM')
                    ),
                    -- Step 2: Pivot the monthly data to have months as columns
                    pivoted_leads AS (
                        SELECT
                        customer_utm_type,
                        -- Sum leads for April 2024, defaulting to 0 if no leads for that type in that month
                        COALESCE(SUM(CASE WHEN lead_month_year = '2024-04' THEN lead_count ELSE 0 END), 0) AS leads_apr_2024,
                        -- Sum leads for March 2025
                        COALESCE(SUM(CASE WHEN lead_month_year = '2025-03' THEN lead_count ELSE 0 END), 0) AS leads_mar_2025,
                        -- Sum leads for April 2025
                        COALESCE(SUM(CASE WHEN lead_month_year = '2025-04' THEN lead_count ELSE 0 END), 0) AS leads_apr_2025
                        FROM
                        monthly_leads
                        GROUP BY
                        customer_utm_type
                    )
                    -- Step 3: Calculate MoM and YoY changes and select the final output
                    SELECT
                    p.customer_utm_type,
                    p.leads_apr_2024 AS "Apr 2024",
                    p.leads_mar_2025 AS "Mar 2025",
                    p.leads_apr_2025 AS "April 2025", -- Matching user's requested column name
                    -- Calculate MoM Change: ((Current Month - Previous Month) / Previous Month) * 100
                    -- Handle division by zero by returning NULL if previous month's leads are 0
                    CASE
                        WHEN p.leads_mar_2025 = 0 THEN NULL
                        ELSE ROUND(
                        ((p.leads_apr_2025 - p.leads_mar_2025) * 100.0 / p.leads_mar_2025),
                        2
                        )
                    END AS "MoM Change",
                    -- Calculate YoY Change: ((Current Month - Same Month Previous Year) / Same Month Previous Year) * 100
                    -- Handle division by zero by returning NULL if previous year's leads are 0
                    CASE
                        WHEN p.leads_apr_2024 = 0 THEN NULL
                        ELSE ROUND(
                        ((p.leads_apr_2025 - p.leads_apr_2024) * 100.0 / p.leads_apr_2024),
                        2
                        )
                    END AS "YoY Change"
                    FROM
                    pivoted_leads p
                    ORDER BY
                    p.customer_utm_type;

                    rejection of leads
                    WITH
                    -- Step 1: Aggregate rejected lead counts by customer_utm_type and month
                    monthly_rejected_leads AS (
                        SELECT
                        customer_utm_type,
                        -- Extract year and month for easier filtering and pivoting
                        TO_CHAR(loan_creation_date, 'YYYY-MM') AS lead_month_year,
                        -- Count unique loan_ids as rejected leads
                        COUNT(DISTINCT loan_id) AS rejected_lead_count
                        FROM
                        investor.funnel_leads_data_2
                        WHERE
                        -- Filter for the specific months relevant to the report
                        TO_CHAR(loan_creation_date, 'YYYY-MM') IN ('2024-04', '2025-03', '2025-04')
                        -- Filter for rejected leads based on loan_status_type
                        AND loan_status_type = 'Rejected'
                        GROUP BY
                        customer_utm_type,
                        TO_CHAR(loan_creation_date, 'YYYY-MM')
                    ),
                    -- Step 2: Pivot the monthly rejected lead data to have months as columns
                    pivoted_rejected_leads AS (
                        SELECT
                        customer_utm_type,
                        -- Sum rejected leads for April 2024, defaulting to 0 if no rejections for that type in that month
                        COALESCE(SUM(CASE WHEN lead_month_year = '2024-04' THEN rejected_lead_count ELSE 0 END), 0) AS rejected_leads_apr_2024,
                        -- Sum rejected leads for March 2025
                        COALESCE(SUM(CASE WHEN lead_month_year = '2025-03' THEN rejected_lead_count ELSE 0 END), 0) AS rejected_leads_mar_2025,
                        -- Sum rejected leads for April 2025
                        COALESCE(SUM(CASE WHEN lead_month_year = '2025-04' THEN rejected_lead_count ELSE 0 END), 0) AS rejected_leads_apr_2025
                        FROM
                        monthly_rejected_leads
                        GROUP BY
                        customer_utm_type
                    )
                    -- Step 3: Calculate MoM and YoY changes for rejected leads and select the final output
                    SELECT
                    p.customer_utm_type,
                    p.rejected_leads_apr_2024 AS "Rejections Apr 2024",
                    p.rejected_leads_mar_2025 AS "Rejections Mar 2025",
                    p.rejected_leads_apr_2025 AS "Rejections April 2025",
                    -- Calculate MoM Change for rejections: ((Current Month Rejections - Previous Month Rejections) / Previous Month Rejections) * 100
                    -- Handle division by zero by returning NULL if previous month's rejections are 0
                    CASE
                        WHEN p.rejected_leads_mar_2025 = 0 THEN NULL
                        ELSE ROUND(
                        ((p.rejected_leads_apr_2025 - p.rejected_leads_mar_2025) * 100.0 / p.rejected_leads_mar_2025),
                        2
                        )
                    END AS "MoM Change",
                    -- Calculate YoY Change for rejections: ((Current Month Rejections - Same Month Previous Year Rejections) / Same Month Previous Year Rejections) * 100
                    -- Handle division by zero by returning NULL if previous year's rejections are 0
                    CASE
                        WHEN p.rejected_leads_apr_2024 = 0 THEN NULL
                        ELSE ROUND(
                        ((p.rejected_leads_apr_2025 - p.rejected_leads_apr_2024) * 100.0 / p.rejected_leads_apr_2024),
                        2
                        )
                    END AS "YoY Change"
                    FROM
                    pivoted_rejected_leads p
                    ORDER BY
                    p.customer_utm_type;
        
        """
    }
    # {
    #     "question": "Find the top 5 products by sales revenue",
    #     "sql": """
    #     SELECT p.product_id, p.name, SUM(o.quantity * o.price) as revenue
    #     FROM order_items o
    #     JOIN products p ON o.product_id = p.product_id
    #     GROUP BY p.product_id, p.name
    #     ORDER BY revenue DESC
    #     LIMIT 5
    #     """
    # }
]
