// const proxyHost = "192.126.238.68";
// const proxyPort = 8800;
// const proxyUsername = "tnm";
// const proxyPassword = "tnm";

// chrome.runtime.onInstalled.addListener(() => {
//     chrome.proxy.settings.set({
//         value: {
//             mode: "fixed_servers",
//             rules: {
//                 singleProxy: {
//                     scheme: "http",
//                     host: proxyHost,
//                     port: parseInt(proxyPort)
//                 },
//                 bypassList: ["localhost", "127.0.0.1"]
//             }
//         },
//         scope: "regular"
//     }, () => {
//         console.log("✅ Proxy settings applied.");
//     });
// });

// chrome.webRequest.onAuthRequired.addListener(
//     function (details) {
//         console.log("🔐 Proxy auth");
//         return {
//             authCredentials: {
//                 username: proxyUsername,
//                 password: proxyPassword
//             }
//         };
//     },
//     { urls: ["<all_urls>"] },
//     ["blocking"]
// );



let proxyConfig = null;
async function loadProxyConfig() {
    const url = chrome.runtime.getURL("proxy_config.json");
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error("Could not load proxy config file.");
    }
    return await response.json();
}

// Apply proxy settings on install
chrome.runtime.onInstalled.addListener(() => {
    loadProxyConfig().then(config => {
        chrome.proxy.settings.set({
            value: {
                mode: "fixed_servers",
                rules: {
                    singleProxy: {
                        scheme: "http",
                        host: config.proxyHost,
                        port: parseInt(config.proxyPort)
                    },
                    bypassList: ["localhost", "127.0.0.1"]
                }
            },
            scope: "regular"
        }, () => {
            console.log("✅ Proxy settings applied.");
        });
    }).catch(console.error);
});

chrome.webRequest.onAuthRequired.addListener(
    async function (details, callback) {
        if (!proxyConfig) {
            await loadProxyConfig();
        }
        callback({
            authCredentials: {
                username: proxyConfig.proxyUsername,
                password: proxyConfig.proxyPassword
            }
        });
    },
    { urls: ["<all_urls>"] },
    ["asyncBlocking"]
);

