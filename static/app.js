const inputText = document.getElementById("inputText");
const btnProcess = document.getElementById("btnProcess");
const btnSample = document.getElementById("btnSample");
const statusEl = document.getElementById("status");
const resultSection = document.getElementById("resultSection");
const timelineContent = document.getElementById("timelineContent");
const biographyContent = document.getElementById("biographyContent");
const tokenDisplay = document.getElementById("tokenDisplay");

let currentTimeline = null;

// Load sample text
btnSample.addEventListener("click", async () => {
    try {
        statusEl.textContent = "正在加载示例文本...";
        const resp = await fetch("/sample_data/oral_history.txt");
        if (resp.ok) {
            inputText.value = await resp.text();
            statusEl.textContent = "示例文本已加载，点击 [开始生成传记] 按钮";
        } else {
            statusEl.textContent = "加载示例文本失败";
        }
    } catch (e) {
        statusEl.textContent = "加载示例文本失败: " + e.message;
    }
});

// Process text
btnProcess.addEventListener("click", async () => {
    const text = inputText.value.trim();
    if (!text) {
        statusEl.textContent = "请先输入或加载文本";
        return;
    }
    if (text.length < 100) {
        statusEl.textContent = "文本太短，请至少输入100字";
        return;
    }

    btnProcess.disabled = true;
    resultSection.style.display = "none";

    const steps = [
        "正在抽取关键事件...",
        "正在规划时间线...",
        "正在撰写温情传记...",
    ];

    try {
        statusEl.textContent = steps[0];
        const resp = await fetch("/api/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text }),
        });

        // Simulate step progress while waiting
        let stepIdx = 0;
        const stepInterval = setInterval(() => {
            stepIdx = Math.min(stepIdx + 1, steps.length - 1);
            statusEl.textContent = steps[stepIdx];
        }, 3000);

        const data = await resp.json();
        clearInterval(stepInterval);

        if (data.error) {
            statusEl.textContent = "错误: " + data.error;
            btnProcess.disabled = false;
            return;
        }

        // Render results
        currentTimeline = data.timeline;
        renderTimeline(data.timeline);
        renderBiography(data.biography);
        resultSection.style.display = "grid";

        // Update token usage
        const usage = data.token_usage;
        tokenDisplay.textContent =
            `Token 消耗: 总计 ${usage.total.toLocaleString()} (输入 ${usage.prompt.toLocaleString()} + 输出 ${usage.completion.toLocaleString()})`;

        statusEl.textContent = "✅ 传记生成完成！";
    } catch (e) {
        statusEl.textContent = "请求失败: " + e.message;
    } finally {
        btnProcess.disabled = false;
    }
});

// Render timeline
function renderTimeline(timeline) {
    if (!timeline || !timeline.chapters) {
        timelineContent.innerHTML = "<p>未能生成时间线</p>";
        return;
    }

    let html = "";
    for (const ch of timeline.chapters) {
        html += `<div class="chapter-block">
            <div class="chapter-title" onclick="toggleChapter(this)">
                <span>▸ ${esc(ch.title)}</span>
                <span class="chapter-period">${esc(ch.period || "")}</span>
            </div>
            <ul class="event-list">`;

        for (const ev of (ch.events || [])) {
            html += `<li class="event-item" onclick="scrollToSection('${esc(ev.title || ev.year || "")}')">
                <span class="event-year">${esc(ev.year || "")}</span>${esc(ev.title || ev.event || "")}
            </li>`;
        }

        html += "</ul></div>";
    }
    timelineContent.innerHTML = html;
}

// Render biography
function renderBiography(bio) {
    if (!bio) {
        biographyContent.innerHTML = "<p>未能生成传记</p>";
        return;
    }
    // Convert markdown to HTML (simple approach)
    const html = bio
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/^### (.+)$/gm, "<h3>$1</h3>")
        .replace(/^## (.+)$/gm, '<h2 id="$1">$1</h2>')
        .replace(/^# (.+)$/gm, "<h1>$1</h1>")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n\n/g, "</p><p>")
        .replace(/\n/g, "<br>");
    biographyContent.innerHTML = "<p>" + html + "</p>";
}

// Toggle chapter collapse
function toggleChapter(el) {
    const list = el.nextElementSibling;
    if (list) {
        const isHidden = list.style.display === "none";
        list.style.display = isHidden ? "" : "none";
        el.innerHTML = el.innerHTML.replace(isHidden ? "▸" : "▾", isHidden ? "▾" : "▸");
    }
}

// Scroll to section in biography
function scrollToSection(title) {
    // Try to find and scroll to the heading in biography
    const bio = biographyContent;
    const headings = bio.querySelectorAll("h2, h3");
    for (const h of headings) {
        if (h.textContent.includes(title)) {
            h.scrollIntoView({ behavior: "smooth", block: "start" });
            h.style.background = "#fdf6f0";
            setTimeout(() => { h.style.background = ""; }, 2000);
            break;
        }
    }
}

function esc(str) {
    if (!str) return "";
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
