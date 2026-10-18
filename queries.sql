USE aqi_analytics_db;

-- 1. Average AQI per city, with its health category
SELECT city,
       ROUND(AVG(aqi)) AS avg_aqi,
       CASE
         WHEN AVG(aqi) <= 50  THEN 'Good'
         WHEN AVG(aqi) <= 100 THEN 'Moderate'
         WHEN AVG(aqi) <= 150 THEN 'Unhealthy for Sensitive Groups'
         WHEN AVG(aqi) <= 200 THEN 'Unhealthy'
         WHEN AVG(aqi) <= 300 THEN 'Very Unhealthy'
         ELSE 'Hazardous'
       END AS category
FROM aqi_readings
GROUP BY city
ORDER BY avg_aqi DESC;

-- 2. Share of hours with unhealthy air (AQI above 150), per city
SELECT city,
       ROUND(100 * SUM(aqi > 150) / COUNT(*), 1) AS pct_unhealthy_hours
FROM aqi_readings
GROUP BY city
ORDER BY pct_unhealthy_hours DESC;

-- 3. Which hour of the day is worst (IST), across all cities
SELECT HOUR(measured_at) AS hour_of_day,
       ROUND(AVG(aqi), 1) AS avg_aqi
FROM aqi_readings
GROUP BY hour_of_day
ORDER BY avg_aqi DESC;

-- 4. Each city's single worst day (window function)
SELECT city, day, avg_aqi
FROM (
    SELECT city,
           DATE(measured_at) AS day,
           ROUND(AVG(aqi)) AS avg_aqi,
           ROW_NUMBER() OVER (PARTITION BY city ORDER BY AVG(aqi) DESC) AS rn
    FROM aqi_readings
    GROUP BY city, DATE(measured_at)
) ranked
WHERE rn = 1
ORDER BY avg_aqi DESC;

-- 5. Last 7 days vs the 7 days before: is air getting better or worse?
SET @latest = (SELECT MAX(measured_at) FROM aqi_readings);

SELECT city, last_7_days, previous_7_days,
       last_7_days - previous_7_days AS change_in_aqi
FROM (
    SELECT city,
           ROUND(AVG(CASE WHEN measured_at > @latest - INTERVAL 7 DAY THEN aqi END)) AS last_7_days,
           ROUND(AVG(CASE WHEN measured_at <= @latest - INTERVAL 7 DAY
                           AND measured_at >  @latest - INTERVAL 14 DAY THEN aqi END)) AS previous_7_days
    FROM aqi_readings
    GROUP BY city
)
ORDER BY change_in_aqi DESC;
