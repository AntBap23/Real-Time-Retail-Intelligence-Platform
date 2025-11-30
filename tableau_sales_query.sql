-- ============================================================================
-- TABLEAU SALES DATA QUERY
-- Complete star schema join for visualization in Tableau
-- ============================================================================
-- This query joins all dimension tables with the fact_sales table
-- All necessary columns included for visualization - do trends in Tableau
-- ============================================================================

SELECT 
    -- Sales Transaction Data
    fs.sales_key,
    fs.sale_id,
    fs.order_date,
    fs.date_key,
    fs.quantity,
    fs.unit_price,
    fs.total_amount,
    fs.discount_percent,
    fs.discount_amount,
    fs.tax_amount,
    fs.shipping_cost,
    fs.order_status,
    fs.payment_method,
    fs.profit_amount,
    fs.margin_percent,
    
    -- Product Information
    dp.product_key,
    dp.product_id,
    dp.product_name,
    dp.category AS product_category,
    dp.subcategory AS product_subcategory,
    dp.brand AS product_brand,
    dp.price AS product_price,
    dp.cost AS product_cost,
    dp.color AS product_color,
    dp.size AS product_size,
    
    -- Region Information
    dr.region_key,
    dr.region_id,
    dr.region_name,
    dr.country AS region_country,
    dr.region_group,
    
    -- Customer/Reseller Information
    dres.reseller_key,
    dres.reseller_id,
    dres.reseller_name,
    dres.business_type,
    dres.contact_person,
    dres.email AS reseller_email,
    dres.customer_tier,
    
    -- Salesperson Information
    dsp.salesperson_key,
    dsp.salesperson_id,
    dsp.first_name AS salesperson_first_name,
    dsp.last_name AS salesperson_last_name,
    dsp.full_name AS salesperson_full_name,
    dsp.email AS salesperson_email,
    dsp.department,
    dsp.performance_tier AS salesperson_performance_tier,
    dsp.commission_rate,
    dsp.sales_quota

FROM facts.fact_sales fs

LEFT JOIN dimensions.dim_product dp
    ON fs.product_key = dp.product_key

LEFT JOIN dimensions.dim_region dr
    ON fs.region_key = dr.region_key

LEFT JOIN dimensions.dim_reseller dres
    ON fs.reseller_key = dres.reseller_key

LEFT JOIN dimensions.dim_salesperson dsp
    ON fs.salesperson_key = dsp.salesperson_key

ORDER BY fs.order_date DESC, fs.sales_key;

