import numpy as np
from fuzzywuzzy import fuzz
from paddleocr import PaddleOCR
import selenium.webdriver as wb
import os, time, cv2, json, logging, re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from  selenium.webdriver.support import expected_conditions as EC

logging.disable(logging.DEBUG | logging.WARNING)
class questMoudle:

    def __init__(self, driver: wb.Edge) -> None:
        super().__init__()

        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True)
        self.js = None
        
    def startAnswer(self, toPlay):
        
        if self.driver.current_url != "https://onlineweb.zhihuishu.com/onlinestuh5":
            self.driver.get("https://onlineweb.zhihuishu.com/onlinestuh5")
        time.sleep(1.5)
        className = toPlay.find_element(By.CLASS_NAME, 'courseName')
        courseName = className.text
        if os.path.exists(f"data/{courseName}.json"):
            self.js = json.load(open(f"data/{courseName}.json", encoding="utf-8"))
            print(courseName + "题库已加载完成")
            toPlay.find_elements(By.CLASS_NAME, "course-menu-w")[1].click()
            time.sleep(2)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            tmp_url = self.driver.current_url
            ok = self.wait.until(EC.presence_of_element_located((By.ID, 'examStateTabWsj')))
            time.sleep(0.5)
            charpters = self.driver.find_elements(By.CLASS_NAME, 'examItemWrap')
            charpters = [x for x in charpters if x.find_element(By.CLASS_NAME, 'percentage_number').text in ["作业"]]
            if len(charpters) == 0: print("所有单元测试均已完成".center(54, '-'))
            for index in range(len(charpters)): # ?
                self.driver.switch_to.window(self.driver.window_handles[-1])
                time.sleep(1)
                if self.driver.current_url != tmp_url:
                    self.driver.get(tmp_url)
                    time.sleep(3)
                charpters = self.driver.find_elements(By.CLASS_NAME, 'examItemWrap')
                charpters = [x for x in charpters if x.find_element(By.CLASS_NAME, 'percentage_number').text in ["作业"]]
                charpters[0].find_element(By.CLASS_NAME, "themeBg").click()
                time.sleep(1.5)
                self.driver.switch_to.window(self.driver.window_handles[-1])
                time.sleep(1.5)
                problems = self.driver.find_elements(By.CLASS_NAME, "subject_type_describe")
                for index in range(len(problems)):
                    img_btyes = problems[index].screenshot_as_png
                    img = cv2.imdecode(np.frombuffer(img_btyes, np.uint8), 1)
                    results = self.ocr.ocr(img)
                    txt = ''
                    for result in results[0][1: ]:
                        txt += result[-1][0]
                    txt = re.sub(r"[、】（）()【。，·？！：“”：；,.?';:~\!`]", '', txt)
                    arg = self.similarityCalc(txt, self.js)
                    true_answer = self.js[list(self.js.keys())[arg]]
                    answers_box = self.driver.find_elements(By.CLASS_NAME, 'subject_node')[index]
                    answers = answers_box.find_elements(By.CLASS_NAME, 'nodeLab')
                    answers_dic = {v:k for k,v in enumerate([x.text for x in answers])}
                    if type(true_answer) == str:
                        arg = self.similarityCalc(true_answer, answers_dic)
                        answers[arg].click()
                    elif type(true_answer) == int:
                        if true_answer == 0:
                            arg = self.similarityCalc("错", answers_dic)
                            answers[arg].click()
                        else:
                            arg = self.similarityCalc("对", answers_dic)
                            answers[arg].click()
                    else:
                        args = []
                        for item in true_answer:
                            args.append(self.similarityCalc(item, answers_dic))
                        for arg in args:
                            answers[arg].click()
                    self.driver.find_elements(By.CLASS_NAME, 'el-button--primary')[-1].click()
                    time.sleep(1)
                self.driver.find_element(By.CLASS_NAME, 'btnStyleXSumit').click()
                time.sleep(1.5)
                self.driver.find_elements(By.CLASS_NAME, 'el-button--default')[-1].click()
                time.sleep(0.5)
                self.driver.close()
        else:
            print("暂未有该门课程答案 停止作答.")

    def similarityCalc(self, txt:any, dic:dict):

        scores = []
        for question in dic.keys():
            score = fuzz.partial_ratio(question, txt)
            scores.append(score)
        arg = np.array(scores).argmax()

        return arg
