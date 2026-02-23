try:
    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))
    print("Sum: ", num1 + num2)
    if num2 == 0:
        print("Cannot divide by zero")
    else:
        print("Division Result: ", num1 / num2)
except ValueError:
    print("Invalid input")
   