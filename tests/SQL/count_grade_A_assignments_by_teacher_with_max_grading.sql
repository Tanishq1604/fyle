-- Write query to find the number of grade A's given by the teacher who has graded the most assignments

WITH TeacherWithMostGrades AS (
    SELECT teacher_id
    FROM assignments
    WHERE state = 'GRADED'
    GROUP BY teacher_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
SELECT COUNT(*) 
FROM assignments
WHERE teacher_id = (SELECT teacher_id FROM TeacherWithMostGrades)
    AND grade = 'A'
    AND state = 'GRADED';
