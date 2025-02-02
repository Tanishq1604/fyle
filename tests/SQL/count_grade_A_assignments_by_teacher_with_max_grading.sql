-- Write query to find the number of grade A's given by the teacher who has graded the most assignments

WITH TeacherGradedCounts AS (
    SELECT teacher_id, COUNT(*) as graded_count
    FROM assignments
    WHERE state = 'GRADED'
    GROUP BY teacher_id
),
MaxGradedTeacher AS (
    SELECT teacher_id
    FROM TeacherGradedCounts
    WHERE graded_count = (SELECT MAX(graded_count) FROM TeacherGradedCounts)
    LIMIT 1
)
SELECT COUNT(*) as grade_a_count
FROM assignments
WHERE teacher_id = (SELECT teacher_id FROM MaxGradedTeacher)
    AND grade = 'A'
    AND state = 'GRADED';
