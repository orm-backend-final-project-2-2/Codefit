from django.shortcuts import render
from accounts.views import LoginView


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)  # 사용자 인증
        if user is not None:
            login(request, user)  # 로그인 처리 (세션 생성)
            return Response({"message": "로그인 성공"})
        else:
            return Response({"message": "로그인 실패"}, status=401)
