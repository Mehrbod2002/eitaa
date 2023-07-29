function scrollToBottomAndContinue() {
    const chatList = document.querySelector(".scrollable.scrollable-y.tabs-tab.chatlist-parts.active");
    const prevScrollHeight = chatList.scrollHeight;

    chatList.scroll(0, document.body.scrollHeight + 10000);

    return new Promise((resolve) => {
        setTimeout(() => {
            const newScrollHeight = chatList.scrollHeight;
            resolve(newScrollHeight !== prevScrollHeight);
        }, 1000);
    });
}

const mousedown = new MouseEvent("mousedown", {
    bubbles: true,
    cancelable: true,
    view: window,
});

function clickElementAndWaitToFill(element, text) {
    return new Promise((resolve) => {
        const doneEvent = new Event('done');
        const clickEvent = new Event('custom-click');

        const handleDone = () => {
            element.removeEventListener('done', handleDone);
            resolve();
        };

        const handleCustomClick = () => {
            element.removeEventListener('custom-click', handleCustomClick);
            element.dispatchEvent(doneEvent);
        };

        element.addEventListener('done', handleDone);
        element.addEventListener('custom-click', handleCustomClick);
        element.dispatchEvent(mousedown);

        setTimeout(() => {
            const inputMessage = document.querySelector(".input-message-input.scrollable.scrollable-y.i18n.no-scrollbar");
            console.log(inputMessage, "test");
            inputMessage.textContent = text;

            const inputEvent = new Event('input', { bubbles: true, cancelable: true });
            inputMessage.dispatchEvent(inputEvent);

            document.querySelector(".btn-icon.tgico-none.btn-circle.z-depth-1.btn-send.animated-button-icon.rp.send").click();
            element.dispatchEvent(clickEvent);
        }, 10);
    });
}


async function processChatList() {
    let t = Object.values(document.querySelector(".chatlist-top").querySelectorAll("ul")[1].querySelectorAll("li"));

    while (t.length < 55) {
        console.log(t.length, 55);
        const scrollingFinished = await scrollToBottomAndContinue();
        if (!scrollingFinished) {
            break;
        }
        t = Object.values(document.querySelector(".chatlist-top").querySelectorAll("ul")[1].querySelectorAll("li"));
    }

    if (t.length === 55) {
        for (const element of t) {
            await clickElementAndWaitToFill(element, "This is a bot .... please don't send message . we're testing our code");
        }
    }
}

processChatList();
