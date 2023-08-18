from playwright.async_api import async_playwright
import time,argparse,sys,csv,os,asyncio

js_code_send = '''
(async function () {{
    return new Promise(async (complete) => {{
    let mousedown = new MouseEvent("mousedown", {{
        bubbles: true,
        cancelable: true,
        view: window,
    }});

    async function clickElementAndWaitToFill(element, text) {{
        return new Promise(async (resolve) => {{
            element.dispatchEvent(mousedown);
            setTimeout(async () => {{
                let inputMessage = document.querySelector(".input-message-input.scrollable.scrollable-y.i18n.no-scrollbar");
                inputMessage.textContent = text;

                let inputEvent = new Event('input', {{ bubbles: true, cancelable: true }});
                inputMessage.dispatchEvent(inputEvent);

                document.querySelector(".btn-icon.tgico-none.btn-circle.z-depth-1.btn-send.animated-button-icon.rp.send").click();
                await new Promise(resolve => setTimeout(resolve, 1500));
                setTimeout(resolve, 300);
            }}, 200);
        }});
    }}
    async function triggerCustomEvent() {{
        const event = new Event('DONE');
        await document.dispatchEvent(event);
    }};
    async function processChatList() {{
        function waitForClickCompletion() {{
            return new Promise((resolve) => {{
                const btnUser = document.querySelector(".btn-menu-item.tgico-user.rp");
                const handleClick = () => {{
                    btnUser.removeEventListener("click", handleClick);
                    resolve();
                }};
                btnUser.addEventListener("click", handleClick, {{ once: true }});
                btnUser.click();
            }});
        }}

        await waitForClickCompletion();

        var previous_chat_list = 0;
        var stop = false;
        var i = 1;
        setTimeout(async () => {{
            var t = document.querySelectorAll(".chatlist.contacts-container")[0].querySelectorAll("li");
            while (!stop) {{
                var chatList = document.querySelectorAll(".sidebar-content")[1].querySelector(".scrollable.scrollable-y");
                chatList.scroll(0, document.body.scrollHeight + (i * 10000));

                await new Promise(resolve => setTimeout(resolve, 200));
                t = document.querySelectorAll(".chatlist.contacts-container")[0].querySelectorAll("li");
                if (t.length == previous_chat_list) {{
                    stop = true;
                }}
                i += 1;
                previous_chat_list = t.length;
            }}
            var ii = 0;
            for (const element of t) {{
                ii += 1;
                await clickElementAndWaitToFill(element, "{message}");
            }}
            await triggerCustomEvent();
        }}, 1000);
    }};

    await processChatList();
    await triggerCustomEvent();
    setTimeout(complete,6000);
    }});
}})();
'''

async def send(number):
    try:
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
                    message_input = input("enter your message: ")
                    generated_code = js_code_send.format(message=message_input)
                    completed= await page.evaluate(generated_code)
                    await page.wait_for_event('DONE', timeout= 10**10*10*10)
                    if completed:
                        print("Done.")
                    else:
                        print("Something went wrong.")
                    time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")

    finally:
        await browser.close()

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
                    data1 = await page.query_selector('.btn-icon.btn-menu-toggle.rp.sidebar-tools-button.is-visible')
                    await data1.click()
                    data_2= await page.query_selector(".btn-menu-item.tgico-user.rp")
                    await data_2.click()
                    added = 0
                    for adder in to_add:
                        adder[1] = "+"+adder[1]
                        number = 0
                        if len(adder[1]) == 13 and adder[1][0] == '+' and adder[1][0:4] == '+989':
                            number = adder[1][0:3] + " " + adder[1][3:6] + " " + adder[1][6:10] + " " + adder[1][10:13]
                        else:
                            continue
                        data2 = await page.query_selector(".btn-circle.btn-corner.z-depth-1.is-visible.tgico-add.rp")
                        await data2.click()
                        await page.wait_for_selector(".popup-header")
                        data3 = await page.query_selector(".name-fields")
                        data3 = await data3.query_selector(".input-field-input")
                        await data3.fill(adder[0])
                        data4 = await page.query_selector_all(".input-field.input-field-phone")
                        data4 = await data4[1].query_selector(".input-field-input")
                        data4 = await data4.fill(number)
                        await page.wait_for_timeout(100)
                        data5 = await page.query_selector(".popup-header")
                        data5 = await data5.query_selector("button")
                        data5 = await data5.is_disabled()
                        time.sleep(0.2)
                        pop = await page.query_selector(".popup-header")
                        pop = await pop.query_selector("button")
                        if await pop.is_disabled() == False:
                            await pop.click()
                            time.sleep(1)
                            if await page.query_selector(".popup-header"):
                                header1 = await page.query_selector(".btn-icon.popup-close.tgico-close")
                                await header1.click()
                            else:
                                added += 1
                    print(f"{added} numbers added .")
                    time.sleep(5)
    # except Exception as e:
    #     print(f"Error: {e}")
    # finally:
    #     await browser.close()

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
            await add(number)
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