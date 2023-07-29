(async function () {
    let mousedown = new MouseEvent("mousedown", {
        bubbles: true,
        cancelable: true,
        view: window,
    });

    function clickElementAndWaitToFill(element, text) {
        return new Promise((resolve) => {
            let doneEvent = new Event('done');
            let clickEvent = new Event('custom-click');

            let handleDone = () => {
                element.removeEventListener('done', handleDone);
                resolve();
            };

            let handleCustomClick = () => {
                element.removeEventListener('custom-click', handleCustomClick);
                element.dispatchEvent(doneEvent);
            };

            element.addEventListener('done', handleDone);
            element.addEventListener('custom-click', handleCustomClick);
            element.dispatchEvent(mousedown);

            setTimeout(() => {
                let inputMessage = document.querySelector(".input-message-input.scrollable.scrollable-y.i18n.no-scrollbar");
                console.log(inputMessage)
                inputMessage.textContent = text;

                let inputEvent = new Event('input', { bubbles: true, cancelable: true });
                inputMessage.dispatchEvent(inputEvent);

                document.querySelector(".btn-icon.tgico-none.btn-circle.z-depth-1.btn-send.animated-button-icon.rp.send").click();
                element.dispatchEvent(clickEvent);
            }, 10);
        });
    }

    async function processChatList() {
        function waitForClickCompletion() {
            return new Promise((resolve) => {
                const btnUser = document.querySelector(".btn-menu-item.tgico-user.rp");
                const handleClick = () => {
                    btnUser.removeEventListener("click", handleClick);
                    resolve();
                };
                btnUser.addEventListener("click", handleClick, { once: true });
                btnUser.click();
            });
        }

        await waitForClickCompletion();

        let scrollingFinished = false;
        let previous_chat_list = 0;
        setTimeout(async () => {
            var t = document.querySelectorAll(".chatlist.contacts-container")[0].querySelectorAll("li");
            while (!scrollingFinished) {
                const chatList = document.querySelectorAll(".sidebar-content")[1].querySelector(".scrollable.scrollable-y");
                chatList.scroll(0, document.body.scrollHeight + 10000);

                await new Promise((resolve) => setTimeout(resolve, 1000));

                t = document.querySelectorAll(".chatlist.contacts-container")[0].querySelectorAll("li");
                if (t.length == previous_chat_list) {
                    break;
                }
                previous_chat_list = t.length;
            }

            for (const element of t) {
                await clickElementAndWaitToFill(element, "{message}");
            }
        }, 1000);
    }
    await processChatList();
})();
