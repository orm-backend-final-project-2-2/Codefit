from account.models import CustomUser as User
from my_health_info.models import Routine, UsersRoutine
from rest_framework.exceptions import PermissionDenied


class UsersRoutineManagementService:
    def __init__(self, user: User, routine: Routine):
        self.user = user
        self.routine = routine
