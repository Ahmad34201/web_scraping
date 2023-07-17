import random
from polynomial import Polynomial


class DataStorage:
    def __init__(self, n, p, k):
        self.n = n
        self.prime = p
        self.k = k
        self.boolean_array = [False] * n
        self.random_numbers = self.generate_random_numbers()

    def generate_random_numbers(self):
        return random.sample(range(1, self.prime), self.k)

    def process_string(self, s):
        indices = []
        p = Polynomial.ascii_from_string(s)

        for number in self.random_numbers:
            result = p.solve(number, self.prime)
            indices.append(result)

        return indices

    def store(self, s):
        indices = self.process_string(s)
        for index in indices:
            if 0 <= index < self.n:
                self.boolean_array[index] = True

    def is_stored(self, s):
        indices = self.process_string(s)

        return all(0 <= index < self.n and self.boolean_array[index] for index in indices)


data = DataStorage(10, 23, 3)
data.store('hello')

print("Result:", data.is_stored('hello'))
print("Result:", data.is_stored('world'))
