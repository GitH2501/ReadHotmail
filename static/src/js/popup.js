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
    submitBtn.addEventListener('click', handleSubmit);

    async function handleSubmit() {
        const inputValue = stringInput.value.trim();

        if (!inputValue) {
            showStatus('Vui lòng nhập chuỗi string!', 'error');
            return;
        }
        try {
            await logToConsole(inputValue)
            restartInput(stringInput)
            disableButton(submitBtn)
        } catch (error) {
            console.error('Lỗi:', error);
            // showStatus('Có lỗi xảy ra: ' + error.message, 'error');
            showStatus('id đã tồn tại')
        }
    }

    async function logToConsole(inputString) {
        const code = inputString.split("code=")[1];

        let gettoken_response = await get_token_graphAPI(code)

        if (gettoken_response) {
            let pushcode_response = await pushTokenToHotmailDB(gettoken_response)



            // showStatus(pushcode_response)

            // Nếu trả về object có success và profile_id
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
    function restartInput(stringInput) {
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