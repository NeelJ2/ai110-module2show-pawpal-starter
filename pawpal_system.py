from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import List, Optional


@dataclass
class TimeRange:
    start: time
    end: time

    def contains(self, t: time) -> bool:
        ...

    def duration_minutes(self) -> int:
        ...


@dataclass
class Medication:
    name: str
    dose: str
    frequency: str
    notes: Optional[str] = None


@dataclass
class Pet:
    name: str
    breed: str
    age_months: int
    species: str
    meds: List[Medication] = field(default_factory=list)

    def add_medication(self, med: Medication) -> None:
        ...

    def remove_medication(self, med_name: str) -> None:
        ...


@dataclass
class Owner:
    name: str
    availability: TimeRange
    contact_method: str
    preferred_feeding_times: List[TimeRange] = field(default_factory=list)
    urgency_level: int = 1
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        ...

    def get_pet(self, name: str) -> Optional[Pet]:
        ...

    def is_available(self, at: datetime) -> bool:
        ...


@dataclass
class PetCareTask:
    task_id: str
    pet_name: str
    task_name: str
    duration_minutes: int
    priority: int
    instructions: Optional[str] = None
    status: str = "planned"
    scheduled_start: Optional[datetime] = None

    def schedule(self, start: datetime) -> None:
        ...

    def complete(self) -> None:
        ...

    def cancel(self) -> None:
        ...


@dataclass
class PetCareManager:
    owner: Owner
    tasks: List[PetCareTask] = field(default_factory=list)

    def add_task(self, task: PetCareTask) -> None:
        ...

    def edit_task(self, task_id: str, new_task: PetCareTask) -> None:
        ...

    def remove_task(self, task_id: str) -> None:
        ...

    def get_tasks_for_pet(self, pet_name: str) -> List[PetCareTask]:
        ...

    def plan_day(self, for_date: date, available_minutes: int) -> List[PetCareTask]:
        ...

    def explain_plan(self) -> str:
        ...
