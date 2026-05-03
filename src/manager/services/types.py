from enum import Enum


class ImageType(Enum):
    BASE = "base"
    MEDIA = "media"


class RestartPolicyType(Enum):
    NO = "no"
    ALWAYS = "always"
    ON_FAILURE = "on-failure"
    UNLESS_STOPPED = "unless-stopped"
