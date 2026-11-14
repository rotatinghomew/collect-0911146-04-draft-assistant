import json
from local_http import serve
from portal import Portal
from browser_probe import inspect_draft
from quote import QUOTE, validate_quote


def main():
    portal = Portal()
    with serve(portal) as base:
        print(json.dumps({'quote': validate_quote(QUOTE), 'draft': inspect_draft(base),
                          'submissions': portal.submissions}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
