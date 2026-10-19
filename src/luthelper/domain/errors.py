class AppError(Exception):
    """所有业务错误的基类。"""


class NetworkError(AppError):
    pass


class AuthError(AppError):
    pass


class CaptchaError(AuthError):
    pass


class SessionExpiredError(AuthError):
    pass


class CourseUnavailableError(AppError):
    pass
