import re

email_addresses = [
    "ahmed_ali@arbisoft.com",
    "ahmed2@gmail.com",
    "ali@yahoo.com",
    "name@domain.com"
]


def get_username_domain(email):
    pattern = r'^([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$'
    match = re.match(pattern, email)
    if match:
        print("Username ", match[1])
        print("Domain ", match[2])


for email in email_addresses:
    get_username_domain(email)
