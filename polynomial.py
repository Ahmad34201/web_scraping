
class Polynomial:

    def __init__(self, s):
        self.s = s

    # Calculating the Power by using modulo operator
    def fast_power(self, base, power, module_prime):
        power_result = 1
        while (power > 0):
            if ((power % 2) != 0):
                power_result = (power_result * base %
                                module_prime) % module_prime

            base = ((base % module_prime) * (base %
                    module_prime)) % module_prime
            power = power >> 1
        return power_result

    # Function to get result for string polynomial

    def get_polynomial(self, string_to_convert, multiplier_x, module_prime):
        polynomial_result = 0

        for power_of_x, character in enumerate(list(reversed(string_to_convert))):
            polynomial_result = ((polynomial_result % module_prime) +
                                 (ord(character)*(self.fast_power(multiplier_x, power_of_x, module_prime))) % module_prime) % module_prime

        return polynomial_result

    def solve(self, x, prime):
        polynomial = self.get_polynomial(self.s, x, prime)
        print("Final output is ", polynomial)


MODULE_PRIME = int(input("Enter a prime number\n"))
polynomial = Polynomial('hello')
polynomial.solve(42098, MODULE_PRIME)
