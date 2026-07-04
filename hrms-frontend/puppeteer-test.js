const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('BROWSER ERROR:', msg.text());
    }
  });

  page.on('pageerror', err => {
    console.log('PAGE ERROR:', err.toString());
  });

  try {
    // Try both localhost and host.docker.internal
    let success = false;
    for (const host of ['http://localhost:4200', 'http://host.docker.internal:4200']) {
      try {
        console.log(`Trying ${host}...`);
        await page.goto(host, { waitUntil: 'networkidle0', timeout: 5000 });
        const bodyHTML = await page.evaluate(() => document.body.innerHTML);
        console.log(`BODY from ${host}:`, bodyHTML.substring(0, 500));
        success = true;
        break;
      } catch (err) {
        console.log(`Failed ${host}:`, err.message);
      }
    }
  } catch (err) {
    console.log('NAVIGATION ERROR:', err);
  }

  await browser.close();
})();
