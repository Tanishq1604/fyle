-- Write query to get count of assignments in each grade
WITH AllGrades AS (
    SELECT 'A' as grade UNION
    SELECT 'B' UNION
    SELECT 'C' UNION
    SELECT 'D' UNION
    SELECT 'F'
)
SELECT 
    ag.grade,
    COUNT(a.grade) as count
FROM AllGrades ag
LEFT JOIN assignments a ON a.grade = ag.grade 
    AND a.state = 'GRADED'
GROUP BY ag.grade
ORDER BY ag.grade ASC;
