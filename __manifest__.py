{
    'name': "Arkamen",
    'summary': "Module Odoo untuk melakukan manajemen terhadap SDM di PT. Arkamaya",
    'description': 'Module Odoo untuk melakukan manajemen terhadap profil SDM, ketersediaan SDM, alokasi proyek terhadap SDM, penyedia freelancer, dan laporan utilisasi SDM',
    'sequence': -101,
    'author': "Barkelona",
    'category': "Uncategorized",
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'security/usertype.xml',
        'security/ir.model.access.csv',
        'security/ir.rules.xml',
        'views/allocation_forms.xml',
        'views/project_forms.xml',
        'views/vendor_forms.xml',
        'views/external_user_forms.xml',
        'views/internal_user_forms.xml',
        'views/allocation_trees.xml',
        'views/project_trees.xml',
        'views/vendor_trees.xml',
        'views/external_user_trees.xml',
        'views/internal_user_trees.xml',
        'views/utilization_report_views.xml',
        'views/user_menus.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
}