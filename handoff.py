def summarize(events):
    return {'draft': events[0]['draft'] if events else None,
            'fields': [{key: value for key, value in event.items() if key != 'session'} for event in events],
            'submitted': False}
