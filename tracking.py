from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time,os
from PIL import Image
from io import BytesIO
import itertools
import pyautogui
import numpy as np
import re
from tqdm import tqdm

# Interval between mouse movements (in seconds)
movement_interval = 60  # Move the mouse every 60 seconds



us_cities = [
    ('Austin','AUS'),
    ('Dallas','DFW'),
    ('San Francisco', 'SFO'),
    ('Los Angeles','LAX'),
    ('Chicago','ORD'),
    ('Houston','IAH'),
    # ('New York','EWR'),
    # ('New York','JFK'),
    ('Seattle','SEA'),
    ('Vancouver','YVR')
]

asia_cities = [
    ('Hong Kong','HKG'),
    ('Guangzhou','CAN'),
    ('Shanghai','SHA'),
    ('Seoul','ICN'),
    ('Tokyo','NRT'),
    ('Tokyo','HND'),
    ('Beijing','PEK'),
    ('Singapore','SIN')
]

# date_leave = [
#    '2023-12-16',
#    '2023-12-17',
#    '2023-12-18',
#    '2023-12-19',
#    '2023-12-20',
#    '2023-12-21',
#    '2023-12-22',
#    '2023-12-23',
#    '2023-12-24',
#    '2023-12-25',
#    '2023-12-26',
#    '2023-12-27',
#    '2023-12-28',
# ]

date_leave = [
   '2024-1-18',
   '2024-1-19',
   '2024-1-20',
   '2024-1-21',
   '2024-1-22',
   '2024-1-23',
   '2024-1-24',
   '2024-1-25',
   '2024-1-26',
   '2024-1-27',
   '2024-1-28',
   '2024-1-29',
]

# date_comeback = [
#     '2024-01-07',
#     '2024-01-06',
#     '2024-01-08',
#     '2024-01-09',
#     '2024-01-10',
#     '2024-01-11',
#     '2024-01-12',
#     '2024-01-13',
#     '2024-01-14',
#     '2024-01-15',
#     '2024-01-16',
#     '2024-01-17',
#     '2024-01-18',
#     '2024-01-19',
# ]

date_comeback = [
    '2024-02-17',
    '2024-02-18',
    '2024-02-19',
    '2024-02-20',
    '2024-02-21',
    '2024-02-22',
    '2024-02-23',
    '2024-02-24',
    '2024-02-25',
    '2024-02-26',
    '2024-02-27',
    '2024-02-28',
]

# cabin_class = ['business','economy']
cabin_class = ['business']

def keep_screen_active()->None:
    # Get the current mouse position
    current_x, current_y = pyautogui.position()

    # Simulate moving the mouse cursor slightly (1 pixel) to keep the screen active
    pyautogui.moveTo(current_x + 3, current_y + 3)

    # Pause for the specified interval
    # pyautogui.sleep(movement_interval)

def link_builder(departure:str,arrival:str,class_of_service:str,departure_date:str)->str:
    # return f'https://www.point.me/results?departureCity={departure[0]}&departureIata={departure[1]}&arrivalCity={arrival[0]}&arrivalIata={arrival[1]}&legType=oneWay&classOfService={class_of_service}&passengers=1&pid=&departureDate={departure_date}T06%3A00%3A00.000Z'
    return f'https://www.pointsyeah.com/search?airlineProgram=&arrival={arrival[1]}&bankpromotion=false&banks=&cabin=Business%20%26%20First&departDate={departure_date}&departDateSec={departure_date}&departure={departure[1]}&multiday=false&passenger=1&pointpromotion=false&tripType=1'
    
def wait_for_results() -> None:
    time.sleep(25)
    # while True:
    #     try:
    #         driver.find_element(By.XPATH,"//button[normalize-space()='Minimize']")
    #         time.sleep(5)
    #     except:
    #         while True:
    #             try:
    #                 driver.find_element(By.XPATH,"//button[normalize-space()='Maximize']")
    #             except:
    #                 break
    #         break


def click_to_sort_lowest_first()-> bool:
    try:
        sort_button = driver.find_element(By.CSS_SELECTOR,"div[id='headlessui-menu-button-:rg:'] div:nth-child(2)")
        sort_button.click()
        lowest_button = driver.find_element(By.XPATH,"//div[normalize-space()='Points Low to High']")
        lowest_button.click()
        return True
    except:
        return False
    
def click_to_filter_business_higher_60()-> bool:
    try:
        cabin_percentage_button = driver.find_element(By.XPATH,"//div[contains(text(),'Premium Cabin Percentage')]")
        cabin_percentage_button.click()
        time.sleep(3)
        higher_60_button = driver.find_element(By.XPATH,"//input[@value='60']")
        higher_60_button.click()
        return True
    except:
        return False

def get_duration_points():
    point_list = []
    duration_list = []
    stop_list = []
    pts_list = driver.find_elements(By.CLASS_NAME,'pts-miles')
    duration_stop_list = driver.find_elements(By.CLASS_NAME,'duration-stop')
    for pts, duration_stop in zip(pts_list,duration_stop_list):
        pts = int(pts.text.replace('pts', '').replace(',',''))
        if pts > 150000:
            continue
        
        if 'Nonstop' in duration_stop.text:
            stop = 0
        else:
            stop = duration_stop.text.split('-')[1]
            stop = int((re.findall(r'\d+', stop))[0])
        if stop >2: 
            continue
        
        point_list.append(pts)
        stop_list.append(stop)
        duration_list.append(duration_stop.text.split('-')[0])
    if len(point_list) == 0:
        return None
    flight_info = np.array([point_list,stop_list,duration_list])
    return np.transpose(flight_info)
        
        

os.system('pkill Goole Chrome')

# Get the current time as a struct_time object
current_time_struct = time.localtime()

# Format the current time as a string using strftime
formatted_time = time.strftime("%Y_%m_%d_%H_%M_%S", current_time_struct)

results_path = f"/Users/xianggao/Downloads/flight/{formatted_time}"
os.mkdir(results_path)

options = webdriver.ChromeOptions()
options.add_argument("--verbose")
# options.add_argument('--headless')
options.add_argument("user-data-dir=/Users/xianggao/Downloads/chrome_profile/Default")
driver = webdriver.Chrome(options=options)

flight_info_summary = np.array(['points','stop','duration','depature','arrival','date','link'])
driver.get('https://www.pointsyeah.com/search?airlineProgram=&arrival=HKG&bankpromotion=false&banks=&cabin=Business%20%26%20First&departDate=2024-1-24&departDateSec=2024-1-24&departure=DFW&multiday=false&passenger=1&pointpromotion=false&tripType=1')


print("seach U.S. to Asia")
print(f"total flights to search: {len(list(itertools.product(us_cities,asia_cities,date_leave,cabin_class)))}")
for depature,arrival,date,class_of_service in tqdm(list(itertools.product(us_cities,asia_cities,date_leave,cabin_class)), desc="Processing"):
    keep_screen_active()
    screenshot_path = f'{results_path}/{depature[1]}_{arrival[1]}_{date}_{class_of_service}.png'
    driver.get(link_builder(depature,arrival,class_of_service,date))
    click_to_filter_business_higher_60()
    wait_for_results()
    flight_info = get_duration_points()
    if isinstance(flight_info, np.ndarray):
        depature_column = np.full((flight_info.shape[0], 1), depature[0])
        arrival_column = np.full((flight_info.shape[0], 1), arrival[0])
        date_column = np.full((flight_info.shape[0], 1),date)
        link_column = np.full((flight_info.shape[0],1),link_builder(depature,arrival,class_of_service,date))
        flight_info = np.hstack((flight_info,depature_column))
        flight_info = np.hstack((flight_info,arrival_column))
        flight_info = np.hstack((flight_info,date_column))
        flight_info = np.hstack((flight_info,link_column))
        print(flight_info)
        flight_info_summary = np.vstack((flight_info_summary,flight_info))
        np.savetxt(f'{results_path}/flight_summary.csv',flight_info_summary,delimiter=',' ,comments='', fmt='%s')

print("seach asia to U.S.")
print(f"total flights to search: {len(list(itertools.product(asia_cities,us_cities,date_comeback,cabin_class)))}")
for depature,arrival,date,class_of_service in tqdm(list(itertools.product(asia_cities,us_cities,date_comeback,cabin_class)), desc="Processing",unit=' fligth'):
    keep_screen_active()
    driver.get(link_builder(depature,arrival,class_of_service,date))
    click_to_filter_business_higher_60()
    wait_for_results()
    flight_info = get_duration_points()
    if isinstance(flight_info, np.ndarray):
        depature_column = np.full((flight_info.shape[0], 1), depature[0])
        arrival_column = np.full((flight_info.shape[0], 1), arrival[0])
        date_column = np.full((flight_info.shape[0], 1),date)
        link_column = np.full((flight_info.shape[0],1),link_builder(depature,arrival,class_of_service,date))
        flight_info = np.hstack((flight_info,depature_column))
        flight_info = np.hstack((flight_info,arrival_column))
        flight_info = np.hstack((flight_info,date_column))
        flight_info = np.hstack((flight_info,link_column))
        print(flight_info)
        flight_info_summary = np.vstack((flight_info_summary,flight_info))
        np.savetxt(f'{results_path}/flight_summary.csv',flight_info_summary,delimiter=',', comments='', fmt='%s')
 


np.savetxt(f'{results_path}/flight_summary.csv',flight_info_summary,delimiter=',', comments='', fmt='%s')