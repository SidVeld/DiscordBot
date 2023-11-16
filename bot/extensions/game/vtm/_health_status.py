class HealthStatus:
    def __init__(self, name: str, penalty: int) -> None:
        self.__name = name
        self.__penalty = penalty

    @property
    def name(self) -> str:
        return self.__name

    @property
    def penalty(self) -> int:
        return self.__penalty

    def __str__(self) -> str:
        return f"{self.__name} (penalty: {self.__penalty})"
