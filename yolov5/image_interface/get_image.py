from selenium import webdriver
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
import os
import time

DOWNLOAD_PATH = os.path.abspath(os.path.dirname(__file__)) + '\\images\\'
prefs = {
    'profile.default_content_settings.popups': 0,  # 禁止弹窗选择下载路径的弹窗
    'download.default_directory': DOWNLOAD_PATH  # 设置下载路径
} 

url = 'http://192.168.1.184'  # 修改成esp32-cam设定的的local_IP

xpath_list = [
    '//*[@id="xclk"]',  # MHz input
    '//*[@id="set-xclk"]',  # MHz set
    '//*[@id="framesize"]/option[6]',  # resolution  640x480
    '//*[@id="toggle-stream"]',   # start stream
    '//*[@id="stream"]',  # image stream
    '//*[@id="save-still"]'  # save image
]

def get_img_from_cam(image_number=5, duration=1.0):
    """图片获取接口
    
    Parameters: 
    image_number: 获取图片的个数
    duration: 连续拍摄图片的间隔
    """
    chrome_options = Options()
    #chrome_options.add_argument('--headless')  # 无头浏览器 有bug
    chrome_options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    if not os.path.exists(DOWNLOAD_PATH):
        os.mkdir(DOWNLOAD_PATH)
    driver.get(url)

    # 设置分辨率等参数并显示图像
    wait.until(EC.presence_of_element_located((By.XPATH, xpath_list[0])))
    driver.find_element_by_xpath(xpath_list[0]).clear()  # 清空
    driver.find_element_by_xpath(xpath_list[0]).send_keys(30)  # 设置时钟频率
    clk = driver.find_element_by_xpath(xpath_list[0]).get_attribute('value')
    
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath_list[1])))
    driver.find_element_by_xpath(xpath_list[1]).click()

    wait.until(EC.element_to_be_clickable((By.XPATH, xpath_list[2])))
    driver.find_element_by_xpath(xpath_list[2]).click()
    resolution = driver.find_element_by_xpath(xpath_list[2]).text

    wait.until(EC.element_to_be_clickable((By.XPATH, xpath_list[3])))
    driver.find_element_by_xpath(xpath_list[3]).click()

    print('+--------显示配置---------+'.format(clk))
    print('| esp32-cam时钟频率:{}mHZ |'.format(clk))
    print('+-------------------------+')
    print('| 分辨率：{}   |'.format(resolution))
    print('+-------------------------+')

    time.sleep(3)  # 等待图片加载
    print('capturing......')
    wait.until(EC.presence_of_element_located((By.XPATH, xpath_list[4])))
    wait.until(EC.element_to_be_clickable((By.XPATH, xpath_list[5])))

    # 获取本次下载图片的起始索引
    try:
        file_list = sorted(os.listdir(DOWNLOAD_PATH), key=lambda x: int(re.findall(r'image(.*?).jpg', x)[0]))
        img_index = int(re.findall(r'image(.*?).jpg', file_list[-1])[0]) + 1
    except Exception as e:
        img_index = 1

    # 每隔一段时间下载一张图片
    for i in range(image_number):
        driver.find_element_by_xpath(xpath_list[5]).click()
        time.sleep(duration)
        
        # 修改图片名称为 image<index>.jpg
        img_name = driver.find_element_by_xpath(xpath_list[5]).get_attribute('download')
        old_path = DOWNLOAD_PATH + img_name
        new_path = DOWNLOAD_PATH + 'image{}.jpg'.format(img_index)
        os.rename(old_path, new_path)
        print('download image{}: {}'.format(i + 1, img_name))

        img_index += 1
    
    print('downloading completed')
    driver.quit()  # 关闭浏览器

if __name__ == '__main__':
    
    get_img_from_cam(5) # test