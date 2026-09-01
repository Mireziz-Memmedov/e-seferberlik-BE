# import re

# # =========================================================
# # 1. TEST MƏLUMATLARI (DATA)
# # =========================================================

# QUERIES_DATA = [
#     {
#         'normalized': 'men 3 usagim var toplanisa cagirila bilerem',
#         'keywords': ['usagim', 'toplanisa', 'cagirila', 'bilerem'],
#         'expanded_keywords': ['usagim', 'toplanisa', 'cagirila', 'bilerem', 'toplanis', 'telim', 'aile', 'usaq', 'ovlad', 'cagiris'],
#         'phrases': ['toplanisa cagir', 'toplanisa cagiril', 'usagim toplanisa cagirila', 'toplanisa cagirila bilerem', 'usagim toplanisa', 'toplanisa cagirila', 'cagirila bilerem'],
#         'intents': {'toplanis', 'aile', 'cagiris'},
#         'question_type': 'toplanis_aile',
#         'numbers': ['3'],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'aile veziyyetine gore kimler toplanisdan azad edilir',
#         'keywords': ['aile', 'veziyyetine', 'toplanisdan', 'azad'],
#         'expanded_keywords': ['aile', 'veziyyetine', 'toplanisdan', 'azad', 'toplanis', 'telim', 'usaq', 'ovlad'],
#         'phrases': ['toplanisdan azad', 'aile veziyyeti', 'azad edil', 'aile veziyyetine toplanisdan', 'veziyyetine toplanisdan azad', 'aile veziyyetine', 'veziyyetine toplanisdan'],
#         'intents': {'toplanis', 'aile', 'azadetme'},
#         'question_type': 'toplanis_azadetme',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'universitetde oxuyuram herbi xidmete mohlet verilirmi',
#         'keywords': ['universitetde', 'oxuyuram', 'herbi', 'xidmete', 'mohlet'],
#         'expanded_keywords': ['universitetde', 'oxuyuram', 'herbi', 'xidmete', 'mohlet', 'tehsil', 'telebe'],
#         'phrases': ['mohlet veril', 'universitetde oxuyuram herbi', 'oxuyuram herbi xidmete', 'herbi xidmete mohlet', 'universitetde oxuyuram', 'oxuyuram herbi', 'herbi xidmete', 'xidmete mohlet'],
#         'intents': {'tehsil', 'mohlet', 'herbi_xidmet'},
#         'question_type': 'tehsil_mohlet',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'saglamliq veziyyetine gore herbi xidmete mohlet verile bilermi',
#         'keywords': ['saglamliq', 'veziyyetine', 'herbi', 'xidmete', 'mohlet', 'verile', 'bilermi'],
#         'expanded_keywords': ['saglamliq', 'veziyyetine', 'herbi', 'xidmete', 'mohlet', 'verile', 'bilermi', 'tibbi'],
#         'phrases': ['saglamliq veziyyeti', 'mohlet veril', 'saglamliq veziyyetine herbi', 'veziyyetine herbi xidmete', 'herbi xidmete mohlet', 'xidmete mohlet verile', 'mohlet verile bilermi', 'saglamliq veziyyetine', 'veziyyetine herbi', 'herbi xidmete'],
#         'intents': {'saglamliq', 'mohlet', 'herbi_xidmet'},
#         'question_type': 'saglamliq_mohlet',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'ehtiyatda olan sexs toplanisa cagirila bilermi',
#         'keywords': ['ehtiyatda', 'sexs', 'toplanisa', 'cagirila', 'bilermi'],
#         'expanded_keywords': ['ehtiyatda', 'sexs', 'toplanisa', 'cagirila', 'bilermi', 'toplanis', 'telim', 'ehtiyat', 'cagiris'],
#         'phrases': ['toplanisa cagir', 'toplanisa cagiril', 'ehtiyatda olan', 'ehtiyatda sexs toplanisa', 'sexs toplanisa cagirila', 'toplanisa cagirila bilermi', 'ehtiyatda sexs', 'sexs toplanisa', 'toplanisa cagirila', 'cagirila bilermi'],
#         'intents': {'toplanis', 'ehtiyat', 'cagiris'},
#         'question_type': 'toplanis_ehtiyat',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'madde 46.1.3 neyi nezerde tutur',
#         'keywords': ['madde', '46.1.3', 'neyi', 'nezerde', 'tutur'],
#         'expanded_keywords': ['madde', '46.1.3', 'neyi', 'nezerde', 'tutur'],
#         'phrases': ['madde 46.1.3 neyi', '46.1.3 neyi nezerde', 'neyi nezerde tutur', 'madde 46.1.3', '46.1.3 neyi', 'neyi nezerde', 'nezerde tutur'],
#         'intents': {'article_lookup'},
#         'question_type': 'article',
#         'numbers': ['46.1', '3'],
#         'article_numbers': ['46.1.3']
#     },
#     {
#         'normalized': '3 ve daha cox usagi olan sexsler toplanisdan azaddirmi',
#         'keywords': ['daha', 'cox', 'usagi', 'sexsler', 'toplanisdan', 'azaddirmi'],
#         'expanded_keywords': ['daha', 'cox', 'usagi', 'sexsler', 'toplanisdan', 'azaddirmi', 'toplanis', 'telim', 'aile', 'usaq', 'ovlad'],
#         'phrases': ['toplanisdan azad', 'daha cox usagi', 'cox usagi sexsler', 'usagi sexsler toplanisdan', 'sexsler toplanisdan azaddirmi', 'daha cox', 'cox usagi', 'usagi sexsler', 'sexsler toplanisdan', 'toplanisdan azaddirmi'],
#         'intents': {'toplanis', 'aile', 'azadetme'},
#         'question_type': 'toplanis_azadetme',
#         'numbers': ['3'],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'usagim var meni herbi telime cagira bilerler',
#         'keywords': ['usagim', 'meni', 'herbi', 'telime', 'cagira', 'bilerler'],
#         'expanded_keywords': ['usagim', 'meni', 'herbi', 'telime', 'cagira', 'bilerler', 'toplanis', 'telim', 'aile', 'usaq', 'ovlad', 'cagiris'],
#         'phrases': ['usagim meni herbi', 'meni herbi telime', 'herbi telime cagira', 'telime cagira bilerler', 'usagim meni', 'meni herbi', 'herbi telime', 'telime cagira', 'cagira bilerler'],
#         'intents': {'toplanis', 'telim', 'aile', 'cagiris', 'herbi_xidmet'},
#         'question_type': 'toplanis_aile',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'aile veziyyetine gore toplanisdan azad olunuram',
#         'keywords': ['aile', 'veziyyetine', 'toplanisdan', 'azad', 'olunuram'],
#         'expanded_keywords': ['aile', 'veziyyetine', 'toplanisdan', 'azad', 'olunuram', 'toplanis', 'telim', 'usaq', 'ovlad'],
#         'phrases': ['toplanisdan azad', 'aile veziyyeti', 'aile veziyyetine toplanisdan', 'veziyyetine toplanisdan azad', 'toplanisdan azad olunuram', 'aile veziyyetine', 'veziyyetine toplanisdan', 'azad olunuram'],
#         'intents': {'toplanis', 'aile', 'azadetme'},
#         'question_type': 'toplanis_azadetme',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'ali mektebde tehsil aliram herbi xidmete mohlet dusurmu',
#         'keywords': ['ali', 'mektebde', 'tehsil', 'aliram', 'herbi', 'xidmete', 'mohlet', 'dusurmu'],
#         'expanded_keywords': ['ali', 'mektebde', 'tehsil', 'aliram', 'herbi', 'xidmete', 'mohlet', 'dusurmu', 'telebe'],
#         'phrases': ['ali mektebde tehsil', 'mektebde tehsil aliram', 'tehsil aliram herbi', 'aliram herbi xidmete', 'herbi xidmete mohlet', 'xidmete mohlet dusurmu', 'ali mektebde', 'mektebde tehsil', 'tehsil aliram', 'aliram herbi'],
#         'intents': {'tehsil', 'mohlet', 'herbi_xidmet'},
#         'question_type': 'tehsil_mohlet',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'xesteliye gore herbi xidmete mohlet verile bilermi',
#         'keywords': ['xesteliye', 'herbi', 'xidmete', 'mohlet', 'verile', 'bilermi'],
#         'expanded_keywords': ['xesteliye', 'herbi', 'xidmete', 'mohlet', 'verile', 'bilermi'],
#         'phrases': ['mohlet veril', 'xesteliye herbi xidmete', 'herbi xidmete mohlet', 'xidmete mohlet verile', 'mohlet verile bilermi', 'xesteliye herbi', 'herbi xidmete', 'xidmete mohlet', 'mohlet verile', 'verile bilermi'],
#         'intents': {'saglamliq', 'mohlet', 'herbi_xidmet'},
#         'question_type': 'saglamliq_mohlet',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'ehtiyatda olan sexs toplanisa cagirila bilermi',
#         'keywords': ['ehtiyatda', 'sexs', 'toplanisa', 'cagirila', 'bilermi'],
#         'expanded_keywords': ['ehtiyatda', 'sexs', 'toplanisa', 'cagirila', 'bilermi', 'toplanis', 'telim', 'ehtiyat', 'cagiris'],
#         'phrases': ['toplanisa cagir', 'toplanisa cagiril', 'ehtiyatda olan', 'ehtiyatda sexs toplanisa', 'sexs toplanisa cagirila', 'toplanisa cagirila bilermi', 'ehtiyatda sexs', 'sexs toplanisa', 'toplanisa cagirila', 'cagirila bilermi'],
#         'intents': {'toplanis', 'ehtiyat', 'cagiris'},
#         'question_type': 'toplanis_ehtiyat',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'usagi olan ehtiyatda sexs herbi telime cagirila bilermi',
#         'keywords': ['usagi', 'ehtiyatda', 'sexs', 'herbi', 'telime', 'cagirila', 'bilermi'],
#         'expanded_keywords': ['usagi', 'ehtiyatda', 'sexs', 'herbi', 'telime', 'cagirila', 'bilermi', 'toplanis', 'telim', 'aile', 'usaq', 'ovlad', 'ehtiyat', 'cagiris'],
#         'phrases': ['usagi ehtiyatda sexs', 'ehtiyatda sexs herbi', 'sexs herbi telime', 'herbi telime cagirila', 'telime cagirila bilermi', 'usagi ehtiyatda', 'ehtiyatda sexs', 'sexs herbi', 'herbi telime', 'telime cagirila'],
#         'intents': {'toplanis', 'telim', 'aile', 'ehtiyat', 'cagiris', 'herbi_xidmet'},
#         'question_type': 'toplanis_ehtiyat_aile',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'menim uc usagim var meni toplanisa cagira bilerlermi',
#         'keywords': ['usagim', 'meni', 'toplanisa', 'cagira', 'bilerlermi'],
#         'expanded_keywords': ['usagim', 'meni', 'toplanisa', 'cagira', 'bilerlermi', 'toplanis', 'telim', 'aile', 'usaq', 'ovlad', 'cagiris'],
#         'phrases': ['toplanisa cagir', 'usagim meni toplanisa', 'meni toplanisa cagira', 'toplanisa cagira bilerlermi', 'usagim meni', 'meni toplanisa', 'toplanisa cagira', 'cagira bilerlermi'],
#         'intents': {'toplanis', 'aile', 'cagiris'},
#         'question_type': 'toplanis_aile',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'uc ve daha cox usagi olanlar herbi toplanisdan azaddirlarmi',
#         'keywords': ['daha', 'cox', 'usagi', 'herbi', 'toplanisdan', 'azaddirlarmi'],
#         'expanded_keywords': ['daha', 'cox', 'usagi', 'herbi', 'toplanisdan', 'azaddirlarmi', 'toplanis', 'telim', 'aile', 'usaq', 'ovlad'],
#         'phrases': ['toplanisdan azad', 'daha cox usagi', 'cox usagi herbi', 'usagi herbi toplanisdan', 'herbi toplanisdan azaddirlarmi', 'daha cox', 'cox usagi', 'usagi herbi', 'herbi toplanisdan', 'toplanisdan azaddirlarmi'],
#         'intents': {'toplanis', 'aile', 'azadetme', 'herbi_xidmet'},
#         'question_type': 'toplanis_azadetme',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'tehsil alanlara herbi xidmete mohlet verilirmi',
#         'keywords': ['tehsil', 'alanlara', 'herbi', 'xidmete', 'mohlet'],
#         'expanded_keywords': ['tehsil', 'alanlara', 'herbi', 'xidmete', 'mohlet', 'telebe'],
#         'phrases': ['tehsil alan', 'tehsil alanlar', 'mohlet veril', 'tehsil alanlara herbi', 'alanlara herbi xidmete', 'herbi xidmete mohlet', 'tehsil alanlara', 'alanlara herbi', 'herbi xidmete', 'xidmete mohlet'],
#         'intents': {'tehsil', 'mohlet', 'herbi_xidmet'},
#         'question_type': 'tehsil_mohlet',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'universitet telebeleri herbi xidmetden mohlet ala bilermi',
#         'keywords': ['universitet', 'telebeleri', 'herbi', 'xidmetden', 'mohlet', 'ala', 'bilermi'],
#         'expanded_keywords': ['universitet', 'telebeleri', 'herbi', 'xidmetden', 'mohlet', 'ala', 'bilermi', 'tehsil', 'telebe'],
#         'phrases': ['universitet telebeleri herbi', 'telebeleri herbi xidmetden', 'herbi xidmetden mohlet', 'xidmetden mohlet ala', 'mohlet ala bilermi', 'universitet telebeleri', 'telebeleri herbi', 'herbi xidmetden', 'xidmetden mohlet', 'mohlet ala'],
#         'intents': {'tehsil', 'mohlet', 'herbi_xidmet'},
#         'question_type': 'tehsil_mohlet',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'saglamliq problemi olan sexslere mohlet verilirmi',
#         'keywords': ['saglamliq', 'problemi', 'sexslere', 'mohlet'],
#         'expanded_keywords': ['saglamliq', 'problemi', 'sexslere', 'mohlet', 'tibbi'],
#         'phrases': ['mohlet veril', 'saglamliq problemi sexslere', 'problemi sexslere mohlet', 'saglamliq problemi', 'problemi sexslere', 'sexslere mohlet'],
#         'intents': {'saglamliq', 'mohlet'},
#         'question_type': 'saglamliq_mohlet',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'hansi sexsler herbi toplanislara cagirilir',
#         'keywords': ['sexsler', 'herbi', 'toplanislara', 'cagirilir'],
#         'expanded_keywords': ['sexsler', 'herbi', 'toplanislara', 'cagirilir', 'toplanis', 'telim', 'cagiris'],
#         'phrases': ['toplanislara cagir', 'sexsler herbi toplanislara', 'herbi toplanislara cagirilir', 'sexsler herbi', 'herbi toplanislara', 'toplanislara cagirilir'],
#         'intents': {'toplanis', 'cagiris', 'herbi_xidmet'},
#         'question_type': 'toplanis',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'toplanislardan kimler azad edilir',
#         'keywords': ['toplanislardan', 'azad'],
#         'expanded_keywords': ['toplanislardan', 'azad', 'toplanis', 'telim'],
#         'phrases': ['azad edil', 'toplanislardan azad'],
#         'intents': {'toplanis', 'azadetme'},
#         'question_type': 'toplanis_azadetme',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'ehtiyatda olan herbi vezifeliler telime cagirilirmi',
#         'keywords': ['ehtiyatda', 'herbi', 'vezifeliler', 'telime', 'cagirilirmi'],
#         'expanded_keywords': ['ehtiyatda', 'herbi', 'vezifeliler', 'telime', 'cagirilirmi', 'toplanis', 'telim', 'ehtiyat'],
#         'phrases': ['ehtiyatda olan', 'ehtiyatda herbi vezifeliler', 'herbi vezifeliler telime', 'vezifeliler telime cagirilirmi', 'ehtiyatda herbi', 'herbi vezifeliler', 'vezifeliler telime', 'telime cagirilirmi'],
#         'intents': {'toplanis', 'telim', 'ehtiyat', 'cagiris', 'herbi_xidmet'},
#         'question_type': 'toplanis_ehtiyat',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'madde 46 nedir',
#         'keywords': ['madde'],
#         'expanded_keywords': ['madde'],
#         'phrases': [],
#         'intents': {'article_lookup'},
#         'question_type': 'article',
#         'numbers': ['46'],
#         'article_numbers': ['46']
#     },
#     {
#         'normalized': '46.1.3 maddesinde ne yazilib',
#         'keywords': ['46.1.3', 'maddesinde', 'yazilib'],
#         'expanded_keywords': ['46.1.3', 'maddesinde', 'yazilib'],
#         'phrases': ['46.1.3 maddesinde yazilib', '46.1.3 maddesinde', 'maddesinde yazilib'],
#         'intents': {'article_lookup'},
#         'question_type': 'article',
#         'numbers': ['46.1', '3'],
#         'article_numbers': ['46.1.3', '3']
#     },
#     {
#         'normalized': 'madde 19.1.2 neyi nezerde tutur',
#         'keywords': ['madde', '19.1.2', 'neyi', 'nezerde', 'tutur'],
#         'expanded_keywords': ['madde', '19.1.2', 'neyi', 'nezerde', 'tutur'],
#         'phrases': ['madde 19.1.2 neyi', '19.1.2 neyi nezerde', 'neyi nezerde tutur', 'madde 19.1.2', '19.1.2 neyi', 'neyi nezerde', 'nezerde tutur'],
#         'intents': {'article_lookup'},
#         'question_type': 'article',
#         'numbers': ['19.1', '2'],
#         'article_numbers': ['19.1.2']
#     },
#     {
#         'normalized': 'uc usagim oldugu ucun herbi toplanisa getmeye bilerem',
#         'keywords': ['usagim', 'herbi', 'toplanisa', 'getmeye', 'bilerem'],
#         'expanded_keywords': ['usagim', 'herbi', 'toplanisa', 'getmeye', 'bilerem', 'toplanis', 'telim', 'aile', 'usaq', 'ovlad'],
#         'phrases': ['usagim herbi toplanisa', 'herbi toplanisa getmeye', 'toplanisa getmeye bilerem', 'usagim herbi', 'herbi toplanisa', 'toplanisa getmeye', 'getmeye bilerem'],
#         'intents': {'toplanis', 'aile', 'herbi_xidmet'},
#         'question_type': 'toplanis_aile',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'menim aile veziyyetim toplanisa cagirilmagima tesir edir',
#         'keywords': ['aile', 'veziyyetim', 'toplanisa', 'cagirilmagima', 'tesir', 'edir'],
#         'expanded_keywords': ['aile', 'veziyyetim', 'toplanisa', 'cagirilmagima', 'tesir', 'edir', 'toplanis', 'telim', 'usaq', 'ovlad'],
#         'phrases': ['toplanisa cagir', 'toplanisa cagiril', 'aile veziyyeti', 'aile veziyyetim toplanisa', 'veziyyetim toplanisa cagirilmagima', 'toplanisa cagirilmagima tesir', 'cagirilmagima tesir edir', 'aile veziyyetim', 'veziyyetim toplanisa', 'toplanisa cagirilmagima'],
#         'intents': {'toplanis', 'aile', 'cagiris'},
#         'question_type': 'toplanis_aile',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'tehsil sebebinden toplanisa mohlet verilirmi',
#         'keywords': ['tehsil', 'sebebinden', 'toplanisa', 'mohlet'],
#         'expanded_keywords': ['tehsil', 'sebebinden', 'toplanisa', 'mohlet', 'toplanis', 'telim', 'telebe'],
#         'phrases': ['mohlet veril', 'tehsil sebebinden toplanisa', 'sebebinden toplanisa mohlet', 'tehsil sebebinden', 'sebebinden toplanisa', 'toplanisa mohlet'],
#         'intents': {'toplanis', 'tehsil', 'mohlet'},
#         'question_type': 'tehsil_mohlet',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'xestelik sebebinden toplanisdan azad ola bilerem',
#         'keywords': ['xestelik', 'sebebinden', 'toplanisdan', 'azad', 'ola', 'bilerem'],
#         'expanded_keywords': ['xestelik', 'sebebinden', 'toplanisdan', 'azad', 'ola', 'bilerem', 'toplanis', 'telim', 'saglamliq', 'tibbi'],
#         'phrases': ['toplanisdan azad', 'xestelik sebebinden toplanisdan', 'sebebinden toplanisdan azad', 'toplanisdan azad ola', 'azad ola bilerem', 'xestelik sebebinden', 'sebebinden toplanisdan', 'azad ola', 'ola bilerem'],
#         'intents': {'toplanis', 'azadetme', 'saglamliq'},
#         'question_type': 'toplanis_azadetme',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'ehtiyatda olan uc usaqli sexs toplanisa cagirila bilermi',
#         'keywords': ['ehtiyatda', 'usaqli', 'sexs', 'toplanisa', 'cagirila', 'bilermi'],
#         'expanded_keywords': ['ehtiyatda', 'usaqli', 'sexs', 'toplanisa', 'cagirila', 'bilermi', 'toplanis', 'telim', 'ehtiyat', 'cagiris'],
#         'phrases': ['toplanisa cagir', 'toplanisa cagiril', 'ehtiyatda olan', 'ehtiyatda usaqli sexs', 'usaqli sexs toplanisa', 'sexs toplanisa cagirila', 'toplanisa cagirila bilermi', 'ehtiyatda usaqli', 'usaqli sexs', 'sexs toplanisa'],
#         'intents': {'toplanis', 'ehtiyat', 'cagiris', 'aile'},
#         'question_type': 'toplanis_ehtiyat_aile',
#         'numbers': [],
#         'article_numbers': []
#     },
#     {
#         'normalized': 'herbi xidmete cagiris ile herbi telime cagiris eynidirmi',
#         'keywords': ['herbi', 'xidmete', 'cagiris', 'telime', 'eynidirmi'],
#         'expanded_keywords': ['herbi', 'xidmete', 'cagiris', 'telime', 'eynidirmi', 'toplanis', 'telim'],
#         'phrases': ['herbi xidmete cagiris', 'xidmete cagiris herbi', 'cagiris herbi telime', 'herbi telime cagiris', 'telime cagiris eynidirmi', 'herbi xidmete', 'xidmete cagiris', 'cagiris herbi', 'herbi telime', 'telime cagiris'],
#         'intents': {'toplanis', 'telim', 'cagiris', 'herbi_xidmet'},
#         'question_type': 'toplanis',
#         'numbers': [],
#         'article_numbers': []
#     }
# ]

# # =========================================================
# # 2. İNTENT SÖZLÜKLƏRİ (DICTIONARIES)
# # =========================================================

# INTENT_KEYWORDS = {
#     "toplanis": {
#         "toplanis", "toplanisa", "toplanisdan", "toplanislara", 
#         "toplanislardan", "toplanislar", "toplanisim"
#     },
#     "telim": {
#         "telim", "telime", "telimlere", "telimden", "telimleri"
#     },
#     "cagiris": {
#         "cagiris", "cagira", "cagirilir", "cagirila", "cagirilmaga",
#         "cagirilmagi", "cagirilmagima", "cagirilib", "cagirilirler", "cagirilirmi"
#     },
#     "aile": {
#         "aile", "usag", "usaq", "usagi", "usagim", "usaqli", "ovlad", "ovladi"
#     },
#     "ehtiyat": {
#         "ehtiyat", "ehtiyatda", "ehtiyatci"
#     },
#     "azadetme": {
#         "azad", "azaddirmi", "azaddirlarmi", "azadlik"
#     },
#     "mohlet": {
#         "mohlet"
#     },
#     "tehsil": {
#         "tehsil", "telebe", "telebeleri", "universitet", 
#         "universitetde", "mekteb", "mektebde", "oxuyuram"
#     },
#     "saglamliq": {
#         "saglamliq", "xestelik", "xesteliye", "xesteliyi", 
#         "xeste", "tibbi", "xesteliy", "problemi"
#     },
#     "herbi_xidmet": {
#         "herbi", "xidmet", "xidmete", "xidmetden"
#     },
# }

# INTENT_PHRASES = {
#     "toplanis": {
#         "herbi toplanis", "herbi toplanisa", "herbi toplanisdan",
#         "herbi toplanislara", "herbi toplanislardan"
#     },
#     "telim": {
#         "herbi telim", "herbi telime", "herbi telimlere"
#     },
#     "cagiris": {
#         "herbi xidmete cagiris", "herbi telime cagiris", "toplanisa cagir",
#         "toplanisa cagiril", "telime cagira", "telime cagiril"
#     },
#     "azadetme": {
#         "toplanisdan azad", "toplanislardan azad", "azad edilir",
#         "azad olunur", "azad olunuram", "azad ola"
#     },
#     "mohlet": {
#         "herbi xidmete mohlet", "mohlet veril", "mohlet ala", "mohlet dusur"
#     },
#     "tehsil": {
#         "universitetde oxuyuram", "ali mektebde tehsil", "ali mekteb",
#         "tehsil alan", "universitet telebeleri"
#     },
#     "saglamliq": {
#         "saglamliq veziyyeti", "saglamliq problemi", "xesteliye gore",
#         "xestelik sebebinden"
#     },
#     "aile": {
#         "aile veziyyeti", "aile veziyyetine", "uc usagim",
#         "uc ve daha cox usagi", "daha cox usagi"
#     },
#     "ehtiyat": {
#         "ehtiyatda olan"
#     },
#     "herbi_xidmet": {
#         "herbi xidmet", "herbi xidmete", "herbi xidmetden"
#     },
# }

# # =========================================================
# # 3. İNTENT VƏ SUAL NÖVÜNÜN TƏYİN EDİLMƏSİ MƏNTİQİ
# # =========================================================

# def detect_question_type(intents: set[str], article_numbers: list[str] | None = None) -> str:
#     """İntent-lər və maddə nömrələri əsasında əsas question_type müəyyən edir."""
#     if article_numbers or "article_lookup" in intents:
#         return "article"

#     if "toplanis" in intents or "telim" in intents:
#         if "ehtiyat" in intents and "aile" in intents:
#             return "toplanis_ehtiyat_aile"
#         if "azadetme" in intents:
#             return "toplanis_azadetme"
#         if "aile" in intents:
#             return "toplanis_aile"
#         if "ehtiyat" in intents:
#             return "toplanis_ehtiyat"
#         if "tehsil" in intents and "mohlet" in intents:
#             return "tehsil_mohlet"
#         return "toplanis"

#     if "tehsil" in intents and "mohlet" in intents:
#         return "tehsil_mohlet"

#     if "saglamliq" in intents and "mohlet" in intents:
#         return "saglamliq_mohlet"

#     if "mohlet" in intents:
#         return "mohlet"

#     for single in ("tehsil", "saglamliq", "aile", "ehtiyat", "azadetme", "cagiris", "herbi_xidmet"):
#         if single in intents:
#             return single

#     return "general"


# def detect_intents(
#     normalized: str,
#     keywords: list[str] | None = None,
#     phrases: list[str] | None = None,
#     article_numbers: list[str] | None = None,
# ) -> set[str]:
#     """Mətn, açar sözlər və frazalar əsasında intent-ləri müəyyən edir."""
#     intents = set()

#     keywords = keywords or []
#     phrases = phrases or []
#     article_numbers = article_numbers or []

#     keyword_set = set(keywords)
#     phrase_set = set(phrases)

#     # 1. Maddə nömrəsi / Mətn Yoxlaması
#     has_digits = bool(re.search(r"\b\d+(?:\.\d+)*\b", normalized))
#     if article_numbers or "madde" in normalized or has_digits:
#         intents.add("article_lookup")

#     # 2. Keyword əsaslı uyğunlaşma
#     for intent, words in INTENT_KEYWORDS.items():
#         if keyword_set.intersection(words):
#             intents.add(intent)

#     # 3. Phrase əsaslı uyğunlaşma
#     for intent, intent_phrases in INTENT_PHRASES.items():
#         if phrase_set.intersection(intent_phrases):
#             intents.add(intent)

#     # 4. Dinamik Kök (Stemming) və Mətn Yoxlaması
#     all_text = normalized.split()
#     for word in keyword_set.union(all_text):
#         if word.startswith(("xestel", "xeste", "saglam")):
#             intents.add("saglamliq")
#         elif word.startswith(("usaq", "usag", "ovlad")):
#             intents.add("aile")
#         elif word.startswith("ehtiyat"):
#             intents.add("ehtiyat")
#         elif word.startswith("toplanis"):
#             intents.add("toplanis")
#         elif word.startswith("telim"):
#             intents.add("telim")
#         elif word.startswith("cagir"):
#             intents.add("cagiris")
#         elif word.startswith(("telebe", "universitet", "tehsil")):
#             intents.add("tehsil")
#         elif word.startswith("mohlet"):
#             intents.add("mohlet")
#         elif word.startswith("azad"):
#             intents.add("azadetme")

#     return intents


# def analyze_intent(
#     normalized: str,
#     keywords: list[str] | None = None,
#     phrases: list[str] | None = None,
#     article_numbers: list[str] | None = None,
# ) -> dict:
#     """Əsas analiz funksiyası."""
#     intents = detect_intents(
#         normalized=normalized,
#         keywords=keywords,
#         phrases=phrases,
#         article_numbers=article_numbers,
#     )

#     question_type = detect_question_type(intents, article_numbers=article_numbers)

#     return {
#         "intents": intents,
#         "question_type": question_type,
#     }


# # =========================================================
# # 4. İCRA VƏ YOXLEMA (EXECUTION)
# # =========================================================

# if __name__ == "__main__":
#     print("--- Sorğuların Analiz Nəticələri ---\n")
#     for item in QUERIES_DATA:
#         result = analyze_intent(
#             normalized=item["normalized"],
#             keywords=item.get("keywords"),
#             phrases=item.get("phrases"),
#             article_numbers=item.get("article_numbers")
#         )
#         print(f"Sual: {item['normalized']}")
#         print(f"Tapılan Intent-lər: {result['intents']}")
#         print(f"Sual Tipi: {result['question_type']}")
#         print("-" * 50)