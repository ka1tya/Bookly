class AppError(Exception):
    pass

class ValidationError(AppError):
    pass

class NotFoundError(AppError):
    pass

class ConflictError(AppError):
    pass

class OrderStatusError(ConflictError):
    pass

class LockedError(ConflictError):
    pass
