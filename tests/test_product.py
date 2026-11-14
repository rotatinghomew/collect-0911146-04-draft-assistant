import json
import unittest
from local_http import serve
from portal import Portal
from browser_probe import inspect_draft
from playwright.sync_api import sync_playwright


class PortalTests(unittest.TestCase):
    def test_visible_probe_preserves_draft(self):
        portal = Portal()
        with serve(portal) as base:
            self.assertEqual(inspect_draft(base)['line_ids'], ['material-17', 'material-42'])
        self.assertEqual(portal.revision, 1)
        self.assertEqual(portal.submissions, 0)

    def test_revision_conflict_is_not_a_save(self):
        portal = Portal()
        result = portal.save({'revision': 0, 'line_id': 'material-17', 'values': {'quantity': '2', 'price': '1'}})
        self.assertEqual(result.status, 409)
        self.assertEqual(portal.revision, 1)

    def test_browser_branch_validation_and_save(self):
        portal = Portal()
        with serve(portal) as base, sync_playwright() as runtime:
            browser = runtime.chromium.launch(args=['--no-sandbox'])
            try:
                page = browser.new_page()
                page.goto(base)
                page.get_by_label('账号').fill('buyer')
                page.get_by_label('密码').fill('local')
                page.get_by_role('button', name='登录', exact=True).click()
                row = page.locator('[data-line-id="material-42"]')
                row.locator('select').select_option('exempt')
                row.get_by_role('button').click()
                page.get_by_text('请填写免税用途', exact=True).wait_for()
                self.assertEqual(portal.revision, 1)
                row.get_by_label('免税用途').fill('农业用途')
                row.get_by_role('button').click()
                page.get_by_text('已保存 material-42 修订 2', exact=True).wait_for()
                self.assertEqual(portal.lines[1]['exemption'], '农业用途')
                self.assertEqual(portal.submissions, 0)
            finally:
                browser.close()
