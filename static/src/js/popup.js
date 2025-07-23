import { get_token_graphAPI } from "./API/api.js"
import { pushTokenToHotmailDB } from "./API/api.js"

document.addEventListener('DOMContentLoaded', function () {
    const stringInput = document.getElementById('stringInput');
    const submitBtn = document.getElementById('submitBtn');
    const status = document.getElementById('status');


    stringInput.focus();


    stringInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            handleSubmit();
        }
    });
    submitBtn.addEventListener('click', function () {
        handleSubmit()
    });

    async function handleSubmit() {
        const inputValue = stringInput.value.trim();
        const code_url = inputValue.split("code=")[1];
        const api_url = "http://127.0.0.1:8800/push_token"

        //Cần thêm bảo mật ở đây
        const profile_id = localStorage.getItem("profile_id");
        const profile_name = localStorage.getItem("username");
        const password = localStorage.getItem("password")
        const code = code_url

        if (!inputValue) {
            showStatus('Vui lòng nhập chuỗi string!', 'error');
            return;
        }
        showStatus("Đang xử lý....", "processing")
        try {
            const response = await fetch(api_url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    profile_name: profile_name,
                    password: password,
                    profile_id: profile_id,
                    code: code
                })
            })

            if (!response.ok) {
                throw new Error("HTTP Error: " + response.status);
            }
            const result = await response.json();
            if (result.success) {

                // const row = document.querySelector(`.start-button[data-id="${profile_id}"]`)?.closest("tr");
                // if (row) {
                //     const startBtn = row.querySelector(".start-button");
                //     const completedCell = row.querySelector("td[status-cell]") || row.querySelector("td:nth-child(6)");
                //     if (completedCell) completedCell.textContent = "True";
                //     if (startBtn) startBtn.classList.add("disabled");
                // }
                showStatus(result.message, "success");
                autoHideStatus();
                clearInput(stringInput);
                disableButton(submitBtn);
            } else {
                showStatus(result.message, "failed")
                autoHideStatus()
            }

        } catch (error) {
            showStatus(error.message, "error");
        }
    }

    async function logToConsole(inputString) {
        const code = inputString.split("code=")[1];



        let gettoken_response = await get_token_graphAPI(code)

        if (gettoken_response) {
            let pushcode_response = await pushTokenToHotmailDB(gettoken_response)

            if (pushcode_response && pushcode_response.success && pushcode_response.profile_id) {
                // Tìm đúng row theo profile_id (nếu có bảng profile trong popup)
                const row = document.querySelector(`.start-button[data-id="${pushcode_response.profile_id}"]`)?.closest("tr");
                if (row) {
                    // Cập nhật cell Completed
                    const completedCell = row.querySelector("td[status-cell]") || row.querySelector("td:nth-child(6)");
                    if (completedCell) completedCell.textContent = "true";
                    // Disable nút Start
                    const startBtn = row.querySelector(".start-button");
                    if (startBtn) startBtn.classList.add("disabled");
                }
            }
            showStatus(pushcode_response.message || pushcode_response, pushcode_response.success ? 'success' : 'error');
            autoHideStatus()
        }

    }
    function disableButton(submitBtn) {
        submitBtn.classList.add("disabled");
        // submitBtn.disable = true;
    }
    function clearInput(stringInput) {
        stringInput.value = "";
    }
    function showStatus(message, type) {
        status.textContent = message;
        status.className = `status ${type} show`;
    }

    function hideStatus() {
        status.className = 'status';
    }

    function autoHideStatus() {
        setTimeout(hideStatus, 5000);
    }

    submitBtn.addEventListener('mousedown', function () {
        this.style.transform = 'translateY(0)';
    });

    submitBtn.addEventListener('mouseup', function () {
        this.style.transform = 'translateY(-2px)';
    });
});