// "use strict"

chrome.runtime.onMessage.addListener(


    function (request, sender, sendResponse) {
        function getElementByXPath(xpath) {
            return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        }


        if (request.actionMessage == "fill_info") {
            console.log(" Dien thong tin nay")

            let username = localStorage.getItem('username');
            let pass = localStorage.getItem('password')

            if (username && pass) {
                chrome.storage.local.set({ "username": username }).then(() => {
                });
                chrome.storage.local.set({ "password": pass }).then(() => {
                })

            }
            chrome.storage.local.get(["username"]).then((result) => {
                let email = result.username;
                chrome.storage.local.get(["password"]).then((result) => {
                    let password = result.password;

                    if ($('#i0116').length) {
                        $('#i0116').val(email);

                    }
                    if ($('#passwordEntry').length || getElementByXPath("//input[@name='passwd']")) {
                        $('#passwordEntry').val(password);
                    }
                    let passwordField = getElementByXPath("//input[@name='passwd']");
                    if (passwordField) {
                        passwordField.value = password;

                        // Bắn sự kiện để web nhận giá trị mới
                        passwordField.dispatchEvent(new Event('input', { bubbles: true }));
                        passwordField.dispatchEvent(new Event('change', { bubbles: true }));
                    }

                });
            });

            ////h1[text() = 'Verify your email']
            //xpath Yêu cầu recovery



        }

        sendResponse({ farewell: "goodbye" });
    }

);

$(document).ready(function () {
    var txt = '<a href="#" class="float-newmoon"><i class="fa fa-plus my-float">KDP01</i></a>';
    $("body").prepend(txt)
});