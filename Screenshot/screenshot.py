from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import os
from random import randint
from gtts import gTTS
  
def readableNumber(number:int)->str:
    if number < 1000:
        return str(number)
    elif number < 1000000:
        return str(round(number/1000, 1))+'k'
    elif number < 1000000000:
        return str(round(number/1000000, 1))+'M'


def saveAudio(texts:list, destination:str, baseName:str):
    for text in range(len(texts)):
        try:
            if texts[text] != '':
                audio = gTTS(text=texts[text]+".", lang="en-us")
                audio.save(destination+"/"+baseName+str(text+1)+".mp3")
        except:
            print(texts[text])


def prepare(data:str, outputFolder:str, questionTemplate:str, commentTemplate):
    # create webdriver object
    if not os.path.isdir(outputFolder):
        os.mkdir(outputFolder)

    with open(data, "r") as datafile:
        postdata = json.load(datafile)
        questiondata = postdata['question']
        title = questiondata['title']
        author = 'u/'+questiondata['author']
        votes = questiondata['votes']
        comments = questiondata['comments']
        posted = "  "+ str(randint(3, 23)) + "hours ago"
        commenter = 'u/'+postdata['author']
        upvotes = readableNumber(postdata['upvotes'])

    driver = webdriver.Chrome("chromedriver.exe")
    driver.get(questionTemplate)
    # get element 


    title = title.replace('"', "'")

    driver.execute_script(f'document.getElementById("UserInfoTooltip--t3_w4h959").innerText = "{str(author)}"')
    driver.execute_script(f'document.getElementsByClassName("_3a2ZHWaih05DgAOtvu6cIo")[0].innerText = "{str(votes)}"')
    driver.execute_script(f'document.getElementsByClassName("FHCV02u6Cp2zYL0fhQPsO")[0].innerText = "{str(comments)}"')
    driver.execute_script(f'document.getElementsByClassName("_2VF2J19pUIMSLJFky-7PEI")[0].innerText = "{str(posted)}"')
    driver.execute_script(f'document.getElementsByTagName("h3")[0].innerText = "{str(title)}"')
    # changing the data 

    dest = outputFolder+"/Question "+data.split("/")[-1].replace('.json', '.png')
    # getting the output file name 

    element = driver.find_element(By.XPATH, '//*[@id="AppRouter-main-content"]/div/div/div[2]/div/div[2]/div')
    element.screenshot(dest)
    # click screenshot 


    driver.get(commentTemplate)
    # getting the comments 

    comment = postdata["body"].replace('"', "'").split(".")
    cmnt = ""
    for c in range(len(comment)):
        if comment[c] != '':
            cmnt += comment[c] + "."
            driver.execute_script(f'document.getElementsByClassName("_3QEK34iVL1BjyHAVleVVNQ")[0].getElementsByClassName("_23wugcdiaj44hdfugIAlnX ")[0].innerText = "{str(commenter)}"')
            driver.execute_script(f'document.getElementsByClassName(\'_1qeIAgB0cPwnLhDF9XSiJM\')[0].innerText = "{str(cmnt)}"')
            driver.execute_script(f'document.getElementsByClassName("_3ChHiOyYyUkpZ_Nm3ZyM2M")[0].innerText = "{str(upvotes)}"')
            driver.execute_script(f'document.getElementsByClassName("_3yx4Dn0W3Yunucf5sVJeFU")[0].innerText = "{str(posted)}"')
            # modifying the data 

            e = driver.find_element(By.XPATH, '//*[@id="overlayScrollContainer"]/div[1]/div/div[2]/div')
            e.screenshot(dest.replace("Question ", "Comment "+str(c+1)+"  "))
        # click screenshot 

    driver.close()
    # # closing the browser 
    print("[IMAGES PROCESS] Image processing complete")

    saveAudio(comment, outputFolder, "CommentAudio")
    saveAudio([title], outputFolder, "QuestionAudio")
    print("[Audio PROCESS] Audio processing complete")


prepare("../Data/62d8f81419d070eb729ba8a0.json", "Tests", "D:\projects\Scrapers\AskReddit\Screenshot\CommentTemplate.html", "D:\projects\Scrapers\AskReddit\Screenshot\CommentTemplate.html")