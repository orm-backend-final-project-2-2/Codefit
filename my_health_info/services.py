from account.models import CustomUser as User
from my_health_info.models import Routine, UsersRoutine


class UsersRoutineManagementService:
    """
    Routine 모델의 변경으로 인한 UsersRoutine 모델의 변경을 담당하는 서비스 클래스
    """

    def __init__(self, user: User, routine: Routine):
        self.user = user
        self.routine = routine

    def subscribe_routine(self):
        """
        등록된 유저가 등록된 루틴을 구독하는 메서드

        만약 이미 구독 중인 루틴이라면, 이미 구독 중이라는 에러를 발생시킨다.
        만약 작성자 본인의 루틴을 구독하려고 한다면, 작성자 본인의 루틴을 구독할 수 없다는 에러를 발생시킨다.
        """
        ...
