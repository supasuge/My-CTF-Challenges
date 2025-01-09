import time

def extract_flag_v1(H, S):
    # First function
    N = 137
    inv_6 = pow(6, -1, N)  # Modular inverse using pow
    Q = []
    for i in range(N):
        # Q[i] = (S[i] - 5 * H[i] - 14) * inv_6 mod N
        val = (S[i] - 5 * H[i] - 14) % N
        q_i = (val * inv_6) % N
        Q.append(q_i)
    flag_chars = []
    for q in Q[:30]:
        if 32 <= q <= 126:
            flag_chars.append(chr(q))
        else:
            flag_chars.append('?')
    flag = ''.join(flag_chars)
    return flag

def extract_flag_v2(H, S):
    # Second function
    N = 137
    inv_6 = pow(6, -1, N)  # Modular inverse using pow
    Q = [(s - 5 * h - 14) * inv_6 % N for s, h in zip(S, H)]
    flag = ''.join(chr(q) if 32 <= q <= 126 else '?' for q in Q[:30])
    return flag.rstrip('?')

# Test vectors
H = [37, 28, 96, 120, 56, 34, 109, 41, 68, 49, 16, 18, 51, 84, 95, 20, 93, 136, 16, 48, 48, 85, 16, 47, 56, 60, 116, 96, 107, 54, 120, 133, 37, 28, 96, 120, 56, 34, 109, 41, 68, 49, 16, 18, 51, 84, 95, 20, 93, 136, 16, 48, 48, 85, 16, 47, 56, 60, 116, 96, 107, 54, 120, 133, 37, 28, 96, 120, 56, 34, 109, 41, 68, 49, 16, 18, 51, 84, 95, 20, 93, 136, 16, 48, 48, 85, 16, 47, 56, 60, 116, 96, 107, 54, 120, 133, 37, 28, 96, 120, 56, 34, 109, 41, 68, 49, 16, 18, 51, 84, 95, 20, 93, 136, 16, 48, 48, 85, 16, 47, 56, 60, 116, 96, 107, 54, 120, 133, 37, 28, 96, 120, 56, 34, 109, 41, 68]
S = [102, 99, 106, 136, 65, 50, 40, 68, 30, 2, 103, 125, 100, 20, 118, 113, 130, 66, 9, 68, 92, 91, 132, 86, 89, 90, 39, 70, 41, 2, 113, 89, 96, 119, 98, 121, 83, 32, 12, 68, 77, 126, 18, 78, 13, 57, 39, 108, 42, 110, 59, 60, 124, 62, 70, 130, 126, 44, 134, 105, 121, 52, 11, 115, 67, 103, 114, 50, 121, 107, 93, 74, 39, 33, 33, 41, 112, 20, 65, 101, 33, 91, 65, 134, 37, 114, 32, 130, 14, 2, 113, 18, 89, 101, 44, 61, 117, 65, 114, 114, 40, 71, 7, 30, 11, 28, 101, 106, 126, 65, 23, 100, 72, 22, 94, 31, 117, 63, 123, 53, 33, 97, 95, 112, 58, 104, 80, 80, 74, 87, 0, 9, 102, 130, 105, 55, 99]

# Warm-up calls to minimize initialization overhead
extract_flag_v1(H, S)
extract_flag_v2(H, S)

# Number of iterations for timing
iterations = 50

# Timing the first function
start_time_v1 = time.perf_counter()
for _ in range(iterations):
    result_v1 = extract_flag_v1(H, S)
end_time_v1 = time.perf_counter()
total_time_v1 = end_time_v1 - start_time_v1

# Timing the second function
start_time_v2 = time.perf_counter()
for _ in range(iterations):
    result_v2 = extract_flag_v2(H, S)
end_time_v2 = time.perf_counter()
total_time_v2 = end_time_v2 - start_time_v2

# Printing the results
print(f"First function result:  {result_v1}")
print(f"Second function result: {result_v2}")
print(f"Time taken by first function over {iterations} iterations: {total_time_v1:.6f} seconds")
print(f"Time taken by second function over {iterations} iterations: {total_time_v2:.6f} seconds")

if total_time_v1 > total_time_v2:
    print("Second function is faster.")
else:
    print("First function is faster.")
