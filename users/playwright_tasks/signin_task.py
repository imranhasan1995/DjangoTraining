# playwright_tasks.py
from playwright.async_api import async_playwright
from datetime import datetime

async def run_google_create_account_test(username: str, password: str, firstname: str, lastname: str, dob: str, gender: str):
    """
    Open browser, navigate Google sign-in page, click Create Account → For myself,
    fill Name page, then fill Birthday & Gender page using API input.
    Takes screenshots at each step.
    
    Parameters:
        dob: string in format "DD-MM-YYYY"
        gender: string, "male", "female", or "other"
    """
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=False, slow_mo=500)
            page = await browser.new_page()

            # 1️⃣ Open Google sign-in page
            await page.goto("https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&dsh=S757992623%3A1768461444724159&emr=1&followup=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&ifkv=AXbMIuBD14Tg8u7LMoHn1Yg9GglRx9XuJ3aC-3qhI7tN1EtTtxIkeqJKi9LudX7HF0kLSNkbLVIpFQ&osid=1&passive=1209600&service=mail&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
            await page.wait_for_load_state("networkidle")

            # 2️⃣ Click "Create account"
            await page.get_by_text("Create account", exact=True).click()
            await page.screenshot(path="create_account_page.png")
            print("Screenshot saved: create_account_page.png")

            # 3️⃣ Click "For my personal use"
            personal_use_option = page.locator('li[role="menuitem"] >> text=For my personal use')
            await personal_use_option.wait_for(state="visible")
            await personal_use_option.click()

            # 4️⃣ Fill Name page
            await page.wait_for_selector('input[name="firstName"]')
            await page.fill('input[name="firstName"]', firstname)
            await page.fill('input[name="lastName"]', lastname)
            await page.screenshot(path="name_filled_page.png")
            print("Screenshot saved: name_filled_page.png")

            # Click Next on Name page
            next_button = page.locator('button:has-text("Next")')
            await next_button.wait_for(state="visible")
            await next_button.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path="birthday_gender_page.png")
            print("Screenshot saved: birthday_gender_page.png")
            # Wait Birthday & Gender page
            await page.wait_for_selector('input#day')

            # Parse DOB
            dob_date = datetime.strptime(dob, "%d-%m-%Y")

            # Day and Year (simple inputs)
            await page.fill('#day', str(dob_date.day))
            await page.fill('#year', str(dob_date.year))

            # --- Month ---
            month_combobox = page.locator('div#month div[role="combobox"]')
            await month_combobox.click()  # open dropdown
            month_name = dob_date.strftime("%B")
            await page.get_by_role("option", name=month_name).click()

            gender_combobox = page.locator('div#gender div[role="combobox"]')
            await gender_combobox.click()  # open dropdown
            print('gender: ', gender)
            await page.get_by_role("option", name=gender).click()

            # Screenshot after filling
            await page.screenshot(path="birthday_gender_filled.png")
            print("Screenshot saved: birthday_gender_filled.png")

            # Optional: take a screenshot to verify selection
            await page.screenshot(path="gender_male_selected.png")

            next_button = page.locator('button:has-text("Next")')
            await next_button.wait_for(state="visible")
            await next_button.click()
            await page.wait_for_timeout(3000)

            # Wait for username input to appear
            await page.wait_for_selector("input[name='Username']", timeout=5000)
            await page.screenshot(path="username_page.png")

            # Fill dummy username (optional)
            await page.fill("input[name='Username']", username)
            await page.screenshot(path="username_filled.png")

            next_button = page.locator('button:has-text("Next")')
            await next_button.wait_for(state="visible")
            await next_button.click()
            await page.wait_for_timeout(3000)

            # Wait for password page
            await page.wait_for_selector("input[name='Passwd']", timeout=5000)

            # Screenshot password page
            await page.screenshot(path="step_password_page.png")

            # Fill dummy password (optional)
            await page.fill("input[name='Passwd']", password)
            await page.fill("input[name='PasswdAgain']", password)

            await page.screenshot(path="step_password_filled.png")

            await page.get_by_role("button", name="Next").click()

            # Wait a few seconds for the next page to load
            await page.wait_for_timeout(3000)
            await page.screenshot(path="after_next_clicked.png")
            await page.wait_for_timeout(3000)

            await browser.close()
            print("Test finished successfully.")

    except Exception as e:
        print(f"Playwright error: {e}")
