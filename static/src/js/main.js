// Khi mở modal, load giá trị hiện tại
function loadSettings() {
  let defaultPath = "C:\\Users\\Admin\\AppData\\Local\\tnmhotmail\\profile";
  const saved = localStorage.getItem("profileFolder");
  $('#profileFolder').val(saved || defaultPath);
}

// Khi ấn Save Settings
function saveSettings() {
  var oldFolder = localStorage.getItem("profileFolder") || "C:\\Users\\Admin\\AppData\\Local\\tnmhotmail\\profile";
  var newFolder = $('#profileFolder').val();
  $.ajax({
    url: '/api/profile-folder',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ oldProfileFolder: oldFolder, newProfileFolder: newFolder }),
    success: function (response) {
      alert('Đã lưu đường dẫn mới!');
      localStorage.setItem("profileFolder", newFolder);
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
          // Gắn lại sự kiện click cho các nút Start
          document.querySelectorAll('.start-button').forEach(btn => {
            btn.onclick = function () {
              start_action_event(this);
            }
          });
          // Gọi hàm cập nhật trạng thái nút Start sau khi render xong bảng
          updateStartButtonStates(data);
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
      // Đảm bảo cập nhật lại trạng thái nút Start sau khi render
      updateStartButtonStates(data);
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
  // Sắp xếp để các profile có Status là 'Completed' lên đầu
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

  // Gọi hàm cập nhật trạng thái nút Start sau khi render xong bảng
  updateStartButtonStates(data);
  // Sau khi render xong, enable lại nút Start nếu profile đã get token và token=null/rỗng
  const gotTokenIds = JSON.parse(localStorage.getItem('gotTokenProfileIds') || '[]');
  const startedIds = JSON.parse(localStorage.getItem('startedProfileIds') || '[]');
  const failedIds = JSON.parse(localStorage.getItem('failedStartProfileIds') || '[]');

  data.forEach(row => {
    const btn = document.querySelector(`.start-button[data-id="${row["Profile_id"]}"]`);
    const span = btn?.querySelector("span");
    const img = btn?.querySelector("img");
    if (!btn) return;

    // Nếu đã start thành công
    if (startedIds.includes(row["Profile_id"])) {
      btn.classList.add("disabled");
      if (img) img.style.display = "block";
      if (span) span.innerHTML = "Start";
    } else if (failedIds.includes(row["Profile_id"])) {
      // Nếu start thất bại
      btn.classList.remove("disabled");
      if (img) img.style.display = "none";
      if (span) span.innerHTML = "✔ Start";
    } else if (gotTokenIds.includes(row["Profile_id"])) {
      // Nếu đã get token nhưng chưa start
      btn.classList.remove("disabled");
      if (img) img.style.display = "block";
      if (span) span.innerHTML = "Start";
    } else {
      // Chưa get token, disable nút
      btn.classList.add("disabled");
      if (img) img.style.display = "block";
      if (span) span.innerHTML = "Start";
    }
  });


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



  // 1) Hàm Get Token — gọi backend trả về list action, và apply lên từng row
  // async function getTokenEvent() {
  //   const rows = Array.from(document.querySelectorAll('tbody tr'));

  //   // 1) Gọi backend
  //   try {
  //     const res = await fetch('get_token__action', {
  //       method: 'POST',
  //       headers: { 'Content-Type': 'application/json' },
  //       body: JSON.stringify({ profileCount: rows.length })
  //     });
  //     const payload = await res.json();

  //     if (payload.status_code === 200) {
  //       const actionArray = payload.data;

  //       rows.forEach(row => {
  //         const btn = row.querySelector('.start-button');
  //         if (btn) {
  //           btn.classList.remove('disabled');
  //           btn.disabled = false;
  //         }
  //       });

  //       actionArray.forEach(item => {
  //         const idx = item.position;
  //         const row = rows[idx];
  //         if (!row) return;
  //         const btn = row.querySelector('.start-button');
  //         if (!btn) return;

  //         if (item.action === 'start') {
  //           btn.classList.remove('disabled');
  //           btn.disabled = false;
  //         } else {
  //           btn.classList.add('disabled');
  //           btn.disabled = true;
  //         }
  //       });
  //     } else {
  //       console.error('Lỗi get_token__action:', payload.message);
  //     }
  //   } catch (err) {
  //     console.error('Lỗi khi gọi get_token__action:', err);
  //   }

  //   rows.forEach(row => {
  //     const statusCell =
  //       row.querySelector('.status-cell') ||
  //       row.querySelector('td:nth-child(6)');
  //     const st = (statusCell?.textContent || '').trim().toLowerCase();
  //     const btn = row.querySelector('.start-button');
  //     if (!btn) return;

  //     if (st === 'Completed') {
  //       btn.classList.add('disabled');
  //       btn.disabled = true;
  //     } else {
  //       btn.classList.remove('disabled');
  //       btn.disabled = false;
  //     }
  //   });
  // }



  // 2) Hàm Start — gọi backend để chạy, luôn re-enable nếu gặp lỗi, chỉ lock khi thật sự Completed
  // async function start_action_event(el) {

  //   const startButton = document.querySelector(".start-button");

  //     const res  = await fetch('start__action', {
  //       method: 'POST',
  //       headers: { 'Content-Type': 'application/json' },
  //       body: JSON.stringify({ id_profile: btn.dataset.id })
  //     });

  //     if (!res.ok) {
  //       console.log("!res.ok")
  //       return
  //     }
  //     const data = await res.json();
  //     const id = data.ID;
  //     const action = data.action;
  //     console.log(action)

  //     if (action === "start") {
  //       startButton.classList.remove('disabled');

  //     }

  //   } catch (err) {
  //     // 2.7 Nếu lỗi thì re-enable để retry
  //     clearInterval(loadingLoop);
  //     btn.classList.remove('starting');
  //     img.style.display = 'block';
  //     span.textContent  = 'Start';
  //     btn.classList.remove('disabled');
  //     btn.disabled = false;
  //     statusCell.textContent = 'error';
  //     console.error('Lỗi start_action_event:', err);
  //   }
  // }

  // 3) Animation dots
  function animateDots(span) {
    let count = 0;
    return setInterval(() => {
      count = (count + 1) % 16;
      span.textContent = '.'.repeat(count);
    }, 500);
  }

  // 4) Gắn sự kiện sau khi DOM sẵn sàng
  document.addEventListener('DOMContentLoaded', () => {
    // Gán Get token
    document.getElementById('get_token')
      .addEventListener('click', getTokenEvent);

    // Delegate Start button
    document.querySelector('#profiles-table tbody')
      .addEventListener('click', e => {
        if (e.target.closest('.start-button')) {
          start_action_event(e.target.closest('.start-button'));
        }
      });
  });

  function animateDots(span) {
    let dotCount = 0;
    return setInterval(() => {
      dotCount = (dotCount + 1) % 16; //0-10
      span.textContent = ".".repeat(dotCount);
    }, 500);
  }
  // Đảm bảo hàm này nằm ở ngoài cùng file, không nằm trong bất kỳ function nào khác
  async function start_action_event(element) {
    const profileID = element.getAttribute("data-id");
    const startElement = element.querySelector("span");
    const imageElement = element.querySelector("img");

    const loadingInterval = animateDots(startElement);
    element.classList.add("starting");
    imageElement.style.display = "none";

    let ID = profileID != null ? String(profileID) : "null";
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
      const id = String(data.ID);
      const startedButFailed = data.started_but_failed;
      const completed = data.completed;

      clearInterval(loadingInterval);
      imageElement.style.display = "block";
      element.classList.remove("starting");

      // Lưu trạng thái vào localStorage
      let startedIds = JSON.parse(localStorage.getItem('startedProfileIds') || '[]').map(String);
      let failedIds = JSON.parse(localStorage.getItem('failedStartProfileIds') || '[]').map(String);
      // Xóa khỏi failed nếu đã start thành công
      failedIds = failedIds.filter(item => item !== ID);

      if (completed) {
        // Thành công: disable nút, icon/text về mặc định
        element.classList.add("disabled");
        imageElement.src = "/static/publish/plus.png";
        startElement.innerHTML = "Start";
        if (!startedIds.includes(ID)) {
          startedIds.push(ID);
        }
        // Đảm bảo không nằm trong failedIds
        failedIds = failedIds.filter(item => item !== ID);
      } else if (startedButFailed) {
        // Không thành công: đổi icon thành tick, KHÔNG disable nút
        imageElement.style.display = "none";
        startElement.innerHTML = "✔ Start";
        element.classList.remove("disabled");
        if (!failedIds.includes(ID)) {
          failedIds.push(ID);
        }
        // Đảm bảo không nằm trong startedIds
        startedIds = startedIds.filter(item => item !== ID);
      } else {
        // Trường hợp khác: cũng coi như thất bại
        imageElement.style.display = "none";
        startElement.innerHTML = "✔ Start";
        element.classList.remove("disabled");
        if (!failedIds.includes(ID)) {
          failedIds.push(ID);
        }
        startedIds = startedIds.filter(item => item !== ID);
      }
      // Lưu lại localStorage
      localStorage.setItem('startedProfileIds', JSON.stringify(startedIds));
      localStorage.setItem('failedStartProfileIds', JSON.stringify(failedIds));
    } catch (err) {
      clearInterval(loadingInterval);
      element.classList.remove("starting");
      element.classList.remove("disabled");
      startElement.innerHTML = "Start";
      imageElement.style.display = "block";
      imageElement.src = "/static/publish/plus.png";
      console.error('Lỗi start_action_event:', err);
    }
  }
  window.start_action_event = start_action_event;


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
      const actionArray = data.data;
      // Lưu danh sách profile đã get token vào localStorage (chỉ lưu ID)
      const gotTokenIds = actionArray.map(item => item.ID).filter(id => id);
      // Lấy danh sách cũ
      let oldIds = JSON.parse(localStorage.getItem('gotTokenProfileIds') || '[]');
      // Gộp và loại trùng
      let mergedIds = Array.from(new Set([...oldIds, ...gotTokenIds]));
      localStorage.setItem('gotTokenProfileIds', JSON.stringify(mergedIds));

      // Chỉ enable nút Start cho các profile đã Get Token trên trang hiện tại
      for (const actionItem of actionArray) {
        if (actionItem["action"] === "start") {
          // Tìm đúng nút theo data-id
          const btn = document.querySelector(`.start-button[data-id="${actionItem["ID"]}"]`);
          if (btn) btn.classList.remove("disabled");
        }
        // Cập nhật cột Completed
        const row = document.querySelector(`.start-button[data-id="${actionItem["ID"]}"]`)?.closest("tr");
        if (row && typeof actionItem["completed"] !== "undefined") {
          const completedCell = row.querySelector("td[status-cell]") || row.querySelector("td:nth-child(6)");
          if (completedCell) completedCell.textContent = actionItem["completed"] ? "true" : "False";
        }
      }
      // Sau khi lấy token xong, gọi fetchPage để reload lại table
      if (typeof currentPageData !== 'undefined') {
        fetchPage(currentPageData.total, currentPageData.page, currentPageData.limit);
      }
    } else {
      console.error("Lỗi khi lấy token:", data.message);
    }
  } catch (error) {
    console.error("Lỗi khi lưu idProfileArray vào localStorage:", error);
  }
}
function enableButton() {
  const getTokenButton = document.querySelector(".getToken-button");
  if (getTokenButton) {
    getTokenButton.classList.remove("disabled");
  }
}

function updateStartButtonStates(data) {
  const gotTokenIds = JSON.parse(localStorage.getItem('gotTokenProfileIds') || '[]').map(String);
  const startedIds = JSON.parse(localStorage.getItem('startedProfileIds') || '[]').map(String);
  const failedIds = JSON.parse(localStorage.getItem('failedStartProfileIds') || '[]').map(String);

  data.forEach(row => {
    const idStr = String(row["Profile_id"]);
    const btn = document.querySelector(`.start-button[data-id="${idStr}"]`);
    const span = btn?.querySelector("span");
    const img = btn?.querySelector("img");
    if (!btn) return;

    if (startedIds.includes(idStr)) {
      btn.classList.add("disabled");
      if (img) img.style.display = "block";
      if (span) span.innerHTML = "Start";
    } else if (failedIds.includes(idStr)) {
      btn.classList.remove("disabled");
      if (img) img.style.display = "none";
      if (span) span.innerHTML = "✔ Start";
    } else if (gotTokenIds.includes(idStr)) {
      btn.classList.remove("disabled");
      if (img) img.style.display = "block";
      if (span) span.innerHTML = "Start";
    } else {
      btn.classList.add("disabled");
      if (img) img.style.display = "block";
      if (span) span.innerHTML = "Start";
    }
  });
}
