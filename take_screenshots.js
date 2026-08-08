const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

// Ensure screenshots directory exists
const screenshotDir = path.join(__dirname, 'screenshots');
if (!fs.existsSync(screenshotDir)) {
  fs.mkdirSync(screenshotDir);
}

const PAGES = [
  'Threat Overview',
  'Threat Explorer',
  'Indicators of Compromise',
  'Threat Intelligence Graph',
  'Global Threat Map',
  'Threat Analytics',
  'Crawler Targets',
  'Settings'
];

(async () => {
  console.log('Launching Google Chrome headless...');
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    defaultViewport: { width: 1440, height: 960 },
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
  });

  try {
    const page = await browser.newPage();
    console.log('Navigating to http://localhost:8501 ...');
    await page.goto('http://localhost:8501', { waitUntil: 'networkidle0', timeout: 30000 });

    // Wait a little extra for Streamlit loading spinner to disappear
    await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 6000)));

    for (const pageName of PAGES) {
      console.log(`Navigating to tab: "${pageName}" ...`);

      // Locate and click the radio label containing the text
      const clicked = await page.evaluate((name) => {
        const labels = Array.from(document.querySelectorAll('section[data-testid="stSidebar"] div[role="radiogroup"] label'));
        const target = labels.find(l => l.textContent.trim().toLowerCase().includes(name.toLowerCase()));
        if (target) {
          target.click();
          return true;
        }
        return false;
      }, pageName);

      if (clicked) {
        console.log(`Clicked tab "${pageName}", waiting for rendering...`);
        // Wait for page to render (graphs, charts, etc.)
        await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 5000)));

        const safeName = pageName.toLowerCase().replace(/[^a-z0-9]/g, '_');
        const filename = path.join(screenshotDir, `${safeName}.png`);
        await page.screenshot({ path: filename, fullPage: false });
        console.log(`Successfully saved screenshot: ${filename}`);
      } else {
        console.log(`Warning: Tab "${pageName}" not found in sidebar!`);
      }
    }
  } catch (error) {
    console.error('Error during screenshot capture:', error);
  } finally {
    await browser.close();
    console.log('Done!');
  }
})();
