-- Daily booking counts at the activity level
-- activity_date = date the tour takes place (date_of_travel)
-- Filtered to confirmed bookings (status_id = 1 / "active")
-- Date range: 2023-01-01 to 2026-05-01 (inclusive)

SELECT
    tour_id                            AS activity_id,
    CAST(date_of_travel AS DATE)       AS activity_date,
    COUNT(booking_id)                  AS bookings
FROM production.dwh.fact_booking
WHERE status_id = 1
  AND CAST(date_of_travel AS DATE) BETWEEN '2023-01-01' AND '2026-05-01'
GROUP BY
    tour_id,
    CAST(date_of_travel AS DATE)
ORDER BY
    activity_id,
    activity_date
