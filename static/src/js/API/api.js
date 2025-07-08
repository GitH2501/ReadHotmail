export async function get_token_graphAPI(code) {
    const params = new URLSearchParams();
    params.append("client_id", "9e5f94bc-e8a4-4e73-b8be-63364c29d753");
    params.append("scope", "https://graph.microsoft.com/User.Read offline_access");
    params.append("code", code);
    params.append("redirect_uri", "https://localhost");
    params.append("grant_type", "authorization_code");
    

    try {
        let get_token_response = await fetch("https://login.microsoftonline.com/common/oauth2/v2.0/token", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: params
        });
        console.log(get_token_response)
        if (!get_token_response.ok) {
            const errorText = await get_token_response.text();
            console.error("Request failed:", get_token_response.status, errorText);
            return null;
        }

        let get_token_data = await get_token_response.json();
        console.log("Access Token:", get_token_data.access_token);
        console.log("Refresh Token:", get_token_data.refresh_token);
        return get_token_data;

    } catch (err) {
        console.error("Exception during token fetch:", err);
        return null;
    }
}


export async function pushTokenToHotmailDB(data) {

    let profile_name = localStorage.getItem("username");
    let password = localStorage.getItem("password");
    let browser_id = localStorage.getItem("browser_id");
    let access_token = data.access_token;
    let refresh_token = data.refresh_token;
    let error = "Null";
    let status = "Completed";
    let profile_id = localStorage.getItem("profile_id");

    let APIHOST = "http://192.168.1.104:8000";
    let APIPOST = "/api/v1/profiles/"

    URL = `${APIHOST}${APIPOST}`

    let pushTokenResponse = await fetch(URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            profile_name, password, browser_id, access_token, refresh_token, error, status, profile_id
        })
    })


    if (!pushTokenResponse.ok) {
        const errorText = await pushTokenResponse.json();
        console.error("Lỗi ", errorText.detail);
        return errorText.detail;
    } else {
        let pushTokenData = await pushTokenResponse.json();

        if (pushTokenResponse.status === 200) {
            const successText = "Push code success!!!"
            console.log(successText)
            return successText
        } else {
            const errorText = "Push code failed!!!"
            console.log(errorText)
            return errorText
        }
    }


}