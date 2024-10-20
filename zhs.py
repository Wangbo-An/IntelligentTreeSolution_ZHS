import numpy as np
import os, time, cv2, sys
import onnxruntime as orc
import selenium.webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from  selenium.webdriver.support import expected_conditions as EC

class treeSolution:
    def __init__(self, username:str, mm:str) -> None:
        
        options = wb.EdgeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = wb.Edge(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.set_window_size(1200, 800)
        self.driver.get('https://onlineweb.zhihuishu.com/onlinestuh5')
        self.net = orc.InferenceSession("best.onnx")
        self.action = ActionChains(self.driver)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="lUsername"]'))).send_keys(str(username))
        self.driver.find_element(By.XPATH, '//*[@id="lPassword"]').send_keys(str(mm))
        self.driver.find_element(By.XPATH, '//*[@id="f_sign_up"]/div[1]/span').click()
        time.sleep(0.5)
        while self.passCaptia(): pass
        if self.wait.until(lambda driver: self.driver.current_url == 'https://onlineweb.zhihuishu.com/onlinestuh5'):
            print("登入成功".center(60, '-'))
            time.sleep(0.5)
            classes = self.toGetClass()
            self.autoPlay(classes)
        else:
            try:
                if self.driver.find_element(By.XPATH, '//*[@id="form-ipt-error-l-username"]').text == '手机号或密码错误':
                    print("手机号或密码错误!")
            except: pass

    def autoPlay(self, classes_url:list=[]):
        
        if len(classes_url) != 0: 
            for url in classes_url:
                self.driver.get(url)
                time.sleep(1.5)
                self.startPlay()
        y_n = input("是否播放指定地址课程:[y/n]")
        if y_n.lower() == 'y':
            pointed_url = input("输入指定课程地址:")
            print("播放指定课程:", pointed_url)
            self.driver.get(pointed_url)
            time.sleep(1.5)
            self.startPlay()
        self.driver.quit()
        input("over...")

    def startPlay(self):

        self.errorCheck()
        self.driver.minimize_window()
        print("开始学习".center(60, '-'))
        uls = self.driver.find_elements(By.TAG_NAME, 'ul')
        true_uls = [x for x in uls if x.get_attribute('class') == "list"]
        for ul in true_uls:
            classes = ul.find_elements(By.TAG_NAME, 'li')[: -1]
            self.errorCheck()
            print("-" * 50)
            for per_class in classes:
                self.errorCheck()
                if len(per_class.text.split()) <= 2: print(' '.join(per_class.text.split()), end=" ")
                else: print(' '.join(per_class.text.split()[: -1]), end=" ")
                try:
                    A = len(per_class.find_elements(By.CLASS_NAME, 'time_ico_half'))
                    B = len(per_class.find_elements(By.CLASS_NAME, 'time_icofinish'))
                    if A == 0 or A == B:
                        print("完成")
                        break
                    per_class.click()
                    time.sleep(1)
                    while True:
                        while not self.speedChange():
                            self.errorCheck()
                except: pass
        print("学习结束".center(60, '-'))

    def passCaptia(self):

        bytes = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bgimg'))).screenshot_as_png
        img = cv2.imdecode(np.frombuffer(bytes, dtype=np.uint8), 1)
        h, w = img.shape[:-1]
        input_name = self.net.get_inputs()[0].name  
        output_name = self.net.get_outputs()[0].name 
        img_c = cv2.resize(img, (640, 640))
        img_c = img_c.astype(np.float32) / 255
        img_c = img_c.transpose([2, 0, 1])[None,]
        result = self.net.run([output_name], {input_name: img_c})[0][0].transpose([1, 0])
        boxes, conf = [], []
        for layer in result:
            score = layer[-1]
            if score > 0.05:
                x_c, y_c, w1, h1 = (layer[:-1] / 640) * np.array([w, h, w, h])
                x = x_c - w1 // 2
                y = y_c - h1 // 2
                boxes.append((x, y, w1, h1))
                conf.append(score)
        index = cv2.dnn.NMSBoxes(boxes, conf, score_threshold=0.5, nms_threshold=0.4)
        try:
            index = index[0] if len(index) > 0 else 0
            x, y, w, h = np.int_(boxes[index])
        except: x = 10
        e = self.driver.find_element(By.XPATH, '/html/body/div[33]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/img[2]')
        self.action.click_and_hold(e).perform()
        self.action.move_by_offset(xoffset=x+8, yoffset=0).perform()
        self.action.release().perform()
        time.sleep(0.3)
        if len(self.driver.find_elements(By.CLASS_NAME, 'yidun_modal__title')):
            time.sleep(0.5)
            return True
        else: return False

    def speedChange(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'videoArea'))).click()
            time.sleep(0.3)
            self.driver.find_element(By.XPATH, '//*[@id="vjs_container"]/div[10]/div[9]').click()
            self.driver.find_element(By.XPATH, '//*[@id="vjs_container"]/div[10]/div[9]/div/div[1]').click()
            return True
        except: 
            return False

    def errorCheck(self):
        try:
            self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/div[3]/span/button').click()
            self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[6]/div[2]/div[1]/i').click()
        except: 
            try:
                self.driver.find_elements(By.CLASS_NAME, 'item-topic')[1].click()
                self.driver.find_element(By.XPATH, '//*[@id="playTopic-dialog"]/div/div[3]').click()
                self.driver.find_element(By.XPATH, '/html/body/div[5]/div/div[1]/button/i').click()
            except: pass
    
    def toGetClass(self):
        
        classes_url = []
        parent = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="sharingClassed"]/div[2]')))
        classes = parent.find_elements(By.TAG_NAME, 'ul')
        print(f'目前还需要上{len(classes)}节课.')

        for element in classes:
            course_name = element.find_element(By.CLASS_NAME, 'courseName')
            print(course_name.text, end=" ")
            try:
                not_start = element.find_elements(By.CLASS_NAME, 'no-start-msk')
                if len(not_start) == 1: print('尚未开始 跳过')
            except:
                print('已添加至播放列表')
                classes_url.append(course_name)
            
        return classes_url

def login():
    username = input("输入手机号:")
    mm = input("输入密码:")
    y_n = input("是否保存用户:[y/n]")
    if y_n.lower() == 'y':
        log = open("user.txt", '+w')
        log.write(username + '\n')
        log.write(mm)

    treeSolution(username, mm)

if __name__ == "__main__":
    if os.path.exists('user.txt'):
        if len(sys.argv) > 1 and sys.argv[1: ][0] == "-y":
            y_n = 'y'
        else:
            y_n = input("发现已有用户, 是否选择登入:[y/n]")
        if y_n.lower() == 'y':
            log = open("user.txt", 'r')
            username = log.readline().strip()
            mm = log.readline().strip()
            treeSolution(username, mm)
        else:
            login()
    else:
        login()
        