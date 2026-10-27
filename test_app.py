import pathlib
from playwright.sync_api import sync_playwright

def test_app():
    html_path = pathlib.Path("index.html").resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create context with downloads enabled
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto(html_path)

        # 1. Test Google Spreadsheet Integration Guide
        page.click("button:has-text('Settings')")
        page.wait_for_selector("#settingsModal", state="visible")
        assert page.is_visible("text=Petunjuk Lengkap & Kode Google Apps Script")
        page.click("summary:has-text('Petunjuk Lengkap & Kode Google Apps Script')")
        assert page.is_visible("text=Langkah Integrasi Google Spreadsheet")

        # Edit school name in settings
        page.fill("#setSchoolName", "SMKN 1 TEST GONDANG")
        page.click("button:has-text('Simpan Semua')")

        # Take screenshot of settings / main view
        page.screenshot(path="screenshot_settings.png")

        # 2. Test Download HTML saves active state
        with page.expect_download() as download_info:
            page.click("button:has-text('Download HTML')")
        download = download_info.value
        download_path = "downloaded_test.html"
        download.save_as(download_path)

        # Load the downloaded file and check if "SMKN 1 TEST GONDANG" is preserved
        page_downloaded = context.new_page()
        page_downloaded.goto(pathlib.Path(download_path).resolve().as_uri())
        header_text = page_downloaded.inner_text("#headerSchool")
        assert "SMKN 1 TEST GONDANG" in header_text, f"Expected SMKN 1 TEST GONDANG in {header_text}"

        page_downloaded.screenshot(path="screenshot_app.png")
        browser.close()
        print("All Playwright tests passed successfully!")

if __name__ == "__main__":
    test_app()
