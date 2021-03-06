import unittest.mock as mock

import cdx_toolkit

# useful for debugging:
import logging
logging.basicConfig(level='INFO')


def test_apply_cc_defaults():
    mock_now = 1524962339.157388
    assert cdx_toolkit.time_to_timestamp(mock_now) == '20180429003859'
    with mock.patch('time.time', return_value=mock_now):
        params = {}
        cdx_toolkit.apply_cc_defaults(params)
        assert 'from_ts' in params
        assert params['from_ts'] == '20170429003859'  # one year earlier
        assert len(params) == 1

    params = {'to': '201804'}
    cdx_toolkit.apply_cc_defaults(params)
    assert 'from_ts' in params
    assert len(params) == 2

    params = {'from_ts': '201801', 'to': '201804'}
    cdx_toolkit.apply_cc_defaults(params)
    assert len(params) == 2


my_cc_endpoints = [
    'http://index.commoncrawl.org/CC-MAIN-2013-20-index',
    'http://index.commoncrawl.org/CC-MAIN-2017-51-index',
    'http://index.commoncrawl.org/CC-MAIN-2018-05-index',
    'http://index.commoncrawl.org/CC-MAIN-2018-09-index',
    'http://index.commoncrawl.org/CC-MAIN-2018-13-index',
]


def test_customize_index_list():
    tests = [
        # gets the whole list because 201704 is before the first 2017 index
        [{'to': '201804'}, list(reversed(my_cc_endpoints))],
        [{'from_ts': '201801', 'to': '201804'}, my_cc_endpoints[4:0:-1]],
        [{'from_ts': '20180214', 'to': '201804'}, my_cc_endpoints[4:1:-1]],
        [{'from_ts': '20180429', 'to': '20180430'}, my_cc_endpoints[4:5]],
        # perhaps this next one should raise...
        [{'from_ts': '20180430', 'to': '20180429'}, my_cc_endpoints[4:5]],
    ]

    with mock.patch('cdx_toolkit.get_cc_endpoints', return_value=my_cc_endpoints):
        cdx = cdx_toolkit.CDXFetcher(source='cc')
        cdxa = cdx_toolkit.CDXFetcher(source='cc', cc_sort='ascending')

        for params, custom_list in tests:
            cdx_toolkit.apply_cc_defaults(params)
            assert cdx.customize_index_list(params) == custom_list
            assert cdxa.customize_index_list(params) == list(reversed(custom_list))


def test_customize_index_list_closest():
    # when I implement the funky sort order, this will become different
    my_cc_endpoints_rev = list(reversed(my_cc_endpoints))
    tests = [
        [{'closest': '201801', 'from_ts': '20171230', 'to': None}, my_cc_endpoints_rev[0:4]],
        [{'closest': '201803', 'from_ts': '20180214', 'to': None}, my_cc_endpoints_rev[0:3]],
        [{'closest': '201801', 'from_ts': '20171230', 'to': '201802'}, my_cc_endpoints_rev[2:4]],
    ]

    with mock.patch('cdx_toolkit.get_cc_endpoints', return_value=my_cc_endpoints):
        cdx = cdx_toolkit.CDXFetcher(source='cc')

        for params, custom_list in tests:
            cdx_toolkit.apply_cc_defaults(params)
            print(params)
            assert cdx.customize_index_list(params) == custom_list
