// chrome.runtime.onMessage.addListener(data => {
//     if (data.type === 'notification') {
//         // chrome.notifications.create('', data.options);
//         // chrome.notifications.create("", data.options, function (notificationId) {
//         // });
//         // chrome.notifications.create("", data.options);
//         // chrome.notifications.onClicked.addListener(function (notificationId) {
//         //     // chrome.tabs.create({url: 'https://rayz9x.ga'});
//         // });
//         // chrome.notifications.onClicked.addListener(abc);
//     }
// });

// chrome.browserAction.onClicked.addListener(function(){

// 	chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {

//         chrome.tabs.sendMessage(tabs[0].id, {actionMessage: "fill_info"}, function(response){
//             console.log(response)
//         });

// 	});
// });





chrome.action.onClicked.addListener((tab) => {
  chrome.tabs.sendMessage(tab.id, { actionMessage: "fill_info" }, (response) => {
    console.log("Response from content script:", response);
  });
});
