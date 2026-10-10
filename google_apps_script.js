// =================================================================
// GOOGLE APPS SCRIPT DÀNH CHO CẬP NHẬT GOOGLE SHEETS TỰ ĐỘNG
// Coppy toàn bộ đoạn mã này dán vào Google Sheets -> Extensions (Tiện ích mở rộng) -> Apps Script
// =================================================================

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();

    // 1. CẬP NHẬT TAB: 📆 Checklist hôm nay
    if (data.daily) {
      var sheet0 = ss.getSheetByName("📆 Checklist hôm nay") || ss.insertSheet("📆 Checklist hôm nay");
      sheet0.clear();
      sheet0.getRange(1, 1, data.daily.length, data.daily[0].length).setValues(data.daily);
      sheet0.getRange(1, 1, 1, data.daily[0].length).setBackground("#1E293B").setFontColor("#FFFFFF").setFontWeight("bold");
    }

    // 2. CẬP NHẬT TAB: 📋 Tất cả công việc
    if (data.tasks) {
      var sheet1 = ss.getSheetByName("📋 Tất cả công việc") || ss.insertSheet("📋 Tất cả công việc");
      sheet1.clear();
      sheet1.getRange(1, 1, data.tasks.length, data.tasks[0].length).setValues(data.tasks);
      sheet1.getRange(1, 1, 1, data.tasks[0].length).setBackground("#1E293B").setFontColor("#FFFFFF").setFontWeight("bold");
    }

    // 3. CẬP NHẬT TAB: 📝 Nhật ký đã làm
    if (data.logs) {
      var sheet2 = ss.getSheetByName("📝 Nhật ký đã làm") || ss.insertSheet("📝 Nhật ký đã làm");
      sheet2.clear();
      sheet2.getRange(1, 1, data.logs.length, data.logs[0].length).setValues(data.logs);
      sheet2.getRange(1, 1, 1, data.logs[0].length).setBackground("#1E293B").setFontColor("#FFFFFF").setFontWeight("bold");
    }

    return ContentService.createTextOutput(JSON.stringify({ status: "success" })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: err.toString() })).setMimeType(ContentService.MimeType.JSON);
  }
}
