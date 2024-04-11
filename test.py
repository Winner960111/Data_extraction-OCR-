from datetime import datetime

birthday_text = "16 Mar 2021"
birthday_date = datetime.strptime(birthday_text, '%d %b %Y')

formatted_birthday = birthday_date.strftime('%d/%m/%Y')

print(formatted_birthday)