chrome.runtime.onMessage.addListener(


    function (request, sender, sendResponse) {


        if (request.actionMessage == "push_code") {
            console.log(" Dien thong tin nay")
        }
    }
)