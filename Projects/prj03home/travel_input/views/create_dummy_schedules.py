# travel_input/management/commands/create_dummy_schedules.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from travel_input.models import Schedule
from faker import Faker
from datetime import timedelta, date
import random

class Command(BaseCommand):
    help = '더미 일정 500개 생성'

    def handle(self, *args, **kwargs):
        fake = Faker('ko_KR')
        regions = ['서울', '부산', '제주', '강원도', '경기도']
        styles = ['city', 'relax', 'nature', 'culture', 'activity']
        factors = ['stay', 'food', 'weather', 'schedule', 'culture']

        user = User.objects.first()  # ✅ 테스트용 첫 사용자 (원하면 ID로 변경)

        def get_random_list_as_str(options, k=2):
            selected = random.sample(options, k)
            return str(selected)

        for _ in range(500):
            Schedule.objects.create(
                user=user,
                title=fake.catch_phrase(),
                destination=random.choice(regions),
                start_date=date.today() + timedelta(days=random.randint(1, 60)),
                end_date=date.today() + timedelta(days=random.randint(3, 70)),
                notes=fake.sentence(),
                travel_style=get_random_list_as_str(styles),
                important_factors=get_random_list_as_str(factors)
            )

        self.stdout.write(self.style.SUCCESS('✅ 500개 더미 일정 생성 완료!'))
