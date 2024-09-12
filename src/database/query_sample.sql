-- 今日上映する映画
SELECT
	theaters.name, 
	movies.title,
	movie_schedule.start_datetime,
    movie_schedule.start_datetime + INTERVAL '1 minute' * CAST(REPLACE(movies.runtime, '分', '') AS INTEGER) AS end_datetime,
	movies.type,
	movies.staff
FROM movie_schedule
JOIN movies ON movie_schedule.movie_id = movies.id
JOIN programs ON programs.id = movies.program_id
JOIN theaters ON theaters.id = programs.theater_id
WHERE DATE(start_datetime) = CURRENT_DATE
ORDER BY theaters.id ASC, movie_schedule.start_datetime ASC;