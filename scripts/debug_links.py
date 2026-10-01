from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    page.goto('http://localhost:8501', wait_until='networkidle')
    page.wait_for_timeout(3000)
    links = page.eval_on_selector_all(
        'a, [data-testid="stSidebarNavLink"]',
        'els => els.map(e => ({tag: e.tagName, text: e.innerText, href: e.getAttribute("href")}))'
    )
    for lnk in links:
        print(ascii(lnk))
    b.close()
