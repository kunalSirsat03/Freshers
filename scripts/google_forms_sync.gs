function onFormSubmit(event) {
  if (!event || !event.range) {
    throw new Error("Run this function from the spreadsheet form-submit trigger.");
  }
  sendSheetRow(event.range.getSheet(), event.range.getRow());
}

function syncExistingResponses() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = sheet.getLastRow();
  for (let row = 2; row <= lastRow; row += 1) {
    sendSheetRow(sheet, row);
  }
}

function sendSheetRow(sheet, rowNumber) {
  const lastColumn = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, lastColumn).getDisplayValues()[0];
  const values = sheet.getRange(rowNumber, 1, 1, lastColumn).getValues()[0];
  const displayValues = sheet.getRange(rowNumber, 1, 1, lastColumn).getDisplayValues()[0];
  const responses = {};
  headers.forEach((header, index) => {
    responses[header || `Column ${index + 1}`] = displayValues[index];
  });

  const properties = PropertiesService.getScriptProperties();
  const webhookUrl = properties.getProperty("DJANGO_WEBHOOK_URL");
  const webhookToken = properties.getProperty("DJANGO_WEBHOOK_TOKEN");
  if (!webhookUrl || !webhookToken) {
    throw new Error("Set DJANGO_WEBHOOK_URL and DJANGO_WEBHOOK_TOKEN in Script Properties.");
  }

  const submittedAt = values[0] instanceof Date ? values[0].toISOString() : new Date().toISOString();
  const payload = {
    response_id: `${sheet.getSheetId()}:${rowNumber}`,
    submitted_at: submittedAt,
    responses: responses,
  };
  const result = UrlFetchApp.fetch(webhookUrl, {
    method: "post",
    contentType: "application/json",
    headers: { "X-Webhook-Token": webhookToken },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });
  const status = result.getResponseCode();
  if (status < 200 || status >= 300) {
    throw new Error(`Django response sync failed with HTTP ${status}.`);
  }
}