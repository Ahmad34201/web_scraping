
class Polynomial:

    def __init__(self, coefficients):
            self.coefficients = coefficients

    @classmethod
    def ascii_from_string(cls, input_string):
        ascii_list = []
        for char in input_string:
            ascii_list.append(ord(char))
        return cls(ascii_list)


    def extract_coefficients(self, polynomial_string):
        for character in reversed(polynomial_string):
            self.coefficients.append(ord(character))
        return self.coefficients

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

    def get_polynomial(self, multiplier_x, module_prime):
        polynomial_result = 0

        for power_of_x, cooef in enumerate(self.coefficients):
            polynomial_result = ((polynomial_result % module_prime) +
                                 (cooef * (self.fast_power(multiplier_x, power_of_x, module_prime))) % module_prime) % module_prime

        return polynomial_result

    def solve(self, x, prime):
        polynomial = self.get_polynomial(x, prime)
        print("Final output is ", polynomial)


MODULE_PRIME = int(input("Enter a prime number\n"))
# polynomial = Polynomial([104, 101, 108, 108, 111])
polynomial = Polynomial.ascii_from_string('hello')
polynomial.solve(42098, MODULE_PRIME)
polynomial.solve(30098, MODULE_PRIME)

