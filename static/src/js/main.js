// Khi mở modal, load giá trị hiện tại
function loadSettings() {
  $.get('/api/profile-folder', function (data) {
    $('#profileFolder').val(data.profileFolder);
  });
}

// Khi ấn Save Settings
function saveSettings() {
  var newFolder = $('#profileFolder').val();
  $.ajax({
    url: '/api/profile-folder',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ profileFolder: newFolder }),
    success: function (response) {
      alert('Đã lưu đường dẫn mới!');
    }
  });
}

// Gắn sự kiện khi mở modal
$('#exampleModal').on('show.bs.modal', loadSettings);

function logoutEvent() {
  try {
    fetch('/logout__action', {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.logout === "success") {
          localStorage.removeItem('username');
          localStorage.removeItem('password');
          localStorage.removeItem('user');
          localStorage.removeItem('pass');

          window.location.href = '/';
        } else {
          console.error('Đăng xuất thất bại:', data.message);
        }
      })
      .catch((error) => {
        console.error('Lỗi khi đăng xuất:', error);
      });
  } catch (error) {
    console.error("Lỗi rồi nha pro:", error);
  }
}
document
  .getElementById("fileInput")
  .addEventListener("change", async function (event) {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append("file", file);

      // Hiển thị progress bar và reset về 0%
      $('#progressContainer').show();
      $('#progressBar').val(0);
      $('#status').text('0% - Đang load dữ liệu mới...');

      // Ẩn table khi bắt đầu upload file mới
      $('#table').hide();

      try {
        const response = await fetch("import_profile__action", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const text = await response.text();
          throw new Error(text);
        }

        const result = await response.json();
        const totalPages = result.total;
        const page = result.page;
        const limit = result.limit;
        const data = result.data;

        $('#progressBar').val(30);
        $('#status').text('30% - Đang xử lý dữ liệu...');

        await renderTableWithProgress(data);
        $('#table').show();
        $('#progressBar').val(100);
        $('#status').text('100% - Hoàn thành!');

        setTimeout(() => {
          $('#progressContainer').hide();
        }, 2000);

        enableButton();
        renderPaginate(totalPages, page, limit);
      } catch (error) {
        console.error("Lỗi khi upload:", error);
        $('#status').text('Lỗi khi upload file!');
        $('#progressBar').val(0);
        setTimeout(() => {
          $('#progressContainer').hide();
        }, 3000);
      }
      event.target.value = "";
    }
  });
/**
 * @param {Array}   data         - mảng dữ liệu cần load
 * @param {Number}  delay        - thời gian giả lập xử lý mỗi phần tử (ms), mặc định 500
 */
async function loadDataWithProgress(data, delay = 500, onComplete) {
  const total = data.length;
  const $container = $('#progressContainer');
  const $bar = $('#progressBar');
  const $status = $('#status');

  if (total === 0) {
    $status.text('Không có dữ liệu để load.');
    return;
  }

  // 1. Hiển thị progress bar và reset
  $container.show();
  $bar.val(0);
  $status.text('0% - Đang load dữ liệu mới...');

  const totalTime = total * 50;
  const stepInterval = totalTime / 100;

  let simulated = 0;
  const simId = setInterval(() => {
    simulated++;
    if (simulated < 100) {
      $bar.val(simulated);
      $status.text(`${simulated}% - Đang load dữ liệu mới...`);
    } else {
      clearInterval(simId);
    }
  }, stepInterval);
  for (let idx = 0; idx < total; idx++) {
    await new Promise(res => setTimeout(res, 50));
  }

  clearInterval(simId);
  $bar.val(100);
  $status.text('100% - Hoàn thành!');

  if (typeof onComplete === 'function') {
    onComplete();
  }

  setTimeout(() => {
    $container.hide();
    $bar.val(0);
    $status.text('0%');
  }, 200);
}


async function renderTableWithProgress(data) {
  const total = data.length;
  if (total === 0) {
    $('#status').text('Không có dữ liệu để hiển thị.');
    return;
  }

  let currentProgress = 30;
  const progressStep = 60 / total;

  document.getElementById("table").innerHTML = `
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Profile name</th>
            <th>Browser</th>
            <th>Proxy</th>
            <th class="ngangtoken">Token</th>
            <th>Completed</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="table-body">
          ${data.map((row, index) => `
            <tr class="{{ loop.index0 }}">
              <td id="idProfile" class="id-profile">${row["Profile_id"]}</td>
              <td>${row["Profile_name"]}</td>
              <td>${row["Browser_type"]}</td>
              <td>${row["Proxy_type"]}|| ${row["Proxy_ip"]}:${row["Proxy_port"]}</td>
              <td class="ngangtoken" id="access_token">${row["Access_token"]}</td>
              <td status-cell >${row["completed"] === true ? "True" : "False"}</td>
              <td>
                <div class="action-column">
                  <div class="item-button start-button disabled" data-id="${row['Profile_id']}" onclick="start_action_event(this)">
                    <img src="/static/publish/plus.png" alt="" style="max-width:12px">
                    <span>Start</span>
                  </div>
                </div>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;

  // Cập nhật progress cho từng item với delay
  return new Promise((resolve) => {
    data.forEach((row, index) => {
      setTimeout(() => {
        currentProgress += progressStep;
        const percent = Math.min(Math.floor(currentProgress), 90);
        $('#progressBar').val(percent);
        $('#status').text(`${percent}% - Đang xử lý tài khoản ${index + 1}/${total}...`);

        // Khi hoàn thành tất cả items
        if (index + 1 === total) {
          resolve();
        }
      }, index * 50); // Delay 50ms cho mỗi item
    });
  });
}

function renderPaginate(total, page, limit) {
  const pages = Math.ceil(total / limit);
  const current = page;

  // Tính toán range hiển thị (tối đa 5 trang)
  let startPage = Math.max(1, current - 2);
  let endPage = Math.min(pages, startPage + 4);

  // Điều chỉnh startPage nếu endPage quá gần cuối
  if (endPage - startPage < 4 && pages > 5) {
    startPage = Math.max(1, endPage - 4);
  }

  let html = '';
  html += `<li><button onclick="fetchPage(${total},${Math.max(1, current - 1)}, ${limit})" ${current <= 1 ? 'disabled' : ''} class="nav-btn">‹</button></li>`;
  if (startPage > 1) {
    html += `<li><button onclick="fetchPage(${total},1, ${limit})">1</button></li>`;
    if (startPage > 2) {
      html += `<li><span class="dots">...</span></li>`;
    }
  }
  for (let i = startPage; i <= endPage; i++) {
    html += `<li><button onclick="fetchPage(${total},${i}, ${limit})" ${i === current ? 'disabled' : ''}>${i}</button></li>`;
  }
  if (endPage < pages) {
    if (endPage < pages - 1) {
      html += `<li><span class="dots">...</span></li>`;
    }
    html += `<li><button onclick="fetchPage(${total},${pages}, ${limit})">${pages}</button></li>`;
  }
  html += `<li><button onclick="fetchPage(${total},${Math.min(pages, current + 1)}, ${limit})" ${current >= pages ? 'disabled' : ''} class="nav-btn">›</button></li>`;

  document.getElementById("panigate_page").innerHTML = `<ul>${html}</ul>`;

  currentPageData = { total, page, limit };
  updatePageInfo();
}

async function fetchPage(total, page, limit) {
  try {
    const response = await fetch(`paginate_page/${page}?total=${total}&limit=${limit}`, {
      method: "GET",
    })

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text);
    }

    const result = await response.json()
    const data = result.result
    setTimeout(() => {
      renderPaginate(total, page, limit);
      renderTable(data);
      window.addEventListener('load', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }, 100);


  } catch (error) {

  }
}


function updatePageInfo() {
  const pages = Math.ceil(currentPageData.total / currentPageData.limit);
  const info = `Trang ${currentPageData.page}/${pages} - Hiển thị ${currentPageData.limit} items/trang - Tổng: ${currentPageData.total} items`;
  document.getElementById("page-info").textContent = info;
}

function renderTable(data) {
  data.sort((a, b) => {
    if ((a["completed"] === 'true' && b["completed"] !== 'true')) return -1;
    if ((a["completed"] !== 'true' && b["completed"] === 'true')) return 1;
    return 0;
  });
  const html = data.map(row => `
                <tr class="{{ loop.index0 }}">
                    <td id="idProfile" class="id-profile">${row["Profile_id"]}</td>
                    <td>${row["Profile_name"]}</td>
                    <td>${row["Browser_type"]}</td>
                    <td>${row["Proxy_type"]} || ${row["Proxy_ip"]}:${row["Proxy_port"]}</td>
                    <td class="ngangtoken">${row["Access_token"]}</td>
                    <td>${row["completed"] === true ? "True" : "False"}</td>
                    <td>
                        <div class="action-column">
                            <div class="item-button start-button disabled" data-id="${row['Profile_id']}" onclick="start_action_event(this)">
                                <img src="/static/publish/plus.png" alt="" style="max-width:12px">
                                <span>Start</span>
                            </div>
                        </div>
                    </td>
                </tr>
                
        `).join("");

  document.getElementById("table").innerHTML =
    `
          <table>
          <thead>
                <tr>
                    <th>ID</th>
                    <th>Profile name</th>
                    <th>Browser</th>
                    <th>Proxy</th>
                    <th class="ngangtoken">Token</th>
                    <th>Completed</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody id="table-body">
           ${html}
          </tbody>
          </table>
          
          `;
}


function enableButton() {
  const data = getDataTableProfile();
  const getTokenButton = document.querySelector(".getToken-button");
  getTokenButton.classList.remove("disabled");
}
function getDataTableProfile() {
  const table = document.getElementById("table");
  const rows = table.querySelectorAll("tbody tr");
  const data = [];

  rows.forEach((row) => {
    const cells = row.querySelectorAll("td");
    const rowData = Array.from(cells).map((cell) => cell.textContent.trim());
    data.push(rowData);
  });

  return data;
}
async function getTokenEvent() {
  const profileCount = document.querySelectorAll("tbody tr").length;
  const idProfileArray = Array.from(document.querySelectorAll(".id-profile")).map(
    (id) => id.textContent.trim()
  );
  try {
    const response = await fetch("get_token__action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        profileCount: profileCount,
        ids: idProfileArray
      }),
    });

    const data = await response.json();
    if (data.status_code === 200) {
      actionArray = data.data;
      const start_action_ele_array = document.querySelectorAll(".start-button");
      for (const actionItem of actionArray) {
        if (actionItem["action"] === "start") {
          const btn = document.querySelector(`.start-button[data-id="${actionItem["ID"]}"]`);
          if (btn) btn.classList.remove("disabled");
        }
        // Cập nhật cột Completed
        const row = document.querySelector(`.start-button[data-id="${actionItem["ID"]}"]`)?.closest("tr");
        if (row && typeof actionItem["completed"] !== "undefined") {
          const completedCell = row.querySelector("td[status-cell]") || row.querySelector("td:nth-child(6)");
          if (completedCell) completedCell.textContent = actionItem["completed"] ? "True" : "False";
        }
      }
    } else {
      console.error("Lỗi khi lấy token:", data.message);
    }
  } catch (error) {
    console.error("Lỗi khi lưu idProfileArray vào localStorage:", error);
  }
}


// 3) Animation dots
function animateDots(span) {
  let count = 0;
  return setInterval(() => {
    count = (count + 1) % 16;
    span.textContent = '.'.repeat(count);
  }, 0);
}

// // 4) Gắn sự kiện sau khi DOM sẵn sàng
// document.addEventListener('DOMContentLoaded', () => {
//   // Gán Get token
//   document.getElementById('get_token')
//     .addEventListener('click', getTokenEvent);

//   // Delegate Start button
//   document.querySelector('#profiles-table tbody')
//     .addEventListener('click', e => {
//       if (e.target.closest('.start-button')) {
//         start_action_event(e.target.closest('.start-button'));
//       }
//     });
// });

function animateDots(span) {
  let dotCount = 0;
  return setInterval(() => {
    dotCount = (dotCount + 1) % 16; //0-10
    span.textContent = ".".repeat(dotCount);
  }, 500);
}


async function start_action_event(element) {
  const profileID = element.getAttribute("data-id");
  const trElement = element.closest("tr");
  const accessTokenElement = trElement.querySelector("#access_token");
  const statusElement = trElement.querySelector('td[status-cell]');
  const startElement = element.querySelector("span");
  const imageElement = element.querySelector("img");
  const loadingInterval = animateDots(startElement);

  element.classList.add("starting");
  imageElement.style.display = "none";

  let ID = profileID != null ? profileID : "null";
  try {
    var response = await fetch("start__action", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_profile: ID,
      }),
    })
    const data = await response.json();
    const id = data.ID;
    const action = data.action;
    const access_token = data.access_token;

    clearInterval(loadingInterval);
    imageElement.style.display = "block";
    startElement.innerHTML = "Start";
    element.classList.remove("starting");

    if (action === null && access_token !== null) {
      accessTokenElement.textContent = shortenToken(access_token, 40);
      statusElement.textContent = "True";
      element.classList.add("disabled");
    } else {
      element.classList.remove("disabled");
    }
  } catch (err) {
    clearInterval(loadingInterval);
    element.classList.remove("starting");
    element.classList.remove("disabled");
    startElement.innerHTML = "Start";
    imageElement.style.display = "block";
    console.error('Lỗi start_action_event:', err);
  }
}
function shortenToken(token, maxLength = 10) {
  if (!token) return "";
  if (token.length <= maxLength) return token;
  return token.slice(0, maxLength) + '...';
}
function saveSettings() {
  // Lưu đường dẫn profile
  const folder = document.getElementById("profileFolder").value;
  localStorage.setItem("profileFolder", folder);
  // Lưu trạng thái autoLogin
  const autoLoginChecked = document.getElementById("autoLogin").checked;
  localStorage.setItem("autoLogin", autoLoginChecked ? "1" : "0");
  alert("Đã lưu cài đặt!");
}

function loadSettingsAndAutoLogin() {
  // Khôi phục profile folder
  const saved = localStorage.getItem("profileFolder");
  if (saved) {
    document.getElementById("profileFolder").value = saved;
  }
  // Khôi phục autoLogin
  const autoLogin = localStorage.getItem("autoLogin");
  if (autoLogin === "1") {
    document.getElementById("autoLogin").checked = true;
  }
  // Tự động đăng nhập nếu autoLogin bật
  const username = localStorage.getItem("username");
  const password = localStorage.getItem("password");
  if (autoLogin === "1" && username && password) {
    loginEvent(username, password); // Thay bằng hàm login thực tế của bạn
  }
}

// Gán sự kiện cho nút Save Settings
// (Đảm bảo nút Save Settings có onclick="saveSettings()" trong HTML)

// Gán sự kiện khi load trang
window.addEventListener("DOMContentLoaded", loadSettingsAndAutoLogin);

// Nếu bạn muốn lưu trạng thái autoLogin ngay khi tick/bỏ tick (không cần bấm Save):
document.getElementById("autoLogin").addEventListener("change", function () {
  localStorage.setItem("autoLogin", this.checked ? "1" : "0");
});

