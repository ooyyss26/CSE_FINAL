import time as t
import random as rd

y = rd.randint(1,100)
tries = 0

while True:
    guess = int(input("Guessing Game!! \nIf you guess incorrectly your PC will go BOOM!!!! \nWhat's your first guess? \nInput number: "))
    
    if guess == y:
        print("SAFE!!!!")
        break
      
    elif guess > y:
        print("Bruh, too high.")
        tries= tries + 1
        print("Wrong! Incorrect answer! Failed attempt:", tries)

    elif guess < y:
        print("Bruh, too low.")
        tries= tries + 1
        print("Wrong! Incorrect answer! Failed attempt:", tries)
    
    print(tries)    

    if tries == 3:
        print("You Failed!!!!! \nGoodbye!")
        break
    
    
print("Thank you for playing!")
