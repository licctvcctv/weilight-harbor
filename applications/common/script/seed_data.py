import json
import random
import datetime
import click
from flask.cli import with_appcontext
from applications.extensions import db
from applications.models import User, Role, Power
from applications.models.sensitive_word import SensitiveWord
from applications.models.post import Post
from applications.models.comment import Comment
from applications.models.post_like import PostLike
from applications.models.confession import Confession
from applications.models.campaign import Campaign
from applications.models.donation import Donation
from applications.models.journal_entry import JournalEntry
from applications.models.respite_request import RespiteRequest
from applications.models.certification import Certification


@click.command('seed')
@with_appcontext
def seed_command():
    """Seed initial data."""
    _seed_roles()
    _seed_admin()
    _seed_admin_powers()
    _seed_sensitive_words()
    click.echo('Base seed data created.')


@click.command('seed-demo')
@with_appcontext
def seed_demo_command():
    """Seed rich demo data for testing."""
    _seed_roles()
    _seed_admin()
    _seed_admin_powers()
    _seed_sensitive_words()
    _seed_users()
    _seed_certifications()
    _seed_posts()
    _seed_comments()
    _seed_confessions()
    _seed_campaigns()
    _seed_donations()
    _seed_journal_entries()
    _seed_respite_requests()
    click.echo('Demo data seeded successfully! 🎉')
    click.echo('---')
    click.echo('Test accounts:')
    click.echo('  admin / admin123        (Administrator)')
    click.echo('  limei / test123         (Certified Family)')
    click.echo('  zhangwei / test123      (Regular User)')
    click.echo('  wangfang / test123      (Certified Volunteer)')
    click.echo('  chenyun / test123       (Certified Family)')
    click.echo('  liuyang / test123       (Regular User)')


def _seed_roles():
    roles_data = [
        {'name': 'Regular User', 'code': 'regular', 'enable': 1, 'remark': 'Default role for new users', 'sort': 1},
        {'name': 'Certified Family', 'code': 'certified_family', 'enable': 1, 'remark': 'Verified family caregiver', 'sort': 2},
        {'name': 'Certified Volunteer', 'code': 'certified_volunteer', 'enable': 1, 'remark': 'Verified volunteer', 'sort': 3},
        {'name': 'Administrator', 'code': 'admin', 'enable': 1, 'remark': 'Platform administrator', 'sort': 4},
    ]
    for rd in roles_data:
        if not Role.query.filter_by(code=rd['code']).first():
            db.session.add(Role(**rd))
    db.session.commit()


def _seed_admin():
    admin_role = Role.query.filter_by(code='admin').first()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', realname='Administrator', enable=1,
                     user_type='admin', email='admin@weilight.org', is_certified=True)
        admin.set_password('admin123')
        admin.role.append(admin_role)
        db.session.add(admin)
        db.session.commit()


def _seed_admin_powers():
    """Create minimum admin menu and review permissions used by custom modules."""
    admin_role = Role.query.filter_by(code='admin').first()
    if not admin_role:
        return

    def upsert_power(code, **kwargs):
        power = Power.query.filter_by(code=code).first()
        if power:
            for key, value in kwargs.items():
                setattr(power, key, value)
        else:
            power = Power(code=code, **kwargs)
            db.session.add(power)
        db.session.flush()
        if power not in admin_role.power:
            admin_role.power.append(power)
        return power

    review_parent = upsert_power(
        'admin:review',
        name='Review Management',
        type='0',
        url='',
        open_type='_iframe',
        parent_id=0,
        icon='layui-icon layui-icon-survey',
        sort=20,
        enable=1
    )

    upsert_power(
        'admin:certification:main',
        name='Certification Review',
        type='1',
        url='/admin/certification/',
        open_type='_iframe',
        parent_id=review_parent.id,
        icon='layui-icon layui-icon-vercode',
        sort=10,
        enable=1
    )
    upsert_power(
        'admin:certification:edit',
        name='Edit Certification Review',
        type='2',
        url='',
        open_type='',
        parent_id=review_parent.id,
        icon='',
        sort=11,
        enable=1
    )
    upsert_power(
        'admin:campaign:main',
        name='Campaign Review',
        type='1',
        url='/admin/campaign-review/',
        open_type='_iframe',
        parent_id=review_parent.id,
        icon='layui-icon layui-icon-rmb',
        sort=20,
        enable=1
    )
    upsert_power(
        'admin:campaign:edit',
        name='Edit Campaign Review',
        type='2',
        url='',
        open_type='',
        parent_id=review_parent.id,
        icon='',
        sort=21,
        enable=1
    )
    upsert_power(
        'admin:community:main',
        name='Community Moderation',
        type='1',
        url='/admin/community/',
        open_type='_iframe',
        parent_id=review_parent.id,
        icon='layui-icon layui-icon-dialogue',
        sort=30,
        enable=1
    )
    upsert_power(
        'admin:community:edit',
        name='Edit Community Moderation',
        type='2',
        url='',
        open_type='',
        parent_id=review_parent.id,
        icon='',
        sort=31,
        enable=1
    )
    db.session.commit()


def _seed_sensitive_words():
    crisis_words = ['suicide', 'kill myself', 'end my life', 'want to die', 'no reason to live',
                    '自杀', '不想活', '结束生命', '活不下去', '轻生']
    warning_words = ['damn', 'stupid', 'idiot', 'scam', 'fraud', '骗子', '诈骗', '傻逼']
    for w in crisis_words:
        if not SensitiveWord.query.filter_by(word=w).first():
            db.session.add(SensitiveWord(word=w, severity=2))
    for w in warning_words:
        if not SensitiveWord.query.filter_by(word=w).first():
            db.session.add(SensitiveWord(word=w, severity=1))
    db.session.commit()


def _seed_users():
    """Create test users with different roles."""
    family_role = Role.query.filter_by(code='certified_family').first()
    volunteer_role = Role.query.filter_by(code='certified_volunteer').first()
    regular_role = Role.query.filter_by(code='regular').first()

    users_data = [
        {'username': 'limei', 'realname': 'Li Mei', 'email': 'limei@test.com',
         'phone': '13800001111', 'bio': 'Caring for my husband with ALS for 3 years. Every day is a battle, but love keeps us going.',
         'user_type': 'certified_family', 'is_certified': True, 'role': family_role},
        {'username': 'zhangwei', 'realname': 'Zhang Wei', 'email': 'zhangwei@test.com',
         'phone': '13800002222', 'bio': 'Software engineer. My colleague shared this platform and I want to help.',
         'user_type': 'regular', 'is_certified': False, 'role': regular_role},
        {'username': 'wangfang', 'realname': 'Wang Fang', 'email': 'wangfang@test.com',
         'phone': '13800003333', 'bio': 'Retired nurse volunteering to support families in need. 20 years of medical experience.',
         'user_type': 'certified_volunteer', 'is_certified': True, 'role': volunteer_role},
        {'username': 'chenyun', 'realname': 'Chen Yun', 'email': 'chenyun@test.com',
         'phone': '13800004444', 'bio': 'My mother has Alzheimer\'s. Some days she remembers me, some days she doesn\'t. Both kinds of days are precious.',
         'user_type': 'certified_family', 'is_certified': True, 'role': family_role},
        {'username': 'liuyang', 'realname': 'Liu Yang', 'email': 'liuyang@test.com',
         'phone': '13800005555', 'bio': 'College student interested in social welfare. Here to learn and support.',
         'user_type': 'regular', 'is_certified': False, 'role': regular_role},
        {'username': 'sunli', 'realname': 'Sun Li', 'email': 'sunli@test.com',
         'phone': '13800006666', 'bio': 'Father of a child with leukemia. We fight together every single day.',
         'user_type': 'certified_family', 'is_certified': True, 'role': family_role},
        {'username': 'zhaojing', 'realname': 'Zhao Jing', 'email': 'zhaojing@test.com',
         'phone': '13800007777', 'bio': 'Social worker at Dublin City Hospital. Connecting families with resources.',
         'user_type': 'certified_volunteer', 'is_certified': True, 'role': volunteer_role},
        {'username': 'huanghai', 'realname': 'Huang Hai', 'email': 'huanghai@test.com',
         'phone': '13800008888', 'bio': 'Just browsing, hoping to understand what caregivers go through.',
         'user_type': 'regular', 'is_certified': False, 'role': regular_role},
    ]

    for ud in users_data:
        if User.query.filter_by(username=ud['username']).first():
            continue
        role = ud.pop('role')
        user = User(enable=1, **ud)
        user.set_password('test123')
        if role:
            user.role.append(role)
        db.session.add(user)
    db.session.commit()
    click.echo(f'  Created {len(users_data)} test users')


def _seed_certifications():
    """Create certification records for certified users."""
    certified_users = User.query.filter(User.is_certified == True, User.user_type != 'admin').all()
    for u in certified_users:
        if Certification.query.filter_by(user_id=u.id).first():
            continue
        cert_type = 'family' if 'family' in u.user_type else 'volunteer'
        cert = Certification(
            user_id=u.id, cert_type=cert_type, real_name=u.realname,
            id_card='320XXXXX' + str(random.randint(1000, 9999)),
            relation='Spouse' if cert_type == 'family' else 'Volunteer',
            patient_name='Patient of ' + u.realname if cert_type == 'family' else None,
            patient_illness=random.choice(['ALS', "Alzheimer's", 'Cancer', 'Rare Disease']) if cert_type == 'family' else None,
            hospital_name='Dublin City Hospital' if cert_type == 'family' else None,
            status='approved',
            reviewed_at=datetime.datetime.now() - datetime.timedelta(days=random.randint(10, 60))
        )
        db.session.add(cert)

    # Add one pending certification
    liuyang = User.query.filter_by(username='liuyang').first()
    if liuyang and not Certification.query.filter_by(user_id=liuyang.id).first():
        db.session.add(Certification(
            user_id=liuyang.id, cert_type='volunteer', real_name='Liu Yang',
            id_card='410XXXXX5678', relation='Volunteer',
            status='pending'
        ))
    db.session.commit()
    click.echo('  Created certifications')


def _seed_posts():
    """Create community posts across categories."""
    posts_data = [
        {'username': 'limei', 'title': 'Three years into ALS caregiving - what I wish I knew on day one',
         'content': 'When my husband was first diagnosed, I felt like the ground had been pulled from under me. Three years later, I want to share some things I wish someone had told me.\n\n1. It\'s okay to grieve even while they\'re still here. You\'re grieving the future you planned together.\n2. Accept help. I know it\'s hard. I spent the first year trying to do everything alone and nearly broke.\n3. Find your people. This community has been a lifeline for me.\n4. Take breaks without guilt. You can\'t pour from an empty cup.\n5. Document the good days. Take photos, write notes. You\'ll treasure them.\n\nTo anyone just starting this journey - you are stronger than you think. And you are not alone.',
         'category': 'emotional', 'likes': 47, 'comments_count': 12},
        {'username': 'chenyun', 'title': 'Mom recognized me today',
         'content': 'After three weeks of blank stares, my mother looked at me this morning and said my name. Just my name, nothing else. But it was everything.\n\nI sat in the car afterward and cried for twenty minutes. Happy tears, sad tears, I don\'t even know anymore. Alzheimer\'s is cruel, but moments like these remind me why I keep showing up every single day.\n\nHas anyone else experienced these lucid moments? How do you handle the emotional whiplash?',
         'category': 'emotional', 'likes': 89, 'comments_count': 23},
        {'username': 'wangfang', 'title': 'Free resources for caregivers in Dublin area',
         'content': 'Hi everyone! As a retired nurse and volunteer, I\'ve compiled a list of free resources available in the Dublin area:\n\n- Dublin Caregiver Support Group: meets every Tuesday at 7 PM at St. James\'s Hospital\n- Free respite care: contact the HSE Carer Support line at 1800-240014\n- Mental health counseling: free sessions through the Aware helpline\n- Equipment lending: the Irish Wheelchair Association has a lending program\n- Legal advice: FLAC provides free legal guidance on carer\'s rights\n\nI\'ll keep updating this list. Please share any resources you know of!',
         'category': 'resources', 'likes': 65, 'comments_count': 18},
        {'username': 'sunli', 'title': 'Small victory: my son rang the bell today 🔔',
         'content': 'After 8 months of chemotherapy, my 6-year-old son finally rang the bell at the hospital today. The nurses lined up and cheered. He was so proud of himself.\n\nWe still have a long road ahead - maintenance therapy, regular check-ups, the constant worry. But today, we celebrate.\n\nThank you to everyone who donated to our campaign. Thank you to the strangers who sent messages of hope. You helped us get here.\n\nTo the parents fighting similar battles: keep going. There are bells waiting to be rung.',
         'category': 'good_news', 'likes': 156, 'comments_count': 34},
        {'username': 'limei', 'title': 'Practical tips for ALS home care setup',
         'content': 'After lots of trial and error, here\'s our home setup that works:\n\n1. Hospital bed in the living room (not bedroom) - keeps them part of family life\n2. Voice-activated smart home devices - game changer when mobility decreases\n3. Communication board before they need it - practice while speech is still clear\n4. Bathroom grab bars and raised toilet seat - install these early\n5. A good quality suction machine - don\'t cheap out on this\n6. Backup power supply for medical equipment\n\nHappy to answer specific questions about any of these.',
         'category': 'medical', 'likes': 38, 'comments_count': 15},
        {'username': 'zhaojing', 'title': 'Understanding the medical card application process in Ireland',
         'content': 'Many families don\'t know they may be eligible for a medical card, which covers most healthcare costs. Here\'s a step-by-step guide:\n\n1. Check eligibility on hse.ie/medicalcard\n2. Gather income documentation\n3. Apply online through myWelfare.ie\n4. Processing takes 2-4 weeks\n5. If denied, you can appeal within 21 days\n\nCarers may also be eligible for the Carer\'s Allowance and the Carer\'s Support Grant. Don\'t leave money on the table - these supports exist for you.',
         'category': 'resources', 'likes': 42, 'comments_count': 8},
        {'username': 'chenyun', 'title': 'How do you handle the anger?',
         'content': 'I need to be honest. Today I got angry at my mother. She asked me the same question for the fifteenth time in an hour and I snapped. I immediately felt terrible.\n\nI know it\'s the disease. I know she can\'t help it. But I\'m human and I\'m exhausted and sometimes the patience just runs out.\n\nPlease tell me I\'m not the only one who feels this way. The guilt is eating me alive.',
         'category': 'emotional', 'likes': 73, 'comments_count': 28},
        {'username': 'huanghai', 'title': 'Donated for the first time today',
         'content': 'I\'m not a caregiver. I found this platform through a friend\'s shared link. I read through the stories here and was deeply moved.\n\nI just made my first donation to a family raising funds for their child\'s treatment. It wasn\'t much, but I hope it helps.\n\nTo all the caregivers here: you are doing incredible work. The world sees you, even when it feels like it doesn\'t.',
         'category': 'daily', 'likes': 95, 'comments_count': 19},
        {'username': 'wangfang', 'title': 'Volunteer training session this Saturday',
         'content': 'For those interested in volunteering as respite caregivers, we\'re holding a training session this Saturday from 10 AM to 2 PM at the community center.\n\nTopics covered:\n- Basic patient care and safety\n- Communication with patients who have cognitive impairment\n- Emergency procedures\n- Self-care for volunteers\n\nNo prior medical experience needed. Just bring your willingness to help. Lunch provided!\n\nPlease sign up by Thursday so we can prepare materials.',
         'category': 'resources', 'likes': 31, 'comments_count': 7},
        {'username': 'sunli', 'title': 'Hospital food hacks for long stays',
         'content': 'After spending what feels like half my life in hospital waiting rooms and wards, here are my survival tips:\n\n1. Bring a small electric kettle (ask permission first)\n2. Stock instant oatmeal and cup noodles in your bag\n3. Fresh fruit that doesn\'t need refrigeration: apples, bananas, oranges\n4. A good thermos for hot drinks\n5. Snack bars for when the cafeteria is closed\n6. Download movies/shows before you go - hospital WiFi is unreliable\n\nWhat are your hospital survival essentials?',
         'category': 'daily', 'likes': 44, 'comments_count': 22},
        {'username': 'limei', 'title': 'Finding moments of joy in the hardest days',
         'content': 'Yesterday, despite everything, we had a perfect evening. I played our wedding song and my husband smiled. Not the forced smile he gives when he\'s trying to be strong - a real, genuine smile.\n\nI\'ve learned to chase these moments. To notice them. To hold onto them when the 3 AM anxiety hits.\n\nWhat small moments of joy have you found lately? Let\'s share the light.',
         'category': 'emotional', 'likes': 112, 'comments_count': 31},
        {'username': 'zhangwei', 'title': 'Tech tools that help caregivers',
         'content': 'As a software engineer, I\'ve been researching apps and tools that can help caregivers:\n\n1. CareZone - medication management and tracking\n2. Medisafe - pill reminders\n3. Life360 - location sharing for patients who wander\n4. Lotsa Helping Hands - coordinate help from family/friends\n5. Calm/Headspace - guided meditation for stress relief\n\nAre there any other tools you\'d recommend? I\'m thinking of building a simple caregiving dashboard as a side project.',
         'category': 'resources', 'likes': 56, 'comments_count': 14},
    ]

    for pd in posts_data:
        user = User.query.filter_by(username=pd['username']).first()
        if not user:
            continue
        if Post.query.filter_by(title=pd['title']).first():
            continue
        days_ago = random.randint(1, 60)
        post = Post(
            user_id=user.id, title=pd['title'], content=pd['content'],
            category=pd['category'], like_count=pd['likes'],
            comment_count=pd['comments_count'], status=1, view_count=pd['likes'] * 3,
            create_at=datetime.datetime.now() - datetime.timedelta(days=days_ago, hours=random.randint(0, 23))
        )
        db.session.add(post)
    db.session.commit()
    click.echo(f'  Created {len(posts_data)} community posts')


def _seed_comments():
    """Add comments to posts."""
    comment_texts = [
        "Thank you for sharing this. It means more than you know.",
        "I went through something very similar. You're not alone in this.",
        "This is incredibly helpful. Saving this for later.",
        "Sending you strength and light. 💛",
        "My experience has been similar. The guilt is real but please be kind to yourself.",
        "I needed to read this today. Thank you.",
        "Does anyone know if this applies to families in Cork as well?",
        "You're an amazing person for sharing these resources. Thank you!",
        "This made me cry. In a good way. We're all in this together.",
        "I've been lurking here for weeks but this post made me want to comment. Thank you.",
        "My mother-in-law is going through the same thing. I'll share this with her.",
        "Three years is a long time. You're stronger than you know.",
        "The lucid moments are the hardest and the most beautiful. I understand completely.",
        "Has anyone tried the support group mentioned? Is it online too?",
        "Welcome to the community! Every donation matters, no matter the size.",
        "This is exactly the practical advice I needed. Installing grab bars this weekend.",
        "I rang that bell too, 2 years ago. Best day of my life. Congratulations! 🔔",
        "You are NOT a bad person for getting frustrated. You are human. Period.",
        "Can you share more details about the equipment lending program?",
        "I wish I had found this community sooner. Better late than never.",
    ]

    users = User.query.filter(User.username != 'admin').all()
    posts = Post.query.all()
    if not posts or not users:
        return

    count = 0
    for post in posts:
        n_comments = random.randint(2, 6)
        for i in range(n_comments):
            user = random.choice(users)
            if user.id == post.user_id and random.random() > 0.3:
                continue
            comment = Comment(
                post_id=post.id, user_id=user.id,
                content=random.choice(comment_texts),
                create_at=post.create_at + datetime.timedelta(hours=random.randint(1, 72))
            )
            db.session.add(comment)
            count += 1
    db.session.commit()
    click.echo(f'  Created {count} comments')


def _seed_confessions():
    """Create anonymous night confessions."""
    confessions_data = [
        "I haven't slept more than 4 hours straight in 8 months. I'm running on fumes and coffee.",
        "Sometimes I wish I could just disappear for one day. Just one day where nobody needs me.",
        "I miss who I was before all of this. I don't even remember what my hobbies used to be.",
        "My friends stopped calling months ago. I guess watching someone struggle isn't fun.",
        "I caught myself googling 'how long can a person go without sleep' at 3 AM. That's when I knew I needed help.",
        "The doctor said 'there's nothing more we can do' today. I nodded calmly. Then I cried in the parking lot for an hour.",
        "I feel guilty for being healthy while they suffer. Survivor's guilt for something that hasn't even ended yet.",
        "Some nights I just sit in the dark kitchen and breathe. It's the only time the house is quiet.",
        "I told everyone I'm fine. I'm not fine. I haven't been fine in a very long time.",
        "My child asked why grandma doesn't remember her name anymore. I didn't know what to say.",
        "Today a stranger held the door open for me and said 'you look like you could use a smile.' I almost broke down right there.",
        "I've started talking to the moon on late night walks. It's the only one who listens without advice.",
        "The hardest part isn't the care. It's watching them lose pieces of who they were, one by one.",
        "I found an old photo of us from before the diagnosis. We looked so carefree. I didn't know how lucky we were.",
        "Thank you to whoever created this space. Knowing others are awake at this hour, carrying similar weight... it helps.",
    ]

    animals = ['Firefly', 'Starling', 'Moonbird', 'Dewdrop', 'Glowworm', 'Nightingale', 'Snowflake', 'Raindrop']
    for text in confessions_data:
        if Confession.query.filter_by(content=text).first():
            continue
        nickname = f"Anonymous {random.choice(animals)} #{random.randint(1000, 9999)}"
        c = Confession(
            content=text, nickname=nickname,
            session_id=f"seed_{random.randint(10000, 99999)}",
            hug_count=random.randint(3, 45),
            create_at=datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 48))
        )
        db.session.add(c)
    db.session.commit()
    click.echo(f'  Created {len(confessions_data)} confessions')


def _seed_campaigns():
    """Create crowdfunding campaigns in various states."""
    demo_qr_url = '/static/index/images/ic_alipay_qrcode.png'
    campaigns_data = [
        {'username': 'limei', 'title': 'Help cover ALS treatment costs for my husband',
         'description': 'My husband was diagnosed with ALS two years ago. The disease has progressed and he now needs a specialized ventilator and a power wheelchair. Our insurance only covers a fraction of the costs.\n\nWe have two children, ages 8 and 12. I had to quit my teaching job to become a full-time caregiver. The financial pressure is crushing.\n\nThe ventilator alone costs €8,000, and the wheelchair is €12,000. We\'ve already spent our savings on medications and home modifications.\n\nAny amount helps. Even a few euros gives us hope. Thank you for reading our story.',
         'category': 'chronic', 'goal': 25000, 'raised': 18750, 'status': 'approved'},
        {'username': 'sunli', 'title': 'Fighting leukemia: help my son Xiaoming',
         'description': 'My 6-year-old son Xiaoming was diagnosed with acute lymphoblastic leukemia last year. He has completed the initial rounds of chemotherapy and rang the bell! But we still need maintenance therapy for the next 2 years.\n\nThe treatment costs are mounting. Each cycle of maintenance chemo costs about €3,000. We need approximately 8 more cycles.\n\nXiaoming is the bravest boy I know. He tells the nurses jokes to make them laugh. He deserves every chance at a normal life.\n\nPlease help us give him that chance.',
         'category': 'pediatric', 'goal': 30000, 'raised': 27500, 'status': 'approved'},
        {'username': 'chenyun', 'title': 'Specialized care for my mother with Alzheimer\'s',
         'description': 'My mother was diagnosed with early-onset Alzheimer\'s at age 58. She\'s now 63 and the disease has progressed to the moderate stage.\n\nWe need funds for:\n- Specialized memory care day program: €500/month\n- Safety modifications at home: €3,000\n- Respite care so I can continue working part-time: €400/month\n\nI\'m her only child and her primary caregiver. Without respite care, I\'ll have to quit my job entirely, which would make our financial situation even worse.\n\nEvery donation extends the time I can keep her at home, where she\'s happiest.',
         'category': 'chronic', 'goal': 15000, 'raised': 6800, 'status': 'approved'},
        {'username': 'limei', 'title': 'Emergency: Wheelchair-accessible van needed',
         'description': 'Our current vehicle can no longer safely transport my husband to his medical appointments. We need a wheelchair-accessible van urgently.\n\nHe has bi-weekly hospital visits, monthly specialist appointments, and occasional emergency trips. Ambulance transport is not always available and costs €200 per trip.\n\nA used wheelchair-accessible van costs approximately €20,000. We\'ve saved €5,000 but need help with the rest.',
         'category': 'other', 'goal': 20000, 'raised': 8200, 'status': 'approved'},
        {'username': 'sunli', 'title': 'Post-treatment rehabilitation for Xiaoming',
         'description': 'Now that Xiaoming has finished intensive chemo, he needs rehabilitation to rebuild his strength. The treatment took a toll on his growing body.\n\nWe need:\n- Physical therapy: €150/session, 2x/week for 6 months\n- Occupational therapy: €120/session, 1x/week\n- Nutritionist consultation and supplements\n- School tutoring to catch up on the year he missed\n\nHe\'s so eager to go back to school and play with his friends again.',
         'category': 'pediatric', 'goal': 12000, 'raised': 12000, 'status': 'approved'},  # Fully funded!
        {'username': 'chenyun', 'title': 'Art therapy program for dementia patients',
         'description': 'Research shows art therapy can slow cognitive decline in Alzheimer\'s patients. I want to start a weekly art therapy group at our local community center.\n\nFunds needed for:\n- Professional art therapist: €2,000 for 12 sessions\n- Art supplies: €500\n- Venue rental: €300\n\nThis program would serve 10-15 patients and give their caregivers a 2-hour break each week.',
         'category': 'mental_health', 'goal': 3000, 'raised': 1200, 'status': 'approved'},
        # Pending campaigns
        {'username': 'sunli', 'title': 'Genetic testing for my son\'s treatment plan',
         'description': 'The oncologist recommended genetic testing to better target Xiaoming\'s treatment. This specialized test costs €5,000 and is not covered by insurance.',
         'category': 'pediatric', 'goal': 5000, 'raised': 0, 'status': 'pending'},
    ]

    for cd in campaigns_data:
        user = User.query.filter_by(username=cd['username']).first()
        if not user:
            continue
        existing = Campaign.query.filter_by(title=cd['title']).first()
        if existing:
            if not existing.qr_code_url:
                existing.qr_code_url = demo_qr_url
            continue
        campaign = Campaign(
            user_id=user.id, title=cd['title'], description=cd['description'],
            category=cd['category'], funding_goal=cd['goal'],
            current_amount=cd['raised'], status=cd['status'],
            qr_code_url=demo_qr_url,
            is_fully_funded=(cd['raised'] >= cd['goal']),
            create_at=datetime.datetime.now() - datetime.timedelta(days=random.randint(5, 45))
        )
        db.session.add(campaign)
    db.session.commit()
    click.echo(f'  Created {len(campaigns_data)} campaigns')


def _seed_donations():
    """Create donation records for approved campaigns."""
    users = User.query.filter(User.username != 'admin').all()
    campaigns = Campaign.query.filter(Campaign.status == 'approved', Campaign.current_amount > 0).all()

    count = 0
    for campaign in campaigns:
        n_donations = random.randint(5, 20)
        messages = [
            "Stay strong! You've got this.", "Sending love and light to your family.",
            "Every bit helps. Wishing you the best.", "Praying for your recovery.",
            "From one caregiver to another - hang in there.", "",
            "I believe in your strength.", "My heart goes out to your family.",
            "Hope this helps, even a little.", "You are not alone in this fight.",
        ]
        for _ in range(n_donations):
            donor = random.choice(users)
            amount = random.choice([5, 10, 20, 50, 100, 200, 50, 20, 10, 10, 5])
            donation = Donation(
                campaign_id=campaign.id, user_id=donor.id,
                amount=amount, message=random.choice(messages),
                is_anonymous=random.random() > 0.7,
                create_at=campaign.create_at + datetime.timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            )
            db.session.add(donation)
            count += 1
    db.session.commit()
    click.echo(f'  Created {count} donations')


def _seed_journal_entries():
    """Create journal entries for certified users."""
    certified_users = User.query.filter(User.is_certified == True, User.user_type != 'admin').all()

    moods = ['😟', '😕', '😐', '🙂', '😊']
    entries_templates = [
        {'title': 'A difficult morning', 'mood': '😟',
         'content': 'Woke up at 4 AM to the sound of the monitor. Spent an hour stabilizing things. Exhausted but couldn\'t go back to sleep. Made tea and watched the sunrise. There\'s something about dawn that makes everything feel temporarily manageable.'},
        {'title': 'Small progress', 'mood': '🙂',
         'content': 'Today was better than yesterday. We managed to go outside for 15 minutes. The fresh air did us both good. Sometimes progress is measured in minutes, not milestones.'},
        {'title': '', 'mood': '😐',
         'content': 'Another Tuesday. Medication schedule, meals, exercises, repeat. The routine is both a prison and a lifeline. At least we know what to expect.'},
        {'title': 'Grateful today', 'mood': '😊',
         'content': 'A neighbor brought over homemade soup. Such a simple gesture but it made me tear up. It\'s been so long since someone took care of ME. Note to self: accept kindness gracefully.'},
        {'title': 'Missing normal', 'mood': '😕',
         'content': 'Saw photos from a friend\'s vacation on social media. Felt a pang of jealousy, then guilt for feeling jealous. Our "normal" is so different now. I need to stop comparing.'},
        {'title': 'A good visit from the nurse', 'mood': '🙂',
         'content': 'The home care nurse came today and said the new medication seems to be helping. First positive medical news in months. I\'ll take it.'},
        {'title': 'Cried in the shower', 'mood': '😟',
         'content': 'The shower is my safe space. Five minutes where no one can see or hear me fall apart. Today I needed those five minutes more than usual.'},
        {'title': 'He laughed today', 'mood': '😊',
         'content': 'Put on his favorite old comedy show and he actually laughed. A real laugh, from deep inside. I recorded the sound on my phone. I never want to forget it.'},
        {'title': 'Research and hope', 'mood': '😐',
         'content': 'Spent the evening reading about new treatment trials. Some promising developments but nothing available yet. Knowledge is power, even when the power is just hope.'},
        {'title': 'One year anniversary', 'mood': '🙂',
         'content': 'One year since the diagnosis. I thought I\'d feel sadder today but actually I feel something like pride. We made it through a whole year. We\'re still here. Still fighting. Still together.'},
        {'title': 'Birthday', 'mood': '😊',
         'content': 'It\'s my birthday. The kids made a card and he managed to write his name in it. Wobbly letters but unmistakably his handwriting. Best present I\'ve ever received.'},
        {'title': 'Sleepless night', 'mood': '😟',
         'content': 'Mind won\'t stop racing. What if the treatment stops working? What if I get sick too? Who takes care of the caregiver? Writing this at 2 AM because the words need to go somewhere.'},
    ]

    count = 0
    for user in certified_users:
        n_entries = random.randint(8, 15)
        for i in range(n_entries):
            template = entries_templates[i % len(entries_templates)]
            days_ago = random.randint(1, 180)
            entry = JournalEntry(
                user_id=user.id,
                title=template['title'],
                content=template['content'],
                mood=template['mood'],
                entry_date=datetime.date.today() - datetime.timedelta(days=days_ago),
                create_at=datetime.datetime.now() - datetime.timedelta(days=days_ago)
            )
            db.session.add(entry)
            count += 1
    db.session.commit()
    click.echo(f'  Created {count} journal entries')


def _seed_respite_requests():
    """Create respite station requests with Dublin area coordinates."""
    requests_data = [
        {'username': 'limei', 'type': 'service', 'title': 'Need someone to watch my husband for 3 hours on Saturday',
         'description': 'I have a doctor\'s appointment myself and need someone experienced with ALS patients to stay with my husband. He needs help with feeding and position changes.',
         'category': 'medical_watch', 'city': 'Dublin', 'district': 'Dublin 4',
         'lat': 53.3244, 'lng': -6.2288, 'status': 'pending'},
        {'username': 'chenyun', 'type': 'service', 'title': 'Weekly companionship visit for my mother',
         'description': 'Looking for a volunteer to visit my mother once a week for 2 hours. She enjoys conversation, puzzles, and gentle music. Alzheimer\'s patient - patience needed.',
         'category': 'companionship', 'city': 'Dublin', 'district': 'Dublin 6',
         'lat': 53.3150, 'lng': -6.2620, 'status': 'pending'},
        {'username': 'wangfang', 'type': 'equipment', 'title': 'Wheelchair available for lending - 3 months',
         'description': 'I have a manual wheelchair in excellent condition. Available for up to 3 months. Self-propelled, with cushion. Pickup from Dublin 2.',
         'category': 'wheelchair', 'city': 'Dublin', 'district': 'Dublin 2',
         'lat': 53.3382, 'lng': -6.2591, 'status': 'pending'},
        {'username': 'sunli', 'type': 'service', 'title': 'Help needed: school pickup for my daughter',
         'description': 'I need to be at the hospital with my son every afternoon this week. Looking for someone to pick up my daughter from school (Dublin 8) at 2:30 PM.',
         'category': 'errands', 'city': 'Dublin', 'district': 'Dublin 8',
         'lat': 53.3358, 'lng': -6.2853, 'status': 'pending'},
        {'username': 'zhaojing', 'type': 'equipment', 'title': 'Hospital bed available - used 6 months',
         'description': 'Electric hospital bed with mattress, used for 6 months, in good condition. Free to a family in need. You arrange pickup/transport. Located in Dun Laoghaire.',
         'category': 'other', 'city': 'Dublin', 'district': 'Dun Laoghaire',
         'lat': 53.2945, 'lng': -6.1340, 'status': 'pending'},
        {'username': 'limei', 'type': 'service', 'title': 'Overnight care needed - one night',
         'description': 'I have a family emergency and need overnight care for my husband this Friday. He requires repositioning every 2 hours and suction as needed.',
         'category': 'medical_watch', 'city': 'Dublin', 'district': 'Dublin 4',
         'lat': 53.3280, 'lng': -6.2350, 'status': 'in_progress'},
        {'username': 'chenyun', 'type': 'equipment', 'title': 'Looking for a shower chair',
         'description': 'Need a shower chair or bath seat for my mother. Willing to buy or borrow. She weighs about 55kg.',
         'category': 'other', 'city': 'Dublin', 'district': 'Dublin 6',
         'lat': 53.3100, 'lng': -6.2500, 'status': 'pending'},
        {'username': 'wangfang', 'type': 'service', 'title': 'Offering free blood pressure monitoring visits',
         'description': 'As a retired nurse, I\'m offering free home visits for blood pressure monitoring and basic health checks. Available Mondays and Wednesdays in the Dublin 4/6 area.',
         'category': 'medical_watch', 'city': 'Dublin', 'district': 'Dublin 4',
         'lat': 53.3200, 'lng': -6.2400, 'status': 'pending'},
    ]

    for rd in requests_data:
        user = User.query.filter_by(username=rd['username']).first()
        if not user:
            continue
        if RespiteRequest.query.filter_by(title=rd['title']).first():
            continue

        acceptor_id = None
        accepted_at = None
        if rd['status'] == 'in_progress':
            acceptor = User.query.filter_by(username='wangfang').first()
            acceptor_id = acceptor.id if acceptor else None
            accepted_at = datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24))

        req = RespiteRequest(
            user_id=user.id, request_type=rd['type'], title=rd['title'],
            description=rd['description'], category=rd['category'],
            city=rd['city'], district=rd['district'],
            latitude=rd['lat'], longitude=rd['lng'],
            pin_color='orange' if rd['type'] == 'service' else 'green',
            status=rd['status'], acceptor_id=acceptor_id, accepted_at=accepted_at,
            create_at=datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 14))
        )
        db.session.add(req)
    db.session.commit()
    click.echo(f'  Created {len(requests_data)} respite requests')
