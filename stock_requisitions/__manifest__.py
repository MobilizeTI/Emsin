# -*- coding: utf-8 -*-
{
    "name": "Stock Prestamos",
    "version": "14",
    "author": "Mobilize (Jorge Quico)",
    'category': 'Mobilize/Apps',
    "application": True,
    "depends": [ "base", "stock" ],
    "data": [
        #"security/ir.model.access.csv",
        "views/product_template.xml",
        "views/stock_picking_type.xml",
        "views/stock_picking.xml",
    ],
    "summary": "Añade funcionalidad para entrega de productos al personal y devolución de los mismos",
    "description": """
        Añade funcionalidad para entrega de productos al personal y devolución de los mismos
    """
}
