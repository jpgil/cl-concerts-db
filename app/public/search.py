from app.public.test_db import TEST, TEST2


def event_list_PREVIO(keywords="", offset=0, limit=10):
    # return { 'rows': TEST , 'total': 100 }
    T = { "rows": TEST2['rows'][offset:offset+limit], 'total': len(TEST2['rows']) }
    return T

# Return a raw set of events paginated
def event_list(keywords="", offset=0, limit=10):
    T = TEST[:]
    return T
