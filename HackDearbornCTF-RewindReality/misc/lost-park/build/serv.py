FLAG = "hd3{this_guy_thinks_the_uc_is_named_after_him}"



def main():
    ATTEMPTS = 0
    while True:
        try:
            usr = input("Enter the name of the waterpark from the picture: ").lower()
            if usr == "aruba park":
                print(f"Correct! Here's your flag: {FLAG}")
                break
            else:
                ATTEMPTS += 1
                print(f"Incorrect! You have {ATTEMPTS} attempts left.")
                if ATTEMPTS == 3:
                    print("You're out of attempts! Better luck next time.")
                    break
        except Exception as e:
            print(f"An error occurred: {e}... try again later.")
            
            
if __name__ == "__main__":
    main()