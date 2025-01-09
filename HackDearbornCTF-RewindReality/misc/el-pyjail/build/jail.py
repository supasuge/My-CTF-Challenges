import os
print("Welcome to Jail You can't escape, try to hack me if you can! Think of a shell and you'll do well!")
print('-'*10+'\n')
print("""

██╗  ██╗██████╗ ██████╗     ██████╗ ██╗   ██╗   ██╗ █████╗ ██╗██╗     
██║  ██║██╔══██╗╚════██╗    ██╔══██╗╚██╗ ██╔╝   ██║██╔══██╗██║██║     
███████║██║  ██║ █████╔╝    ██████╔╝ ╚████╔╝    ██║███████║██║██║     
██╔══██║██║  ██║ ╚═══██╗    ██╔═══╝   ╚██╔╝██   ██║██╔══██║██║██║     
██║  ██║██████╔╝██████╔╝    ██║        ██║ ╚█████╔╝██║  ██║██║███████╗
╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝        ╚═╝  ╚════╝ ╚═╝  ╚═╝╚═╝╚══════╝

""")
print('-'*10+'\n')
while True:
    x = input(">>> ")
    whitelist = ["0","1","2","3","4","5","6","7","8","9","/","*","?","$",".","'","!","@","#"]
    for i in range(11):
        whitelist += whitelist[i].upper()
    if any([i for i in x if i not in whitelist]):
        print("I see you are trying to hack, Exiting!")
        exit(0)
    else:
        os.system(x)