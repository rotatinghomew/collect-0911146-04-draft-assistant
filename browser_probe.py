from playwright.sync_api import sync_playwright


def inspect_draft(base):
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(args=['--no-sandbox'])
        try:
            page = browser.new_page()
            page.goto(base)
            page.get_by_role('textbox', name='账号').fill('buyer')
            page.get_by_label('密码').fill('local-only')
            page.get_by_role('button', name='登录', exact=True).click()
            page.locator('#editor').wait_for(state='visible')
            return {'draft': 'D-701', 'revision': page.locator('#revision').inner_text(),
                    'line_ids': page.locator('tr[data-line-id]').evaluate_all('(rows) => rows.map(row => row.dataset.lineId)')}
        finally:
            browser.close()
