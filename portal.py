import json
from pathlib import Path
import threading
from decimal import Decimal, InvalidOperation
from local_http import Reply


class Portal:
    def __init__(self):
        self.revision = 1
        self.submissions = 0
        self.lock = threading.Lock()
        self.lines = [
            {'line_id': 'material-17', 'description': '纸箱', 'quantity': '1', 'price': '0', 'tax': 'normal', 'note': ''},
            {'line_id': 'material-42', 'description': '纸箱', 'quantity': '1', 'price': '0', 'tax': 'normal', 'note': ''}]

    def snapshot(self):
        return {'draft': 'D-701', 'revision': self.revision,
                'lines': json.loads(json.dumps(self.lines)), 'submitted': False}

    def save(self, payload):
        with self.lock:
            if payload['revision'] != self.revision:
                return Reply.json({'error': '草稿已被其他人修改', **self.snapshot()}, 409)
            target = next((line for line in self.lines if line['line_id'] == payload['line_id']), None)
            if not target:
                return Reply.json({'error': '物料已不存在'}, 404)
            values = payload['values']
            try:
                if Decimal(values['quantity']) <= 0 or Decimal(values['price']) < 0:
                    raise ValueError('数量应大于零，单价不可为负')
            except (InvalidOperation, KeyError, ValueError):
                return Reply.json({'error': '数量或单价无效'}, 422)
            if values.get('tax') == 'exempt' and not values.get('exemption', '').strip():
                return Reply.json({'error': '请填写免税用途'}, 422)
            permitted = {'quantity', 'price', 'tax', 'note', 'exemption'}
            if set(values) - permitted:
                return Reply.json({'error': '未知字段'}, 422)
            target.update(values)
            self.revision += 1
            return Reply.json(self.snapshot())

    def handle(self, method, path, headers, body):
        if path == '/draft.js':
            return Reply(200, Path('web/draft.js').read_bytes(), {'Content-Type': 'text/javascript'})
        if path == '/login' and method == 'POST':
            return Reply.json({'ok': True}, headers={'Set-Cookie': 'session=local-editor; HttpOnly; SameSite=Strict; Path=/'})
        if path == '/':
            return Reply(200, Path('web/index.html').read_bytes(), {'Content-Type': 'text/html; charset=utf-8'})
        if 'session=local-editor' not in headers.get('Cookie', ''):
            return Reply.json({'error': '需要登录'}, 401)
        if path == '/state':
            return Reply.json(self.snapshot())
        if path == '/save' and method == 'POST':
            return self.save(json.loads(body))
        if path == '/submit' and method == 'POST':
            self.submissions += 1
            return Reply.json({'status': 'submitted'})
        return Reply(404)
