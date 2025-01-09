from pwn import *
import numpy as np




# Calculate event probabilities
prob_aes_key = 1 / 2**128
prob_lottery_win = 1 / 10**6
prob_lottery_win_5 = prob_lottery_win ** 5
prob_lottery_win_6 = prob_lottery_win ** 6
prob_lottery_win_7 = prob_lottery_win ** 7

probabilities = np.array([
    prob_aes_key, 
    prob_lottery_win, 
    prob_lottery_win_5, 
    prob_lottery_win_6,
    prob_lottery_win_7
])

event_order = np.argsort(probabilities)[::-1] + 1 

# Format the answer string in the required format
answer = ", ".join(str(x) for x in event_order)

print(answer)
