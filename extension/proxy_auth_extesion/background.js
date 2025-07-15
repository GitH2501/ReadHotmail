const proxyHost = "38.154.118.182";
const proxyPort = 8800;
const proxyUsername = "tnm";
const proxyPassword = "tnm";

chrome.runtime.onInstalled.addListener(() => {
    chrome.proxy.settings.set(
        {
            value: {
                mode: "fixed_servers",
                rules: {
                    singleProxy: {
                        scheme: "http",
                        host: proxyHost,
                        port: proxyPort
                    },
                    bypassList: ["localhost", "127.0.0.1"]
                }
            },
            scope: "regular"
        },
        function () {
            console.log("Proxy settings applied.");
        }
    );
});

chrome.webRequest.onAuthRequired.addListener(
    function (details, callbackFn) {
        callbackFn({
            authCredentials: {
                username: proxyUsername,
                password: proxyPassword
            }
        });
    },
    { urls: ["<all_urls>"] },
    ["blocking"]
);
