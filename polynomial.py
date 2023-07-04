
# Calculating the Power by using modulo operator
def fast_power(base, power):
    power_result = 1
    MODULE_PRIME = 831121
    while (power > 0):
        if ((power % 2) != 0):
            power_result = (power_result * base % MODULE_PRIME) % MODULE_PRIME

        base = ((base % MODULE_PRIME) * (base % MODULE_PRIME)) % MODULE_PRIME
        power = power >> 1
    return power_result

# Function to get result for string polynomial
def get_polynomial(string_to_convert, multiplier_x):
    polynomial_result = 0
    MODULE_PRIME = 831121    

    for power_of_x, character in enumerate(list(string_to_convert[::-1])):
        polynomial_result = ((polynomial_result % 831121) +
                             (ord(character)*(fast_power(multiplier_x, power_of_x))) % MODULE_PRIME) % MODULE_PRIME
    print("Final output is ", polynomial_result)
    return polynomial_result


get_polynomial("hello", 42098)
