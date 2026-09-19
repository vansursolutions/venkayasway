// Phone screenshots via Chrome DevTools Protocol with real mobile emulation.
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PAGES = [['index.html','01-home'],['annadanam.html','02-annadanam'],['events.html','03-events'],['temple.html','04-temple'],['gallery.html','05-gallery'],['life.html','06-life']];
const port = 9333;
const chrome = spawn(CHROME, ['--headless=new','--disable-gpu','--no-first-run',`--remote-debugging-port=${port}`,'--user-data-dir=/tmp/vs-shots-profile','about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
await sleep(1500);
const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
let id = 0; const pending = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Emulation.setDeviceMetricsOverride', { width: 360, height: 800, deviceScaleFactor: 3, mobile: true });
await send('Emulation.setUserAgentOverride', { userAgent: 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Mobile Safari/537.36' });
await send('Emulation.setTouchEmulationEnabled', { enabled: true });
await send('Page.enable');
for (const [path, name] of PAGES) {
  await send('Page.navigate', { url: 'https://srivenkaiahswamy.com/' + path });
  await sleep(3500);
  await send('Runtime.evaluate', { expression: "var b=document.getElementById('installBanner'); if(b) b.remove(); window.scrollTo(0,0);" });
  await sleep(300);
  const { data } = await send('Page.captureScreenshot', { format: 'png', clip: { x: 0, y: 0, width: 360, height: 800, scale: 3 } });
  writeFileSync(`screenshots/${name}.png`, Buffer.from(data, 'base64'));
  console.log('saved', name);
}
ws.close(); chrome.kill();
