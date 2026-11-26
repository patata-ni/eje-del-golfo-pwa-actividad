import {defineConfig} from '@playwright/test';
export default defineConfig({
  testDir:'./tests/pwa',
  timeout:45000,
  fullyParallel:false,
  reporter:[['list'],['html',{outputFolder:'pwa-test-report',open:'never'}]],
  use:{baseURL:'http://127.0.0.1:8765',browserName:'chromium',screenshot:'only-on-failure',trace:'retain-on-failure',launchOptions:{args:['--use-fake-device-for-media-stream']}},
  webServer:{command:'python3 -m http.server 8765 --bind 127.0.0.1 --directory public/pwa',url:'http://127.0.0.1:8765',reuseExistingServer:!process.env.CI}
});
