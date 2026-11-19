// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
// Print one HTML page of the user guide to PDF with Chromium (Playwright).
//   node print-pdf.js guide-en.html Edukasaun-Desktop-Guide-English.pdf "Footer text"
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [, , input, output, footer] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const esc = (s) => String(s || '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  await page.pdf({
    path: output,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate:
      '<div style="width:100%;font-family:Inter,sans-serif;font-size:7.5pt;color:#6b7d90;padding:0 16mm;display:flex;justify-content:space-between;">' +
      '<span>' + esc(footer) + '</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: { top: '18mm', bottom: '20mm', left: '16mm', right: '16mm' },
    preferCSSPageSize: true,
  });
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
