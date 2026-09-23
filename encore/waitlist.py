
from abc import ABC, abstractmethod


class WaitlistObserver(ABC):
    """
    Observer interface: notified when a sold-out show has seats again.
    """

    @abstractmethod
    def notify(self, show_title: str, available_seats: int) -> None:
        raise NotImplementedError


class EmailWaitlistNotifier(WaitlistObserver):
    def __init__(self, email: str):
        self.email = email
        self.sent = []

    def notify(self, show_title: str, available_seats: int) -> None:
        self.sent.append(
            f"[Email to {self.email}] '{show_title}' has {available_seats} seat(s) available again"
        )


class SMSWaitlistNotifier(WaitlistObserver):
    def __init__(self, phone: str):
        self.phone = phone
        self.sent = []

    def notify(self, show_title: str, available_seats: int) -> None:
        self.sent.append(
            f"[SMS to {self.phone}] '{show_title}' has {available_seats} seat(s) available again"
        )


class Show:
    """
    Subject: a live show with a seat count and a list of waitlisted fans.
    """

    def __init__(self, title: str, available_seats: int = 0):
        self.title = title
        self.available_seats = available_seats
        self._observers = []

    def join_waitlist(self, observer: WaitlistObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def leave_waitlist(self, observer: WaitlistObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def sell_seats(self, count: int) -> None:
        if count <= 0:
            raise ValueError("count must be positive")
        if count > self.available_seats:
            raise ValueError("not enough seats available")
        self.available_seats -= count

    def release_seats(self, count: int) -> None:
        if count <= 0:
            raise ValueError("count must be positive")
        was_sold_out = self.available_seats == 0
        self.available_seats += count
        if was_sold_out:
            for observer in self._observers:
                observer.notify(self.title, self.available_seats)
