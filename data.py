from playwright.async_api import async_playwright
import time,argparse,sys,csv,os,asyncio

js_code_send = '''
function scrollToBottomAndContinue() {{
    var chatList = document.querySelector(".scrollable.scrollable-y.tabs-tab.chatlist-parts.active");
    var prevScrollHeight = chatList.scrollHeight;

    chatList.scroll(0, document.body.scrollHeight + 10000);

    return new Promise((resolve) => {{
        setTimeout(() => {{
            var newScrollHeight = chatList.scrollHeight;
            resolve(newScrollHeight !== prevScrollHeight);
        }}, 1000);
    }});
}}

var mousedown = new MouseEvent("mousedown", {{
    bubbles: true,
    cancelable: true,
    view: window,
}});

function clickElementAndWaitToFill(element, text) {{
    return new Promise((resolve) => {{
        var doneEvent = new Event('done');
        var clickEvent = new Event('custom-click');

        var handleDone = () => {{
            element.removeEventListener('done', handleDone);
            resolve();
        }};

        var handleCustomClick = () => {{
            element.removeEventListener('custom-click', handleCustomClick);
            element.dispatchEvent(doneEvent);
        }};

        element.addEventListener('done', handleDone);
        element.addEventListener('custom-click', handleCustomClick);
        element.dispatchEvent(mousedown);

        setTimeout(() => {{
            var inputMessage = document.querySelector(".input-message-input.scrollable.scrollable-y.i18n.no-scrollbar");
            inputMessage.textContent = text;

            var inputEvent = new Event('input', {{ bubbles: true, cancelable: true }});
            inputMessage.dispatchEvent(inputEvent);

            document.querySelector(".btn-icon.tgico-none.btn-circle.z-depth-1.btn-send.animated-button-icon.rp.send").click();
            element.dispatchEvent(clickEvent);
        }}, 10);
    }});
}}

async function processChatList() {{
    let t = Object.values(document.querySelector(".chatlist-top").querySelectorAll("ul")[1].querySelectorAll("li"));

    while (t.length < {count}) {{
        var scrollingFinished = await scrollToBottomAndContinue();
        if (!scrollingFinished) {{
            break;
        }}
        t = Object.values(document.querySelector(".chatlist-top").querySelectorAll("ul")[1].querySelectorAll("li"));
    }}

    if (t.length === {count}) {{
        for (var element of t) {{
            await clickElementAndWaitToFill(element, "{message}");
        }}
    }}
}}

'''

async def send(number):
    # try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            url = 'https://web.eitaa.com/'

            await page.goto(url)

            await page.wait_for_selector('.input-field-input')
            input_elements = await page.query_selector_all('.input-field-input')

            if len(input_elements) >= 2:
                    await input_elements[1].type(number)
                    await page.wait_for_selector('.c-ripple')
                    await page.click('.btn-primary.btn-color-primary')
                    await page.wait_for_selector(".input-wrapper")
                    get_code = input("Verification Code: ")

                    input_selector = 'input[type="tel"]'
                    await page.wait_for_selector(input_selector)
                    input_element = await page.query_selector(input_selector)

                    if input_element:
                        await input_element.fill(get_code)
                    await page.wait_for_load_state('load')
                    await page.wait_for_selector(".whole.page-chats")
                    time.sleep(10)
                    max_attempts = 10
                    attempts = 0
                    data = None
                    while attempts < max_attempts:
                        data = await page.evaluate('''async () => {
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
                    message_input = input("enter your message: ")
                    await page.evaluate(js_code_send.format(count=len(users),message=message_input))

                    completed= await page.evaluate('(async () => { return await processChatList(); })')
                    if completed:
                        print("Done.")
                    else:
                        print("Something went wrong.")
                    time.sleep(5)
    # except Exception as e:
    #     print(f"Error: {e}")

    # finally:
    #     browser.close()

async def add(number):
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
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            url = 'https://web.eitaa.com/'

            await page.goto(url)

            await page.wait_for_selector('.input-field-input')
            input_elements = await page.query_selector_all('.input-field-input')

            if len(input_elements) >= 2:
                    input_elements[1].type(number)
                    await page.wait_for_selector('.c-ripple')
                    await page.click('.btn-primary.btn-color-primary')
                    await page.wait_for_selector(".input-wrapper")
                    get_code = input("Verification Code: ")

                    input_selector = 'input[type="tel"]'
                    await page.wait_for_selector(input_selector)
                    input_element = await page.query_selector(input_selector)

                    if input_element:
                        input_element.fill(get_code)
                    await page.wait_for_load_state('load')
                    await page.wait_for_selector(".whole.page-chats")
                    time.sleep(10)
                    await page.query_selector('.btn-icon.btn-menu-toggle.rp.sidebar-tools-button.is-visible').click()
                    await page.query_selector(".btn-menu-item.tgico-user.rp").click()
                    added = 0
                    for adder in to_add:
                        number = 0
                        if len(adder[1]) == 13 and adder[1][0] == '+' and adder[1][0:4] == '+989':
                            number = adder[1][0:3] + " " + adder[1][3:6] + " " + adder[1][6:10] + " " + adder[1][10:13]
                        else:
                            continue
                        await page.query_selector(".btn-circle.btn-corner.z-depth-1.is-visible.tgico-add.rp").click()
                        await page.wait_for_selector(".popup-header")
                        await page.query_selector(".name-fields").query_selector(".input-field-input").fill(adder[0])
                        await page.query_selector_all(".input-field.input-field-phone")[1].query_selector(".input-field-input").fill(number)
                        await page.wait_for_timeout(100)
                        if await page.query_selector(".popup-header").query_selector("button").is_disabled() == False:
                            await page.query_selector(".popup-header").query_selector("button").click()
                            await page.wait_for_function(
                                '() => !document.querySelector(".popup-header").querySelector("button").classList.contains("disabled")',
                            )
                            if await page.query_selector(".popup-header"):
                                await page.query_selector(".btn-icon.popup-close.tgico-close").click()
                            else:
                                added += 1
                    print(f"{added} numbers added .")
                    time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")

    finally:
        browser.close()

async def main():
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
            await send(number)
        else:
            print("No option selected. Please choose an options add or send")
    else:
        print("No option selected. Please choose an options add or send")

if __name__ == "__main__":
    asyncio.run(main())