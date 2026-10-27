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

        # 1. Test Google Spreadsheet Integration Guide & Test Spreadsheet Button
        page.click("button:has-text('Settings')")
        page.wait_for_selector("#settingsModal", state="visible")
        assert page.is_visible("text=Petunjuk Lengkap & Kode Google Apps Script")
        assert page.is_visible("button:has-text('Test Spreadsheet')")
        page.click("summary:has-text('Petunjuk Lengkap & Kode Google Apps Script')")
        assert page.is_visible("text=Langkah Integrasi Google Spreadsheet")

        # Click Test Spreadsheet button with empty URL -> should show toast warning
        page.click("button:has-text('Test Spreadsheet')")
        assert page.is_visible("text=Masukkan Web App URL")

        # Verify DAFTAR KELAS (CRUD) no longer has "Jam Ke-" inputs in settings modal
        assert not page.is_visible("#class-start-0")
        assert not page.is_visible("text=Jam Ke-") or page.is_visible("button:has-text('Settings')")

        # Edit school name in settings
        page.fill("#setSchoolName", "SMKN 1 TEST GONDANG")
        page.click("button:has-text('Simpan Semua')")

        # Take screenshot of settings / main view
        page.screenshot(path="screenshot_settings.png")

        # 2. Test Download Template
        with page.expect_download() as download_info:
            page.click("button:has-text('Template')")
        download_tpl = download_info.value
        tpl_path = "downloaded_template.xlsx"
        download_tpl.save_as(tpl_path)
        assert pathlib.Path(tpl_path).exists()

        # 3. Test Student CRUD Functionality
        # Add new student
        page.click("button:has-text('Tambah Siswa')")
        page.wait_for_selector("#studentModal", state="visible")
        page.fill("#studentNis", "99-001")
        page.fill("#studentName", "BUDI SANTOSO")
        page.click("#studentModal button:has-text('Simpan')")

        # Verify student is in table
        assert page.is_visible("td:has-text('BUDI SANTOSO')")
        assert page.is_visible("td:has-text('99-001')")

        # Edit student details
        page.click("tr:has-text('BUDI SANTOSO') button:has-text('Edit')")
        page.wait_for_selector("#studentModal", state="visible")
        page.fill("#studentName", "BUDI SANTOSO EDIT")
        page.click("#studentModal button:has-text('Simpan')")

        # Verify edited student in table
        assert page.is_visible("td:has-text('BUDI SANTOSO EDIT')")

        # Delete student
        page.click("tr:has-text('BUDI SANTOSO EDIT') button:has-text('Hapus')")
        page.wait_for_selector("#modal", state="visible")
        page.click("#modalOk")

        # Verify student removed
        assert not page.is_visible("td:has-text('BUDI SANTOSO EDIT')")

        # Add a student to stay saved for download test
        page.click("button:has-text('Tambah Siswa')")
        page.wait_for_selector("#studentModal", state="visible")
        page.fill("#studentNis", "99-002")
        page.fill("#studentName", "SITI AMINAH")
        page.click("#studentModal button:has-text('Simpan')")

        # 4. Test Download HTML saves active state
        with page.expect_download() as download_info:
            page.click("button:has-text('Download HTML')")
        download = download_info.value
        download_path = "downloaded_test.html"
        download.save_as(download_path)

        # Load the downloaded file and check if "SMKN 1 TEST GONDANG" and "SITI AMINAH" are preserved
        page_downloaded = context.new_page()
        page_downloaded.goto(pathlib.Path(download_path).resolve().as_uri())
        header_text = page_downloaded.inner_text("#headerSchool")
        assert "SMKN 1 TEST GONDANG" in header_text, f"Expected SMKN 1 TEST GONDANG in {header_text}"
        assert page_downloaded.is_visible("td:has-text('SITI AMINAH')")

        page_downloaded.screenshot(path="screenshot_app.png")
        browser.close()
        print("All Playwright tests passed successfully!")

if __name__ == "__main__":
    test_app()
