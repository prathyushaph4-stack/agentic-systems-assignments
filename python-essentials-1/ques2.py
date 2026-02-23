try:
    # Get user inputs
    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    age_input = input("Enter your age: ")
    
    # Convert age to integer
    age = int(age_input)
    
    # Validate age
    if age < 0:
        print("Age cannot be negative")
    else:
        # Print full name and age next year
        print("Full Name: " + first_name + " " + last_name)
        print("You will be " + str(age + 1) + " next year")
        
except ValueError:
    print("Invalid age input")
except Exception as e:
    print(f"An error occurred: {e}")