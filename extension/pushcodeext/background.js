chrome.action.onClicked.addListener((tab) => {
    chrome.tabs.sendMessage(tab.id, { actionMessage: "push_code" }, (response) => {
        console.log("Response from content script:", response);
    });
});