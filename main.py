from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import env
import config

# Define the list of problems and initialize problem_stats dictionary
problem_list = {str(problem["id"]): problem["title"] for problem in config.problems["week1"]}
problem_stats = {problem_id: {'title': title, 'submissions': {member: {'attempts': 0, 'correct': 0, 'incorrect': 0} for member in config.members.values()}} for problem_id, title in problem_list.items()}

# User credentials
user_id = env.user_id
user_pw = env.user_pw

# Setting up the Chrome driver
CHROME_DRIVER_PATH = './chromedriver.exe'
service = Service(executable_path=CHROME_DRIVER_PATH)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# Navigate to the login page and log in
driver.get('https://www.acmicpc.net/login')
username = driver.find_element('name', 'login_user_id')
username.send_keys(user_id)

password = driver.find_element('name', 'login_password')
password.send_keys(user_pw)

auto_login_button = driver.find_element('name', 'auto_login')
auto_login_button.click()

login_button = driver.find_element('id', 'submit_button')
login_button.click()


while driver.current_url == 'https://www.acmicpc.net/login':
    time.sleep(1)

# Navigate to the status page
driver.get('https://www.acmicpc.net/status?group_id=19681')

# Process multiple pages
for i in range(1):
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    submission_table = soup.find('table', id='status-table')

    # Extract submission data
    for row in submission_table.find_all('tr')[1:]:
        cols = row.find_all('td')
        submission_data = {
            '제출 번호': cols[0].text.strip(),
            '아이디': cols[1].text.strip(),
            '문제': cols[2].text.strip(),
            '결과': cols[3].text.strip(),
            '메모리': cols[4].text.strip(),
            '시간': cols[5].text.strip(),
            '언어': cols[6].text.strip(),
            '코드 길이': cols[7].text.strip(),
            '제출한 시간': cols[8].text.strip(),
        }

        problem_id = submission_data['문제']
        user_id = submission_data['아이디']
        if problem_id in problem_stats and user_id in config.members:
            member_name = config.members[user_id]
            problem_stats[problem_id]['submissions'][member_name]['attempts'] += 1
            if submission_data['결과'] == '맞았습니다!!':
                problem_stats[problem_id]['submissions'][member_name]['correct'] += 1
            elif submission_data['결과'] in ["출력 형식이 잘못되었습니다", "틀렸습니다", "시간 초과", "메모리 초과", "출력 초과", "런타임 에러", "컴파일 에러"]:
                problem_stats[problem_id]['submissions'][member_name]['incorrect'] += 1

    # Navigate to the next page
    next_button = driver.find_element('id', 'next_page')
    next_button.click()

# Close the browser
driver.quit()

# Print the summary
print("Problem Statistics:\n")
for problem_id, info in problem_stats.items():
    print(f"Problem ID: {problem_id} - {info['title']}")
    print("  Member :   Attempts\t|    Correct\t|   Incorrect")
    for member, stats in info['submissions'].items():
        print(f"  {member} :\t{stats['attempts']}\t|\t{stats['correct']}\t|\t{stats['incorrect']}")
    print("\n")
