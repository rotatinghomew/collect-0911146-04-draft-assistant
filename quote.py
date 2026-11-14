from decimal import Decimal


QUOTE = {'draft': 'D-701', 'revision': 'Q-4', 'lines': [
    {'line_id': 'material-17', 'description': '纸箱', 'quantity': '24', 'price': '3.80', 'tax': 'normal'},
    {'line_id': 'material-42', 'description': '纸箱', 'quantity': '12', 'price': '5.20', 'tax': 'exempt', 'exemption': '农业用途'}]}


def validate_quote(quote):
    identities = [line['line_id'] for line in quote['lines']]
    if len(set(identities)) != len(identities):
        raise ValueError('报价行重复')
    for line in quote['lines']:
        if Decimal(line['quantity']) <= 0 or Decimal(line['price']) < 0:
            raise ValueError('报价数值范围无效')
    return quote
