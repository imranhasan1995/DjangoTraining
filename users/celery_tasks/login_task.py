# tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger
from playwright.async_api import async_playwright
import asyncio

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def run_login_playwright_task(self, username, password):
    """
    Celery task to run Playwright login.
    Celery will automatically retry if an exception is raised.
    """

    async def main():
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("http://127.0.0.1:8000/login/")

            await page.fill("input[name=username]", username)
            await page.fill("input[name=password]", password)
            await page.click("button[type=submit]")

             # Check if redirected to dashboard
            try:
                await page.wait_for_url("http://127.0.0.1:8000/dashboard/", timeout=5000)
                success = True
                message = "Login successful"
            except:
                success = False
                message = "Login failed"

            await page.wait_for_timeout(1000)
            await browser.close()
            logger.info(f"Playwright[celery] finished login for {username}")
            return {
                "username": username,
                "success": success,
                "message": message
            }

    # Run the async Playwright task
    return asyncio.run(main())

    # If any exception occurs, Celery automatically retries because the task fails
