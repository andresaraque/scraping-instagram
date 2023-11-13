import os
import wget
import pickle # for cookies
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from config_ig import *


def LaunchChrome():
  
  options = Options()
  user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"
  options.add_argument(f"user-agent={user_agent}")
  # options.add_argument("--headless") # without chrome window
  # options.add_argument(f"--window-size=970,1080")
  options.add_argument("--start-maximized")
  options.add_argument("--disable-web-security")
  options.add_argument("--disable-extensions")
  options.add_argument("--disable-notifications")
  options.add_argument("--ignore-certificate-errors")
  options.add_argument("--no-sandbox")
  options.add_argument("--log-level=3")
  options.add_argument("--allow-running-insecure-content")
  options.add_argument("--no-default-browser-check")
  options.add_argument("--no-first-run")
  options.add_argument("--no-proxy-server")
  options.add_argument("--disable-blink-features=AutomationControlled")
  options.add_argument("--disable-features=ChromeEOLPowerSaveMode")
  options.add_argument("--disable-features=CalculateNativeWinOcclusion")
  
  excludeOpt = [
    'enable-automation',
    'ignore-certificate-errors',
    'enable-logging',
    'disable-infobars'
  ]
  options.add_experimental_option('excludeSwitches', excludeOpt)

  prefs = {
    'profile.default_content_setting_values.notifications': 2,
    'intl.accept_languages': ['es-ES', 'es'], #it is in spanish, change for your language
    'credentials_enable_service': False
  }
  options.add_experimental_option('prefs', prefs)
  driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))
  return driver

def login_instagram():
  cookie_name_file = "instagram.cookies"

  #########################
  # LOGIN FROM COOKIES
  #########################

  print('Login by cookies')
  if (os.path.isfile(cookie_name_file)):
    cookies = pickle.load(open(cookie_name_file, 'rb'))

    driver.get('https://www.instagram.com/robots.txt')
    
    for cookie in cookies:
      driver.add_cookie(cookie)
    driver.get('https://www.instagram.com')
      # Validate if feed exists
    driver.find_element(By.XPATH, "//*[name()='svg'][@aria-label='Like']").click()
    return 'ok'

  #########################
  # LOGIN FROM SCRATCH
  #########################
  print('Login from scratch')
  driver.get('https://www.instagram.com')

  driver.find_element(By.NAME, "username").send_keys(USER_IG)
  driver.find_element(By.NAME, "password").send_keys(PASS_IG)
  driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

  #--------------------
  # if you have 2fa, shoud know that it's no implemented (or do it manually) :(
  #--------------------

  driver.find_element(By.XPATH, "//button[text()='Save Info']").click()
  
  # Validate that the feed exists
  driver.find_element(By.XPATH, "//*[name()='svg'][@aria-label='Like']").click()

  #save cookies on file
  cookies = driver.get_cookies()
  pickle.dump(cookies, open(cookie_name_file, "wb"))
  return 'ok'

def download_photos(hashTag):

  print('Search by #')
  driver.get(f'https://www.instagram.com/explore/tags/{hashTag}')
  try:
    number_posts = driver.find_element(By.CSS_SELECTOR, "._ac2a > span").text.replace(",", "")
  except NoSuchElementException:
    print(' ERROR: No posts found with that hashtag')
    return "error"
    
  url_photos = set()

  # On a computer, the maximum posts we can see are 28
  while len(url_photos) < (28 if float(number_posts) > 28 else float(number_posts)):
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    elements = driver.find_elements(By.CSS_SELECTOR, "div._aagv")
    
    for el in elements:
      url = el.find_element(By.CSS_SELECTOR, "img").get_attribute('src')
      url_photos.add(url)
    print(f'Number of photos: {len(url_photos)}')
  if os.path.exists(f'assets/{hashTag}/'):
    print(' ERROR: The folder with that hashtag already exists')
    return "error"
  else:
    os.mkdir(f'assets/{hashTag}/')
  n = 0
  for url_photo in url_photos:
    n+= 1
    print(f'Download: {n} of {len(url_photos)}')
    name_file = wget.download(url_photo, f'assets/{hashTag}/')
    print(f'\33[k Download: {name_file}]')
    print()
  

#########################
# -------- MAIN ---------
#########################
if __name__ == '__main__':
  driver = LaunchChrome()
  driver.implicitly_wait(8)

  #Login
  res = login_instagram()
  
  # Search for the hashtag you want to search for
  download_photos('treksupercaliber')

  driver.quit()