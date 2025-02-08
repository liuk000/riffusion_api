class RiffusionApiError(Exception):
    """Base exception for riffusion API"""


class NoAccounts(RiffusionApiError):
    """No accounts"""


class RiffusionGenerationError(RiffusionApiError):
    """Error while generate"""

class RiffusionRefreshError(RiffusionApiError):
    """Error while refresh"""