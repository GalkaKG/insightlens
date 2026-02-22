/* Minimal frontend logic for InsightLens demo.
 * - Upload file to /upload
 * - Trigger /analyze with returned upload_id
 * - Fetch and render HTML report and JSON summary
 * - Allow downloading the full report HTML
 */

const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("file");
const thresholdInput = document.getElementById("threshold");
const reportHtmlDiv = document.getElementById("reportHtml");
const reportJsonPre = document.getElementById("reportJson");
const downloadBtn = document.getElementById("downloadReportBtn");
const downloadInfoDiv = document.getElementById("downloadInfo");

let latestReportId = null;

function setDownloadingUI(isWorking) {
  if (isWorking) {
    downloadBtn.disabled = true;
    downloadBtn.innerText = "Downloading...";
  } else {
    downloadBtn.disabled = !latestReportId;
    downloadBtn.innerText = "Download Full Report";
  }
}

downloadBtn.addEventListener("click", async () => {
  if (!latestReportId) return;
  setDownloadingUI(true);
  try {
    const res = await fetch(`/report/${latestReportId}?format=html`);
    if (!res.ok) throw new Error(res.statusText || "Failed to fetch report");
    const text = await res.text();
    const blob = new Blob([text], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const fname = `insightlens-report-${latestReportId}.html`;
    a.download = fname;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    if (downloadInfoDiv) downloadInfoDiv.textContent = `Saved as ${fname}`;
  } catch (err) {
    alert("Download failed: " + String(err));
  } finally {
    setDownloadingUI(false);
  }
});

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  latestReportId = null;
  setDownloadingUI(false);

  if (!fileInput.files || fileInput.files.length === 0) {
    alert("Please choose a file");
    return;
  }

  const file = fileInput.files[0];
  const fd = new FormData();
  fd.append("file", file, file.name);

  reportHtmlDiv.innerHTML = "Uploading...";
  reportJsonPre.textContent = "";

  try {
    const upResp = await fetch("/upload", { method: "POST", body: fd });
    if (!upResp.ok) {
      const err = await upResp
        .json()
        .catch(() => ({ detail: upResp.statusText }));
      reportHtmlDiv.innerText =
        "Upload failed: " + (err.detail || JSON.stringify(err));
      return;
    }
    const upJson = await upResp.json();
    const uploadId = upJson.upload_id;

    reportHtmlDiv.innerHTML = "Uploaded — analyzing...";

    const analyzeResp = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        upload_id: uploadId,
        missingness_threshold: parseFloat(thresholdInput.value || 0.5),
      }),
    });

    if (!analyzeResp.ok) {
      const err = await analyzeResp
        .json()
        .catch(() => ({ detail: analyzeResp.statusText }));
      reportHtmlDiv.innerText =
        "Analysis failed: " + (err.detail || JSON.stringify(err));
      return;
    }

    const analyzeJson = await analyzeResp.json();
    reportJsonPre.textContent = JSON.stringify(
      analyzeJson.summary || analyzeJson,
      null,
      2,
    );

    // Fetch HTML report and render
    const reportId = analyzeJson.report_id;
    latestReportId = reportId;
    setDownloadingUI(false);
    if (downloadInfoDiv)
      downloadInfoDiv.textContent = `Suggested filename: insightlens-report-${reportId}.html`;

    const rpt = await fetch(`/report/${reportId}?format=html`);
    if (rpt.ok) {
      const html = await rpt.text();
      reportHtmlDiv.innerHTML = html;
    } else {
      reportHtmlDiv.innerText = "Failed to fetch report HTML";
    }
  } catch (err) {
    reportHtmlDiv.innerText = "Unexpected error: " + String(err);
  }
});
