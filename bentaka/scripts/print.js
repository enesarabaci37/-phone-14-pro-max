const { chromium } = require('playwright');
(async () => {
  const dir = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + dir + '/guide.html', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: dir + '/../Bentaka-Marka-Kiti/Bentaka-Marka-Kilavuzu.pdf',
    width: '297mm', height: '210mm', printBackground: true, preferCSSPageSize: true,
  });
  await page.setViewportSize({ width: 1123, height: 794 });
  const pages = await page.$$('section.page');
  for (let i = 0; i < pages.length; i++) {
    await pages[i].screenshot({ path: dir + '/_guide_p' + (i + 1) + '.png' });
  }
  await browser.close();
})();
