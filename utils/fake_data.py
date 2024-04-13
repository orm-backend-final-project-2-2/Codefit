from faker import Faker
from account.models import CustomUser
from my_health_info.models import HealthInfo
from exercises_info.models import ExercisesInfo, FocusArea
from community.models import Post
from utils.enums import FocusAreaEnum
import abc
import random


class FakeModel(abc.ABC):
    """
    가짜 모델 생성 클래스
    공통된 동작을 정의했습니다.
    """

    def __init__(self, model):
        """생성시 모델을 받아서 인스턴스 변수로 저장합니다."""
        self.fake = Faker()
        self.model = model
        self.attributes = self.model._meta.get_fields()
        self.base_attr = None
        self.related_fake_models = None
        self.related_attr = None
        self.derived_attr = None

    def needed_info(self, info_list):
        """필요한 정보로 이루어진 리스트를 넣으면 필요한 정보와 값을 반환합니다."""
        return {key: self.base_attr.get(key) for key in info_list}

    @abc.abstractmethod
    def set_base_attr(self):
        """모델의 기본 속성을 설정합니다."""
        pass

    def set_related_fake_models(self):
        """모델의 관련 가짜 모델을 설정합니다."""
        pass

    def set_related_attr(self):
        """모델의 관련 속성을 설정합니다."""
        pass

    def set_derived_attr(self):
        """모델의 파생 속성을 설정합니다."""
        pass

    @abc.abstractmethod
    def create_instance(self):
        """모델을 생성하고 인스턴스를 반환합니다."""
        pass


class FakeUser(FakeModel):
    def __init__(self):
        super().__init__(CustomUser)
        self.base_attr = self.set_base_attr()

    def set_base_attr(self):
        return {
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "password": self.fake.password(),
        }

    def create_instance(self, is_staff=False):
        """스태프 여부에 따라 유저를 생성합니다."""
        if is_staff:
            self.instance = self.model.objects.create_superuser(**self.base_attr)
        else:
            self.instance = self.model.objects.create_user(**self.base_attr)
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["username", "email", "password"])

    def request_login(self):
        """Login 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["email", "password"])


class FakeHealthInfo(FakeModel):
    def __init__(self):
        super().__init__(HealthInfo)
        self.base_attr = self.set_base_attr()

    def set_base_attr(self):
        return {
            "height": self.fake.random_int(150, 200),
            "weight": self.fake.random_int(50, 100),
            "age": self.fake.random_int(10, 100),
        }

    def create_instance(self, user_instance):
        self.instance = self.model.objects.create(user=user_instance, **self.base_attr)
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        base_info = self.needed_info(["height", "weight", "age"])
        return base_info


class FakeFocusArea(FakeModel):
    def __init__(self, focus_area):
        super().__init__(FocusArea)
        self.base_attr = self.set_base_attr(focus_area)
        self.count = random.randint(1, 4)

    def set_base_attr(self, focus_area):
        return {
            "focus_area": focus_area,
        }

    def create_instance(self):
        self.instance = self.model.objects.create(**self.base_attr)
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["focus_area"])


class FakeExercisesInfo(FakeModel):
    def __init__(self):
        super().__init__(ExercisesInfo)
        self.base_attr = self.set_base_attr()
        self.related_fake_models = self.set_related_fake_models()
        self.related_attr = self.set_related_attr()

    def set_base_attr(self):
        return {
            "title": self.fake.sentence(),
            "description": self.fake.text(),
            "video": self.fake.url(),
        }

    def set_related_fake_models(self):
        focus_areas = self.set_focus_areas()
        return {"focus_areas": focus_areas}

    def set_focus_areas(self):
        sample_count = random.randint(1, 4)
        sample_focus_areas = random.sample(FocusAreaEnum.choices(), sample_count)

        focus_areas = []
        for name, area in sample_focus_areas:
            fake_focus_area = FakeFocusArea(area)
            focus_areas.append(fake_focus_area)

        return focus_areas

    def set_related_attr(self):
        related_attr = {}

        if self.related_fake_models:
            related_attr["focus_areas"] = [
                focus_area.base_attr
                for focus_area in self.related_fake_models.get("focus_areas")
            ]

        return related_attr

    def create_instance(self, user_instance):
        self.instance = self.model.objects.create(
            author=user_instance, **self.base_attr
        )

        for verbose_name, fake_models in self.related_fake_models.items():
            for fake_model in fake_models:
                fake_model_instance = fake_model.create_instance()

        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        base_attr = self.base_attr
        related_attr = self.related_attr
        return {**base_attr, **related_attr}


class FakePost(FakeModel):
    def __init__(self):
        super().__init__(Post)
        self.base_attr = self.set_base_attr()

    def set_base_attr(self):
        return {
            "title": self.fake.sentence(),
            "content": self.fake.text(),
        }

    def create_instance(self, user_instance):
        self.instance = self.model.objects.create(
            author=user_instance, **self.base_attr
        )
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["title", "content"])
