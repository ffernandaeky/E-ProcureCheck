const form = document.querySelector('#search-form');
const codeInput = document.querySelector('#code');
const clearButton = document.querySelector('#clear-button');
const searchButton = document.querySelector('#search-button');
const searchLabel = document.querySelector('#search-label');
const message = document.querySelector('#message');
const result = document.querySelector('#result');
const resultBanner = document.querySelector('#result-banner');
const resultTitle = document.querySelector('#result-title');
const resultDescription = document.querySelector('#result-description');
const fields = document.querySelector('#result-fields');
const themeToggle = document.querySelector('#theme-toggle');

const copy = {
  en: {
    brandSubtitle: 'ITEM VERIFICATION SYSTEM',
    title: 'Item Code Verification',
    intro: 'Check an item code against the procurement database.',
    label: 'Enter Item Code',
    hint: 'Exact match. Codes are case-sensitive.',
    button: 'Check Item Code',
    checking: 'Checking...',
    clear: 'Clear item code',
    themeDark: 'Switch to dark mode',
    themeLight: 'Switch to light mode',
    language: 'Language',
    resultLabel: 'Verification result',
    empty: 'Enter an item code to continue.',
    invalid: 'Check the item code and try again.',
    found: ['Item Found', 'Registered in the procurement database.'],
    'not-found': ['Item Not Found', 'No matching code found.'],
    duplicate: ['Duplicate Code Detected', 'Multiple records found for this code.'],
    error: ['Unable to Verify Item', 'Database unavailable. Please try again.'],
    fields: ['Unique Code', 'Item Name', 'Category', 'Specification', 'Unit', 'Procurement Year']
  },
  id: {
    brandSubtitle: 'SISTEM VERIFIKASI BARANG',
    title: 'Verifikasi Kode Barang',
    intro: 'Periksa kode barang pada database pengadaan.',
    label: 'Masukkan Kode Barang',
    hint: 'Kode dicocokkan persis dan peka huruf besar/kecil.',
    button: 'Periksa Kode Barang',
    checking: 'Memeriksa...',
    clear: 'Hapus kode barang',
    themeDark: 'Aktifkan mode gelap',
    themeLight: 'Aktifkan mode terang',
    language: 'Bahasa',
    resultLabel: 'Hasil verifikasi',
    empty: 'Masukkan kode barang untuk melanjutkan.',
    invalid: 'Periksa kode barang lalu coba lagi.',
    found: ['Barang Ditemukan', 'Terdaftar di database pengadaan.'],
    'not-found': ['Barang Tidak Ditemukan', 'Kode tidak ditemukan.'],
    duplicate: ['Kode Duplikat Terdeteksi', 'Beberapa data memiliki kode ini.'],
    error: ['Barang Tidak Dapat Diverifikasi', 'Database tidak tersedia. Silakan coba lagi.'],
    fields: ['Kode Unik', 'Nama Barang', 'Kategori', 'Spesifikasi', 'Satuan', 'Tahun Pengadaan']
  }
};

const sourceFieldLabels = {
  'Unique Code': 0,
  'Nama Barang': 1,
  'Kategori': 2,
  'Spesifikasi': 3,
  'Satuan': 4,
  'Tahun Pengadaan': 5
};
let language = localStorage.getItem('procurecheck-language') === 'id' ? 'id' : 'en';

function currentTheme() {
  return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  document.querySelector('meta[name="theme-color"]').content = theme === 'dark' ? '#111827' : '#17365D';
  const label = copy[language][theme === 'dark' ? 'themeLight' : 'themeDark'];
  themeToggle.setAttribute('aria-label', label);
  themeToggle.title = label;
  localStorage.setItem('procurecheck-theme', theme);
}

function renderResultCopy() {
  const status = resultBanner.dataset.status;
  const statusCopy = copy[language][status] || copy[language].error;
  resultTitle.textContent = statusCopy[0];
  resultDescription.textContent = statusCopy[1];
  fields.querySelectorAll('.field').forEach((row) => {
    const term = row.querySelector('dt');
    const fieldIndex = sourceFieldLabels[term.dataset.sourceLabel];
    if (fieldIndex !== undefined) term.textContent = copy[language].fields[fieldIndex];
  });
}

function setLanguage(nextLanguage) {
  language = nextLanguage;
  const strings = copy[language];
  document.documentElement.lang = language;
  document.title = language === 'id' ? 'PROCURECHECK | Verifikasi Barang' : 'PROCURECHECK | Item Verification';
  document.querySelectorAll('[data-copy]').forEach((element) => {
    element.textContent = strings[element.dataset.copy];
  });
  codeInput.placeholder = 'e.g. PRC-2026-000001';
  clearButton.setAttribute('aria-label', strings.clear);
  clearButton.title = strings.clear;
  document.querySelector('.language-switch').setAttribute('aria-label', strings.language);
  result.setAttribute('aria-label', strings.resultLabel);
  document.querySelectorAll('[data-language]').forEach((button) => {
    const active = button.dataset.language === language;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  if (searchButton.disabled) searchLabel.textContent = strings.checking;
  if (message.dataset.message === 'empty') message.textContent = strings.empty;
  if (message.dataset.message === 'invalid') message.textContent = strings.invalid;
  renderResultCopy();
  localStorage.setItem('procurecheck-language', language);
  setTheme(currentTheme());
}

function showResult(status, record = null) {
  resultBanner.dataset.status = status;
  fields.replaceChildren();

  if (status === 'found' && record) {
    for (const [sourceLabel, value] of Object.entries(record)) {
      const term = document.createElement('dt');
      const description = document.createElement('dd');
      const row = document.createElement('div');
      row.className = 'field';
      row.dataset.sourceLabel = sourceLabel;
      const fieldIndex = sourceFieldLabels[sourceLabel];
      term.textContent = fieldIndex === undefined ? sourceLabel : copy[language].fields[fieldIndex];
      description.textContent = value === null || value === '' ? '—' : String(value);
      row.append(term, description);
      fields.append(row);
    }
  }

  result.hidden = false;
  renderResultCopy();
  result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

let latestRequestId = 0;

codeInput.addEventListener('input', () => {
  latestRequestId += 1;
  clearButton.disabled = codeInput.value.length === 0;
  message.textContent = '';
  delete message.dataset.message;
  result.hidden = true;
  fields.replaceChildren();
  searchButton.disabled = false;
  searchButton.classList.remove('is-loading');
  searchLabel.textContent = copy[language].button;
});

clearButton.addEventListener('click', () => {
  latestRequestId += 1;
  codeInput.value = '';
  clearButton.disabled = true;
  message.textContent = '';
  delete message.dataset.message;
  result.hidden = true;
  fields.replaceChildren();
  searchButton.disabled = false;
  searchButton.classList.remove('is-loading');
  searchLabel.textContent = copy[language].button;
  codeInput.focus();
});

themeToggle.addEventListener('click', () => setTheme(currentTheme() === 'dark' ? 'light' : 'dark'));
document.querySelectorAll('[data-language]').forEach((button) => {
  button.addEventListener('click', () => setLanguage(button.dataset.language));
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  message.textContent = '';
  delete message.dataset.message;
  result.hidden = true;
  fields.replaceChildren();

  if (codeInput.value.length === 0) {
    message.dataset.message = 'empty';
    message.textContent = copy[language].empty;
    codeInput.focus();
    return;
  }

  searchButton.disabled = true;
  searchButton.classList.add('is-loading');
  searchLabel.textContent = copy[language].checking;
  const requestId = ++latestRequestId;
  const requestedCode = codeInput.value;

  try {
    const response = await fetch(`/api/search?code=${encodeURIComponent(requestedCode)}`, { cache: 'no-store' });
    const payload = await response.json();
    if (requestId !== latestRequestId) return;
    if (response.status === 404) {
      showResult('not-found');
    } else if (response.ok && (payload.status === 'duplicate' || payload.result === 'DUPLICATE')) {
      showResult('duplicate');
    } else if (response.ok && payload.record) {
      if (payload.record['Unique Code'] !== requestedCode) {
        showResult('error');
      } else {
        showResult('found', payload.record);
      }
    } else if (response.status === 400) {
      message.dataset.message = 'invalid';
      message.textContent = copy[language].invalid;
    } else {
      showResult('error');
    }
  } catch {
    if (requestId === latestRequestId) showResult('error');
  } finally {
    if (requestId === latestRequestId) {
      searchButton.disabled = false;
      searchButton.classList.remove('is-loading');
      searchLabel.textContent = copy[language].button;
    }
  }
});

const savedTheme = localStorage.getItem('procurecheck-theme') === 'dark' ? 'dark' : 'light';
setLanguage(language);
setTheme(savedTheme);
