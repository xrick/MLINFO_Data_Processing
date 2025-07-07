const API_BASE_URL = 'http://localhost:8000';

export async function processText(textContent, customRules, tempRegex) {
  const response = await fetch(`${API_BASE_URL}/api/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text_content: textContent,
      custom_rules: customRules,
      temp_regex: tempRegex,
    }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'An unknown error occurred');
  }
  return response.json();
}

export async function ingestToDB(tableData) {
    const response = await fetch(`${API_BASE_URL}/api/ingest-to-db`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: tableData }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'An unknown error occurred during ingestion');
    }
    return response.json();
}