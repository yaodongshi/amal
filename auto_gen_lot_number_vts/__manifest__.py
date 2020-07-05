{
    "name": "Auto Generate Lot Number in Incoming Shipment",
    "version": "13.0.17.10.2019",
    "category": "Purchase",
    "summary": """
	Auto generate Lot no in Incoming Shipment when we have confirm Purchase Order based on Purchase Order Date/Schedule date of Incoming Shipment/Today Date.
	""",
    "author": 'Vraja Technologies',
    'price': 27,
    'currency': 'EUR',
    "depends": ['stock','purchase'],
    "data": [
        'wizard/res_config.xml',
    ],
    'qweb': [],
    'css': [],
    'js': [],
    'images': [
        'static/description/auto_gen_po.jpg',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
