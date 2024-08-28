from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv, dotenv_values
#import keys
import schedule
import time
import json


def split_message(msg, max_length):
    #Split the message into chunks of a maximum length
    return [msg[i:i+max_length] for i in range(0, len(msg), max_length)] #returns a list of our split up strings that are only up to 2000 characters long

def check_Response(response):
     if response.status_code == 204:
        print("Msg sent successfully")
     else:
        print(f"Failed to send message {response.status_code} {response.text}")


def bruin_plate():
    load_dotenv()
    url = "https://menu.dining.ucla.edu/Menus/BruinPlate/Today"
    try:

        result = requests.get(url)
        result.raise_for_status()
    except requests.RequestException as e:
        print(f"Error getting menu")
        return
    doc = BeautifulSoup(result.text,"html.parser")



    date_of_menu = doc.find(id='page-header').text.strip() 

    all_three_menus = doc.find_all('div', class_=['menu-block','third-col']) 
    menu = [f"\n**{date_of_menu}**\n"]

    
    for menusss in all_three_menus:
        type_of_meal = menusss.find('h3',class_='col-header').text.strip()
        menu.append(f"\n**{type_of_meal}**\n")
        section_tags = menusss.find_all('li',class_='sect-item')
        for section_title in section_tags:
            menu_items = section_title.find_all('a', class_='recipelink') 
            menu.append(f"**{section_title.contents[0].strip()}:**")
            for dishes in menu_items:
                menu.append(f"- {dishes.contents[0].strip()}")
        

    msg = "\n".join(menu)

    dining_hall_data = {
        "content": msg
    }
    
    
    
    max_length = 2000
    if int(len(json.dumps(dining_hall_data))> max_length): #splits our message since bruin plate contains over the max 2k characters
        messages = split_message(msg,max_length)
        for message in messages:
            dining_hall_data["content"] = message

            response = requests.post(os.getenv("WEBHOOK_URL"),data=dining_hall_data)
            check_Response(response)

           
    else:
        response = requests.post(os.getenv("WEBHOOK_URL"),data=dining_hall_data)
        check_Response(response)


def rieber_food():
    load_dotenv()
    url = "https://menu.dining.ucla.edu/Menus/Rieber/Today"
    try:

        result = requests.get(url)
        result.raise_for_status()
    except requests.RequestException as e:
        print(f"Error getting menu")
        return
    doc = BeautifulSoup(result.text,"html.parser")


    date_of_menu = doc.find(id='page-header').text.strip()

    all_three_menus = doc.find_all('div', class_=['menu-block','third-col']) #breakfast,lunch,dinner
    menu = [f"**{date_of_menu}**\n"]



    for menusss in all_three_menus: #For each meal of the day, add its header into the list and all the categories of food and all their subsequent items into the list
        type_of_meal = menusss.find('h3',class_='col-header').text.strip()
        menu.append(f"\n**{type_of_meal}**\n")
        section_tags = menusss.find_all('li',class_='sect-item')
        for section_title in section_tags:
            menu_items = section_title.find_all('a', class_='recipelink') # finds all the "a" tags with the recipe or all items listed under the sectiontitle
            menu.append(f"**{section_title.contents[0].strip()}:**") #add category/section title
            for dishes in menu_items: #add all item under the category 
                menu.append(f"- {dishes.contents[0].strip()}")
        


        

    msg = "\n".join(menu) #formatting for the entire list 

    dining_hall_data = {
        "content": msg
    }
    print(len(json.dumps(dining_hall_data)))


    response = requests.post(os.getenv("WEBHOOK_URL"),data=dining_hall_data) #sends data to discord

    check_Response(response)




schedule.every().day.at("16:27").do(rieber_food)
schedule.every().day.at("16:27").do(bruin_plate)


while True:
    schedule.run_pending()
    time.sleep(1)