MAIN_CATEGORY_CHOICES = (
    ('drink', '饮料'),
    ('snack', '零食'),
    ('fresh', '新鲜/冷藏'),
    ('main', '主食'),
    ('source', '酱料')
)

SUB_CATEGORY_CHOICES = (
    # 饮料
    ('饮料', (
        ('drink_soft', '软饮料'),
        ('drink_instant_hot', '冲泡热饮'),
        ('drink_alcohol', '酒'),
    )
     ),

    # 零食
    ('饮料', (
        ('snack_mochi', '麻薯'),
    )
     ),

    # 新鲜/冷藏
    ('新鲜/冷藏', (
        ('fresh_veg', '蔬菜'),
        ('fresh_fruit', '水果'),
    )
     ),

    # 主食
    ('主食', (
        ('main_rice', '米谷'),
        ('main_noodles', '面条'),
        ('main_instant_noodles', '方便面'),
        ('main_instant_hot_pot', '自热火锅'),
        ('main_luosifeng', '螺蛳粉'),

    )
     ),

    # 酱料
    ('酱料', (
        ('source_laoganma', '老干妈'),
        ('source_cuihong', '翠红'),

    )
     ),
)
