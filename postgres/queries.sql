-- Find top 5 locations by the number of jobs, excluding vacancies with several locations

SELECT
"dimLocation".name,
COUNT("listingFacts".location_id) AS job_count
FROM
"listingFacts"
JOIN
"dimLocation" ON "listingFacts".location_id = "dimLocation".location_id
WHERE ("dimLocation".name<>' מספר מקומות')
GROUP BY
"dimLocation".name
ORDER BY
job_count DESC
LIMIT 5;


-- Top 5 categories with most jobs
SELECT
"dimCategory".name,
COUNT("listingFacts".category_id) AS job_count
FROM
"listingFacts"
JOIN
"dimCategory" ON "listingFacts".category_id = "dimCategory".id
GROUP BY
"dimCategory".name
ORDER BY
job_count DESC
LIMIT 5;

-- Bottom 5 categories with least jobs
SELECT
"dimCategory".name,
COUNT("listingFacts".category_id) AS job_count
FROM
"listingFacts"
JOIN
"dimCategory" ON "listingFacts".category_id = "dimCategory".id
GROUP BY
"dimCategory".name
ORDER BY
job_count ASC
LIMIT 5;


--Location where the most hi-tech jobs located.
-- Hi-tech categories: אינטרנט, הייטק-QA, הייטק-חומרה, הייטק-כללי, הייטק-תוכנה, אבטחת מידע 
SELECT "dimLocation".name, COUNT(*) as count
FROM "listingFacts"
JOIN "dimLocation" ON "listingFacts".location_id = "dimLocation".location_id
JOIN "dimCategory" ON "listingFacts".category_id = "dimCategory".id
WHERE "dimCategory".name IN ('אינטרנט', 'הייטק-QA', 'הייטק-חומרה', 'הייטק-כללי', 'הייטק-תוכנה', 'אבטחת מידע')
GROUP BY "dimLocation".name
ORDER BY count DESC
LIMIT 5;

--Top 5 companies
SELECT "dimCompany".name, COUNT(*) as job_count
FROM "listingFacts"
JOIN "dimCompany" ON "listingFacts".company_id = "dimCompany".company_id
WHERE "dimCompany".name<>' None'
GROUP BY "dimCompany".name
ORDER BY job_count DESC
LIMIT 5;

