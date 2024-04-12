from faker import Faker
from account.models import CustomUser
from my_health_info.models import HealthInfo
from exercises_info.models import ExercisesInfo
from community.models import Post
from . import enums
import abc


class FakeModel(abc.ABC):
    """
    가짜 모델 생성 클래스
    공통된 동작을 정의했습니다.
    """

    def __init__(self, model):
        """생성시 모델을 받아서 인스턴스 변수로 저장합니다."""
        self.fake = Faker()
        self.model = model
        self.fake_info = None
        self.instance = None

    def needed_info(self, info_list):
        """필요한 정보로 이루어진 리스트를 넣으면 필요한 정보와 값을 반환합니다."""
        if self.fake_info:
            return {key: self.fake_info.get(key) for key in info_list}

    @abc.abstractmethod
    def basic_info(self):
        """모델이 필요한 최소한의 정보를 반환합니다."""
        pass

    @abc.abstractmethod
    def create_instance(self):
        """모델을 생성하고 인스턴스를 반환합니다."""
        pass


class FakeUser(FakeModel):
    def __init__(self):
        super().__init__(CustomUser)
        self.fake_info = self.basic_info()

    def basic_info(self):
        return {
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "password": self.fake.password(),
        }

    def create_instance(self, is_staff=False):
        """스태프 여부에 따라 유저를 생성합니다."""
        if is_staff:
            self.instance = self.model.objects.create_superuser(**self.fake_info)
        else:
            self.instance = self.model.objects.create_user(**self.fake_info)
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
        self.fake_info = self.basic_info()

    def basic_info(self):
        return {
            "height": self.fake.random_int(150, 200),
            "weight": self.fake.random_int(50, 100),
            "age": self.fake.random_int(10, 100),
        }

    def create_instance(self, user_instance):
        self.instance = self.model.objects.create(user=user_instance, **self.fake_info)
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["height", "weight", "age"])


class FakeExercisesInfo(FakeModel):
    def __init__(self):
        super().__init__(ExercisesInfo)
        self.fake_info = self.basic_info()

    def basic_info(self):
        focus_areas = enums.FocusAreaEnum.choices()
        chosen_focus_areas = self.fake.random_choices(focus_areas)
        return {
            "title": self.fake.sentence(),
            "description": self.fake.text(),
            "video": self.fake.url(),
            "focus_areas": chosen_focus_areas,
        }

    def create_instance(self, user_instance):
        focus_areas = self.fake_info.pop("focus_areas")
        self.instance = self.model.objects.create(
            author=user_instance, **self.fake_info
        )
        self.instance.focus_areas.set(focus_areas)
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["title", "description"])


class FakePost(FakeModel):
    def __init__(self):
        super().__init__(Post)
        self.fake_info = self.basic_info()

    def basic_info(self):
        return {
            "title": self.fake.sentence(),
            "content": self.fake.text(),
        }

    def create_instance(self, user_instance):
        self.instance = self.model.objects.create(
            author=user_instance, **self.fake_info
        )
        return self.instance

    def request_create(self):
        """Create 요청에 필요한 정보를 반환합니다."""
        return self.needed_info(["title", "content"])
