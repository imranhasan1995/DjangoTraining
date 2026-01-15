# playwright_tasks.py
from playwright.async_api import async_playwright

async def run_login_playwright(username, password):
    """
    Open browser and login with provided credentials.
    Runs asynchronously, no return to API.
    """
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()

            # Open Django login page
            await page.goto("http://127.0.0.1:8000/login/")

            # Fill username & password
            await page.fill("input[name=username]", username)
            await page.fill("input[name=password]", password)

            # Click login
            await page.click("button[type=submit]")

            # Optional: wait a few seconds to simulate user interaction
            await page.wait_for_timeout(3000)

            await browser.close()
            print(f"Playwright finished login for {username}")

    except Exception as e:
        print(f"Playwright error: {e}")
