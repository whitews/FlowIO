"""
FCS keyword strings
"""

# FCS 3.1 reserves certain keywords as being part of the FCS standard. Some
# of these are required, and others are optional. However, all of these
# keywords shall be prefixed by the '$' character. No other keywords shall
# begin with the '$' character. All keywords are case-insensitive, however
# most cytometers use all uppercase for keyword strings. FlowKit follows
# the convention used in FlowIO and internally stores and references all
# FCS keywords as lowercase for more convenient typing by developers.
#
# NOTE: When creating new FCS files, some keywords (and values) are set
#    automatically by the create_fcs function. The standard list of
#    keywords will be ignored if included in the metadata passed to
#    the create_fcs function.
#
# noinspection SpellCheckingInspection
FCS_STANDARD_REQUIRED_KEYWORDS = [
    'beginanalysis',
    'begindata',
    'beginstext',
    'byteord',
    'datatype',
    'endanalysis',
    'enddata',
    'endstext',
    'mode',
    'nextdata',
    'par',
    'tot'
]

FCS_STANDARD_OPTIONAL_KEYWORDS = [
    'abrt',
    'btim',
    'cells',
    'com',
    'csmode',
    'csvbits',
    'cyt',
    'cytsn',
    'date',
    'etim',
    'exp',
    'fil',
    'gate',
    'inst',
    'last_modified',
    'last_modifier',
    'lost',
    'op',
    'originality',
    'plateid',
    'platename',
    'proj',
    'smno',
    'spillover',
    'src',
    'sys',
    'timestep',
    'tr',
    'vol',
    'wellid'
]

FCS_STANDARD_KEYWORDS = FCS_STANDARD_REQUIRED_KEYWORDS + FCS_STANDARD_OPTIONAL_KEYWORDS
