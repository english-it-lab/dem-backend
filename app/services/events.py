from collections.abc import Sequence

from app.models import Event
from app.repositories.committee_member import CommitteeMemberRepository
from app.repositories.events import EventRepository
from app.repositories.participant import ParticipantRepository
from app.repositories.section import SectionRepository
from app.repositories.section_jury import SectionJuryRepository
from app.schemas import EventCreate


def _build_name(person):
    """Helper: build full name from person object."""
    if person is None:
        return ""
    parts = [person.last_name, person.first_name, person.middle_name]
    return " ".join(p for p in parts if p)


class EventProgramService:
    def __init__(
        self,
        event_repo: EventRepository,
        section_repo: SectionRepository,
        participant_repo: ParticipantRepository,
        committee_repo: CommitteeMemberRepository,
        section_jury_repo: SectionJuryRepository,
    ) -> None:
        self._event_repo = event_repo
        self._section_repo = section_repo
        self._participant_repo = participant_repo
        self._committee_repo = committee_repo
        self._section_jury_repo = section_jury_repo

    async def list_events(self) -> Sequence[Event]:
        return await self._event_repo.list_events()

    async def create_event(self, payload: EventCreate) -> Event:
        return await self._event_repo.create_event(payload)

    async def get_event_program_data(self, event_id: int) -> dict:
        event = await self._event_repo.get_event_with_organizer(event_id)
        if not event:
            raise ValueError(f"Мероприятие {event_id} не найдено")

        sections = await self._section_repo.get_sections_by_event(event_id)

        committee = await self._committee_repo.list_by_event(event_id)
        committee_data = []
        for member in committee:
            person = member.person
            committee_data.append(
                {
                    "id": member.id,
                    "full_name": _build_name(person) if person else "",
                    "role": member.role,
                    "committee_type": member.committee_type,
                    "degree": person.degree if person else None,
                    "title": person.title if person else None,
                    "position": person.position if person else None,
                    "workplace": person.workplace if person else None,
                    "sort_order": member.sort_order,
                }
            )

        sections_data = []
        for section in sections:
            section_juries = await self._section_jury_repo.list_by_section_with_jury(section.id)
            juries_data = []
            for sj in section_juries:
                jury_person = sj.jury.person if sj.jury else None
                jury_university = sj.jury.university if sj.jury else None
                juries_data.append(
                    {
                        "id": sj.jury.id if sj.jury else None,
                        "full_name": _build_name(jury_person) if jury_person else "",
                        "degree": jury_person.degree if jury_person else None,
                        "title": jury_person.title if jury_person else None,
                        "position": jury_person.position if jury_person else None,
                        "workplace": jury_person.workplace if jury_person else None,
                        "university": jury_university.name if jury_university else None,
                        "is_chairman": sj.jury.is_chairman if sj.jury else False,
                    }
                )

            participants = await self._participant_repo.get_participants_by_section(section.id)
            participants_data = []
            for participant in participants:
                person = participant.person
                advisor = participant.scientific_advisor
                participants_data.append(
                    {
                        "id": participant.id,
                        "full_name": _build_name(person) if person else "",
                        "university": participant.faculty.university.name
                        if participant.faculty and participant.faculty.university
                        else "",
                        "faculty": participant.faculty.name if participant.faculty else "",
                        "presentation_topic": participant.presentation_topic,
                        "abstract": participant.abstract,
                        "presentation_order": participant.presentation_order,
                        "scientific_advisor": {
                            "full_name": _build_name(advisor) if advisor else "",
                            "degree": advisor.degree if advisor else None,
                            "title": advisor.title if advisor else None,
                            "position": advisor.position if advisor else None,
                            "workplace": advisor.workplace if advisor else None,
                        }
                        if advisor
                        else None,
                    }
                )

            sections_data.append(
                {
                    "id": section.id,
                    "name": section.name,
                    "lecture_hall": section.lecture_hall,
                    "time": section.time.isoformat() if section.time else None,
                    "section_type": section.section_type,
                    "time_limit": section.time_limit,
                    "juries": juries_data,
                    "participants": participants_data,
                }
            )

        return {
            "event": {
                "id": event.id,
                "name": event.name,
                "type": event.type,
                "date": event.event_date.isoformat() if event.event_date else None,
                "venue": {
                    "city": event.venue.city,
                    "street": event.venue.street,
                    "building": event.venue.building,
                }
                if event.venue
                else {},
                "organizer": {
                    "full_name": _build_name(event.organizer.person)
                    if event.organizer and event.organizer.person
                    else "",
                    "contact": event.organizer.contact_number,
                }
                if event.organizer
                else {},
            },
            "committee": committee_data,
            "sections": sections_data,
        }
