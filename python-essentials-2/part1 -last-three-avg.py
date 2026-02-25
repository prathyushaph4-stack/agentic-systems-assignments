class StudentMarks:
    def __init__(self, marks):
        self.marks = marks
    
    def last_three_avg(self):
        try:
            if len(self.marks) < 3:
                raise ValueError("Not enough marks")
            
            last_three = self.marks[-3:]
            average = sum(last_three) / len(last_three)
            print(f"Average of last 3 marks is: {average}")
        except ValueError:
            print("Not enough marks to calculate average")


# Example usage
marks = [50, 60, 70, 80, 90]
student = StudentMarks(marks)
student.last_three_avg()