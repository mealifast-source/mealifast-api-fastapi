from typing import Optional, Dict, Any


class MealiFastException(Exception):
    """Base exception for MealiFast application"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class BadRequestException(MealiFastException):
    """400 Bad Request"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
            details=details,
        )


class UnauthorizedException(MealiFastException):
    """401 Unauthorized"""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(MealiFastException):
    """403 Forbidden"""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )


class NotFoundException(MealiFastException):
    """404 Not Found"""
    
    def __init__(self, resource: str, resource_id: str = ""):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
        )


class ConflictException(MealiFastException):
    """409 Conflict"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details,
        )


class ValidationException(MealiFastException):
    """422 Unprocessable Entity"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class InvalidCredentialsException(UnauthorizedException):
    """Invalid email or password"""
    
    def __init__(self):
        super().__init__("Invalid email or password")


class EmailAlreadyExistsException(ConflictException):
    """Email already registered"""
    
    def __init__(self, email: str):
        super().__init__(f"Email '{email}' is already registered")


class InvalidOTPException(BadRequestException):
    """Invalid or expired OTP"""
    
    def __init__(self):
        super().__init__("Invalid or expired OTP")


class InvalidTokenException(UnauthorizedException):
    """Invalid JWT token"""
    
    def __init__(self):
        super().__init__("Invalid or expired token")


class InvalidResetTokenException(BadRequestException):
    """Invalid or expired reset token"""
    
    def __init__(self):
        super().__init__("Invalid or expired reset token")


class AccountNotVerifiedException(UnauthorizedException):
    """Account email not verified"""
    
    def __init__(self):
        super().__init__("Please verify your email to login")


class AccountInactiveException(UnauthorizedException):
    """Account not active"""
    
    def __init__(self):
        super().__init__("Your account is inactive")


class GroupNotFoundException(NotFoundException):
    """Group not found"""
    
    def __init__(self, group_id: str = ""):
        super().__init__("Group", group_id)


class MemberNotFoundException(NotFoundException):
    """Member not found"""
    
    def __init__(self, member_id: str = ""):
        super().__init__("Member", member_id)


class MealNotFoundException(NotFoundException):
    """Meal not found"""
    
    def __init__(self, meal_id: str = ""):
        super().__init__("Meal", meal_id)


class MenuNotFoundException(NotFoundException):
    """Menu not found"""
    
    def __init__(self, menu_id: str = ""):
        super().__init__("Menu", menu_id)


class OrderWindowNotFoundException(NotFoundException):
    """Order window not found"""
    
    def __init__(self, window_id: str = ""):
        super().__init__("Order window", window_id)


class OrderNotFoundException(NotFoundException):
    """Order not found"""
    
    def __init__(self, order_id: str = ""):
        super().__init__("Order", order_id)


class InvoiceNotFoundException(NotFoundException):
    """Invoice not found"""
    
    def __init__(self, invoice_id: str = ""):
        super().__init__("Invoice", invoice_id)


class SubscriptionPlanNotFoundException(NotFoundException):
    """Subscription plan not found"""
    
    def __init__(self, plan_id: str = ""):
        super().__init__("Subscription plan", plan_id)


class OrderWindowClosedException(BadRequestException):
    """Order window is closed"""
    
    def __init__(self):
        super().__init__("Order window is closed. Cannot submit orders.")


class OrderNotInDraftException(BadRequestException):
    """Order is not in draft status"""
    
    def __init__(self):
        super().__init__("Only draft orders can be updated")


class PaymentFailedException(BadRequestException):
    """Payment processing failed"""
    
    def __init__(self, reason: str = ""):
        message = "Payment processing failed"
        if reason:
            message = f"{message}: {reason}"
        super().__init__(message)


class EmailSendFailedException(BadRequestException):
    """Email sending failed"""
    
    def __init__(self, recipient: str = ""):
        message = "Failed to send email"
        if recipient:
            message = f"{message} to {recipient}"
        super().__init__(message)


class InsufficientPermissionException(ForbiddenException):
    """User lacks required permissions"""
    
    def __init__(self, action: str = ""):
        message = "You do not have permission to perform this action"
        if action:
            message = f"You do not have permission to {action}"
        super().__init__(message)


class RateLimitExceededException(MealiFastException):
    """Rate limit exceeded"""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Too many requests. Please try again later",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after},
        )
