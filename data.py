from playwright.sync_api import sync_playwright
import time,argparse,sys,csv,os

def send(number):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = 'https://web.eitaa.com/'

            page.goto(url)

            page.wait_for_selector('.input-field-input')
            input_elements = page.query_selector_all('.input-field-input')

            if len(input_elements) >= 2:
                    input_elements[1].type(number)
                    page.wait_for_selector('.c-ripple')
                    page.click('.btn-primary.btn-color-primary')
                    page.wait_for_selector(".input-wrapper")
                    get_code = input("Verification Code: ")

                    input_selector = 'input[type="tel"]'
                    page.wait_for_selector(input_selector)
                    input_element = page.query_selector(input_selector)

                    if input_element:
                        input_element.fill(get_code)
                    page.wait_for_load_state('load')
                    page.wait_for_selector(".whole.page-chats")
                    time.sleep(10)
                    max_attempts = 10
                    attempts = 0
                    data = None
                    while attempts < max_attempts:
                        data = page.evaluate('''async () => {
                            function getAllDataFromObjectStore() {
                                return new Promise((resolve, reject) => {
                                    const request = window.indexedDB.open('tweb');
                                    request.onerror = (event) => reject(request.error);
                                    request.onsuccess = async (event) => {
                                        const db = request.result;
                                        const transaction = db.transaction('users', 'readonly');
                                        const objectStore = transaction.objectStore('users');

                                        const data = await new Promise((resolve, reject) => {
                                            const request = objectStore.getAll();
                                            request.onerror = (event) => reject(request.error);
                                            request.onsuccess = (event) => resolve(request.result);
                                        });

                                        resolve(data);
                                    };
                                });
                            }

                            return await getAllDataFromObjectStore();
                        }''')
                        attempts += 1

                    users = {}
                    if data is not None:
                        for i in data:
                            if 'phone' in i and 'first_name' in i:
                                users[i["phone"]] = i['first_name']
                    else:
                        print("IndexedDB data is not available on the new page.")
                    on_contacts = page.query_selector(".chatlist-bottom").query_selector("ul")
                    if on_contacts:
                        text_message = input("Insert your message: ")
                        if len(text_message) == 0:
                            raise "Text message is empty"
                        list_items = on_contacts.query_selector_all('li')
                        while len(list_items) <= len(users)-5:
                            page.evaluate('document.querySelector(".scrollable.scrollable-y.tabs-tab.chatlist-parts.active.with-contacts").scroll(0,document.body.scrollHeight+10000000)')
                            list_items = on_contacts.query_selector_all('li')
                        for item in list_items:
                            item.click()
                            page.wait_for_selector(".input-message-input.scrollable.scrollable-y.i18n.no-scrollbar")
                            inputs = page.query_selector(".input-message-input.scrollable.scrollable-y.i18n.no-scrollbar")
                            if inputs:
                                inputs.fill(text_message)
                                page.query_selector(".btn-icon.tgico-none.btn-circle.z-depth-1.btn-send.animated-button-icon.rp.send").click()
                    time.sleep(10000)
    except Exception as e:
        print(f"Error: {e}")

    finally:
        browser.close()

def add(number):
    file_path = input("User file path: ")
    if os.path.exists(file_path) == False:
        sys.exit("File not exist")
    data = []
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            data.append(row)
    if len(data[1:]) == 0:
        sys.exit("Users list is null")
    to_add = data[1:]
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            url = 'https://web.eitaa.com/'

            page.goto(url)

            page.wait_for_selector('.input-field-input')
            input_elements = page.query_selector_all('.input-field-input')

            if len(input_elements) >= 2:
                    input_elements[1].type(number)
                    page.wait_for_selector('.c-ripple')
                    page.click('.btn-primary.btn-color-primary')
                    page.wait_for_selector(".input-wrapper")
                    get_code = input("Verification Code: ")

                    input_selector = 'input[type="tel"]'
                    page.wait_for_selector(input_selector)
                    input_element = page.query_selector(input_selector)

                    if input_element:
                        input_element.fill(get_code)
                    page.wait_for_load_state('load')
                    page.wait_for_selector(".whole.page-chats")
                    time.sleep(10)
                    page.query_selector('.btn-icon.btn-menu-toggle.rp.sidebar-tools-button.is-visible').click()
                    page.query_selector(".btn-menu-item.tgico-user.rp").click()
                    added = 0
                    for adder in to_add:
                        number = 0
                        if len(adder[1]) == 13 and adder[1][0] == '+' and adder[1][0:4] == '+989':
                            number = adder[1][0:3] + " " + adder[1][3:6] + " " + adder[1][6:10] + " " + adder[1][10:13]
                        else:
                            continue
                        page.query_selector(".btn-circle.btn-corner.z-depth-1.is-visible.tgico-add.rp").click()
                        page.wait_for_selector(".popup-header")
                        page.query_selector(".name-fields").query_selector(".input-field-input").fill(adder[0])
                        page.query_selector_all(".input-field.input-field-phone")[1].query_selector(".input-field-input").fill(number)
                        page.wait_for_timeout(100)
                        if page.query_selector(".popup-header").query_selector("button").is_disabled() == False:
                            page.query_selector(".popup-header").query_selector("button").click()
                            page.wait_for_function(
                                '() => !document.querySelector(".popup-header").querySelector("button").classList.contains("disabled")',
                            )
                            if page.query_selector(".popup-header"):
                                page.query_selector(".btn-icon.popup-close.tgico-close").click()
                            else:
                                added += 1
                    print(f"{added} numbers added .")
                    time.sleep(10000)
    except Exception as e:
        print(f"Error: {e}")

    finally:
        browser.close()

def main():
    parser = argparse.ArgumentParser(description='Eitaa App')
    parser.add_argument('-p', type=str, choices=['add','send'],
                        help='Select an option: add or send')
    args = parser.parse_args()

    if args.p:
        selected_option = args.p
        if selected_option == "add":
            get_number = input("Enter number: ").strip()
            if len(get_number) != 13 and get_number[0] != '+' and get_number[0:4] != '+989':
                sys.exit("Invalid number")
            number = get_number[0:3] + " " + get_number[3:6] + " " + get_number[6:10] + " " + get_number[10:13]
            add(number)
        elif selected_option == "send":
            get_number = input("Enter number: ").strip()
            if len(get_number) != 13 and get_number[0] != '+' and get_number[0:4] != '+989':
                sys.exit("Invalid number")
            number = get_number[0:3] + " " + get_number[3:6] + " " + get_number[6:10] + " " + get_number[10:13]
            send(number)
        else:
            print("No option selected. Please choose an options add or send")
    else:
        print("No option selected. Please choose an options add or send")

if __name__ == "__main__":
    main()