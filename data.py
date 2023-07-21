from playwright.sync_api import sync_playwright
import time,argparse,sys

def login(number):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        url = 'https://web.eitaa.com/'

        page.goto(url)

        page.wait_for_selector('.input-field-input')
        input_elements = page.query_selector_all('.input-field-input')

        if len(input_elements) >= 2:
                input_elements[1].type(number)
                label = page.query_selector_all('label')
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
                print(users)
                # page.query_selector(".btn-menu-item.tgico-user.rp").click()
                # page.query_selector(".btn-circle.btn-corner.z-depth-1.is-visible.tgico-add.rp").click()
                # page.wait_for_selector(".popup-header")
                # inputs = page.query_selector_all(".input-field-input")
                # inputs[3] = 'ALi'
                # inputs[5] = "+98 913 878 0275"
                # page.click('.btn-primary.btn-color-primary')
                time.sleep(40000)

        else:
                print("There are not enough elements with the specified class.")

        # except Exception as e:
        #     print(f"Error: {e}")

        # finally:
        #     browser.close()

def main():
    parser = argparse.ArgumentParser(description='Eitaa App')
    parser.add_argument('-p', type=str, choices=['add','send'],
                        help='Select an option: add or send')
    args = parser.parse_args()

    if args.p:
        selected_option = args.p
        if selected_option == "add":
            get_number = input("Enter number : ").strip()
            if len(get_number) != 13 and get_number[0] != '+' and get_number[0:4] != '+989':
                sys.exit("Invalid number")
            number = get_number[0:3] + " " + get_number[3:6] + " " + get_number[6:10] + " " + get_number[10:13]
            login(number)
        elif selected_option == "send":
            print("You selected option 2.")
        else:
            print("No option selected. Please choose an options add or send")
    else:
        print("No option selected. Please choose an option (1, 2, or 3).")

if __name__ == "__main__":
    main()