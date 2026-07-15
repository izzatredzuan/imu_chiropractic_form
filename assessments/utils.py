# Check if a clinician is read-only for a given assessment
from multiprocessing import context

from playwright.sync_api import sync_playwright


def clinician_is_readonly(profile, assessment):
    """
    A clinician is read-only if they are NOT the assigned evaluator.
    """
    return (
        profile.role == "clinician"
        and assessment is not None
        and assessment.evaluator != profile
    )


# Check if assessment section has all required fields filled
def is_section_complete(obj, fields):
    for field in fields:
        value = getattr(obj, field)
        if value is None:
            return False

        if isinstance(value, str) and value.strip() == "":
            return False
    return True


def generate_pdf(url, cookies=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context(
            viewport={
                "width": 1440,
                "height": 1200,
            }
        )

        if cookies:
            context.add_cookies(cookies)

        page = context.new_page()
        page.emulate_media(media="print")

        response = page.goto(
            url,
            wait_until="networkidle"
        )

        print("========== PDF DEBUG ==========")
        print("Requested URL:", url)
        print("Final URL:", page.url)
        print("Status:", response.status if response else None)
        print("Title:", page.title())
        print("Cookies inside browser:")
        print(context.cookies())
        print("===============================")

        page.wait_for_function(
            "window.pdfReady === true",
            timeout=60000
        )

        pdf = page.pdf(
            format="A4",
            print_background=True,
            margin={
                "top": "15mm",
                "bottom": "15mm",
                "left": "12mm",
                "right": "12mm",
            }
        )
        browser.close()

        return pdf
