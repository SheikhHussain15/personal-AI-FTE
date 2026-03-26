"""Test Playwright browser launch"""
import sys
import traceback
from pathlib import Path
from datetime import datetime

log_file = Path(__file__).parent / 'test_playwright.log'

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'{timestamp} - {msg}\n')

log('=== Starting Playwright Test ===')

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    log('Playwright imported successfully')
except Exception as e:
    log(f'Import ERROR: {e}')
    sys.exit(1)

try:
    log('Entering sync_playwright context...')
    with sync_playwright() as p:
        log('Context entered')
        
        log('Launching browser (headless)...')
        browser = p.chromium.launch(headless=True, timeout=30000)
        log('Browser launched!')
        
        log('Creating new page...')
        page = browser.new_page()
        
        log('Navigating to Google...')
        page.goto('https://www.google.com', timeout=20000)
        log(f'Page title: {page.title()}')
        
        log('Closing browser...')
        browser.close()
        
    log('=== TEST PASSED ===')
    
except Exception as e:
    log(f'TEST FAILED: {e}')
    log(f'Traceback: {traceback.format_exc()}')
