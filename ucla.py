from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv, dotenv_values
#import keys
import schedule
import time

def send_UCLA_food():
    load_dotenv()
    url = "https://menu.dining.ucla.edu/Menus/Rieber/Dinner"
    result = requests.get(url)
    doc = BeautifulSoup(result.text,"html.parser")

    sectionTags = doc.find_all('li', class_='sect-item')
    date_of_menu = doc.find(id='page-header').text.strip()

    menu = [f"**{date_of_menu}**\n"]

    for sectionTitle in sectionTags:
        menuItems = sectionTitle.find_all('a', class_='recipelink') # finds all the a tags with the recipe
        menu.append(f"**{sectionTitle.contents[0].strip()}:**")
        for dishes in menuItems:
            menu.append(f"- {dishes.contents[0].strip()}")

    msg = "\n".join(menu)
    print(msg)

    dining_hall_data = {
        "content": msg
    }

    response = requests.post(os.getenv("WEBHOOK_URL"),data=dining_hall_data)

    if response.status_code == 204:
        print("Msg sent successfully")
    else:
        print(f"Failed to send message")



schedule.every().day.at("00:02").do(send_UCLA_food)

while True:
    schedule.run_pending()
    time.sleep(1)