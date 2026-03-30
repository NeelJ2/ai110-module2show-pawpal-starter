from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List, Optional


@dataclass
class TimeRange:
    start: time
    end: time

    def contains(self, t: time) -> bool:
        """Check if time is within range."""
        return self.start <= t < self.end

    def duration_minutes(self) -> int:
        """Calculate duration in minutes."""
        delta = datetime.combine(date.min, self.end) - datetime.combine(date.min, self.start)
        return int(delta.total_seconds() // 60)


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
    tasks: List['PetCareTask'] = field(default_factory=list)

    def add_medication(self, med: Medication) -> None:
        """Add a medication to the pet."""
        self.meds.append(med)

    def remove_medication(self, med_name: str) -> None:
        """Remove a medication by name."""
        self.meds = [m for m in self.meds if m.name != med_name]

    def add_task(self, task: 'PetCareTask') -> None:
        """Add a task to the pet."""
        if task.pet.name != self.name:
            raise ValueError('Task pet does not belong to this pet')
        self.tasks.append(task)

    def get_tasks(self, status_filter: Optional[List[str]] = None) -> List['PetCareTask']:
        """Get tasks, optionally filtered by status."""
        if status_filter is None:
            return list(self.tasks)
        return [t for t in self.tasks if t.status in status_filter]


@dataclass
class Owner:
    name: str
    availability: TimeRange
    contact_method: str
    preferred_feeding_times: List[TimeRange] = field(default_factory=list)
    urgency_level: int = 1
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Get a pet by name."""
        return next((p for p in self.pets if p.name == name), None)

    def is_available(self, at: datetime) -> bool:
        """Check if owner is available at time."""
        return self.availability.contains(at.time())

    def get_all_tasks(self, status_filter: Optional[List[str]] = None) -> List['PetCareTask']:
        """Get all tasks from all pets."""
        tasks: List['PetCareTask'] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks(status_filter=status_filter))
        return tasks


@dataclass
class PetCareTask:
    task_id: str
    pet: Pet
    task_name: str
    duration_minutes: int
    priority: int
    instructions: Optional[str] = None
    status: str = 'planned'
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None

    def schedule(self, start: datetime) -> None:
        """Schedule the task at start time."""
        self.scheduled_start = start
        self.scheduled_end = start + timedelta(minutes=self.duration_minutes)
        self.status = 'planned'

    def complete(self) -> None:
        """Mark task as completed."""
        self.status = 'completed'

    def cancel(self) -> None:
        """Mark task as canceled."""
        self.status = 'canceled'


@dataclass
class PetCareManager:
    owner: Owner
    tasks: List[PetCareTask] = field(default_factory=list)

    def add_task(self, task: PetCareTask) -> None:
        """Add a task to the manager."""
        if task.pet not in self.owner.pets:
            raise ValueError('Task pet does not belong to this owner')
        self.tasks.append(task)
        task.pet.add_task(task)

    def edit_task(self, task_id: str, new_task: PetCareTask) -> None:
        """Edit an existing task."""
        for i, t in enumerate(self.tasks):
            if t.task_id == task_id:
                self.tasks[i] = new_task
                return
        raise ValueError(f'Task {task_id} not found')

    def remove_task(self, task_id: str) -> None:
        """Remove a task by ID."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
        for pet in self.owner.pets:
            pet.tasks = [t for t in pet.tasks if t.task_id != task_id]

    def get_tasks_for_pet(self, pet_name: str) -> List[PetCareTask]:
        """Get tasks for a specific pet."""
        pet = self.owner.get_pet(pet_name)
        if not pet:
            return []
        return pet.get_tasks()

    def plan_day(self, for_date: date, available_minutes: int, start_time: time = time(8, 0)) -> List[PetCareTask]:
        """Plan tasks for the day."""
        candidate_tasks = [t for t in self.tasks if t.status == 'planned']
        candidate_tasks.sort(key=lambda t: (-t.priority, t.duration_minutes))

        scheduled: List[PetCareTask] = []
        current = datetime.combine(for_date, start_time)
        remaining = available_minutes

        for task in candidate_tasks:
            if task.duration_minutes <= remaining:
                task.schedule(current)
                scheduled.append(task)
                current += timedelta(minutes=task.duration_minutes)
                remaining -= task.duration_minutes

        return scheduled

    def explain_plan(self, scheduled: List[PetCareTask]) -> str:
        """Generate a string explanation of the plan."""
        lines = []
        for task in scheduled:
            start = task.scheduled_start.strftime('%H:%M') if task.scheduled_start else 'TBD'
            lines.append(f'{start} - {task.task_name} ({task.pet.name}, {task.duration_minutes}m, priority {task.priority})')
        return '\n'.join(lines)

