from fastapi import HTTPException, status

from app.models import JuryScore
from app.repositories.jury import JuryRepository
from app.repositories.jury_score import JuryScoreRepository
from app.repositories.participant import ParticipantRepository
from app.repositories.section_jury import SectionJuryRepository
from app.schemas import JuryScoreCreate, JuryScoreRead, JuryScoreUpdate, ParticipantScoreSummary


class JuryScoreService:
    """Business logic for jury score operations."""

    def __init__(
        self,
        jury_score_repository: JuryScoreRepository,
        participant_repository: ParticipantRepository,
        jury_repository: JuryRepository,
        section_jury_repository: SectionJuryRepository,
    ) -> None:
        self._score_repo = jury_score_repository
        self._participant_repo = participant_repository
        self._jury_repo = jury_repository
        self._section_jury_repo = section_jury_repository

    async def list_scores_for_participant(self, participant_id: int) -> ParticipantScoreSummary:
        """
        Retrieve all scores for a participant with calculated average.

        Args:
            participant_id: ID of the participant

        Returns:
            ParticipantScoreSummary with scores and average

        Raises:
            HTTPException: 404 if participant not found
        """
        # Validate participant exists
        participant = await self._participant_repo.get_participant_by_id(participant_id)
        if participant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Participant with id {participant_id} not found",
            )

        # Get all scores for this participant
        scores = await self._score_repo.list_scores_by_participant(participant_id)
        score_reads = [JuryScoreRead.model_validate(s) for s in scores]

        # Calculate average
        average = ParticipantScoreSummary.calculate_average(score_reads)

        return ParticipantScoreSummary(participant_id=participant_id, scores=score_reads, average_score=average)

    async def get_score_by_id(self, participant_id: int, score_id: int) -> JuryScore | None:
        """
        Retrieve a specific jury score.

        Args:
            participant_id: ID of the participant (for validation)
            score_id: ID of the score

        Returns:
            JuryScore instance or None if not found or doesn't belong to participant
        """
        score = await self._score_repo.get_score_by_id(score_id)

        # Verify the score belongs to the specified participant
        if score is not None and score.participant_id != participant_id:
            return None

        return score

    async def create_score(self, participant_id: int, payload: JuryScoreCreate) -> JuryScore:
        """
        Create a new jury score with comprehensive validations.

        Validations:
        1. Participant must exist
        2. Participant must be assigned to a section
        3. Jury member must exist
        4. Jury member must be assigned to participant's section
        5. No duplicate scoring (jury_id + participant_id must be unique)
        6. Score range validation (0-10) handled by schema validators

        Args:
            participant_id: ID of the participant (from URL)
            payload: Score creation data

        Returns:
            Created JuryScore instance

        Raises:
            HTTPException: 404 for missing entities, 422 for validation failures
        """
        # Ensure participant_id from payload matches URL
        if payload.participant_id is not None and payload.participant_id != participant_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Participant ID in payload does not match URL parameter",
            )

        # Set participant_id from URL
        payload.participant_id = participant_id

        # 1. Validate participant exists and get their section
        participant = await self._participant_repo.get_participant_by_id(participant_id)
        if participant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Participant with id {participant_id} not found",
            )

        if participant.section_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Participant {participant_id} is not assigned to any section",
            )

        # 2. Validate jury member exists
        if payload.jury_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="jury_id is required")

        jury = await self._jury_repo.get_jury_by_id(payload.jury_id)
        if jury is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Jury member with id {payload.jury_id} not found",
            )

        # 3. Validate jury is assigned to participant's section
        is_assigned = await self._section_jury_repo.is_jury_assigned_to_section(
            jury_id=payload.jury_id, section_id=participant.section_id
        )
        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Jury member {payload.jury_id} is not assigned to section {participant.section_id}",
            )

        # 4. Check for duplicate scoring (uniqueness constraint)
        existing_score = await self._score_repo.get_score_by_jury_and_participant(
            jury_id=payload.jury_id, participant_id=participant_id
        )
        if existing_score is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Jury member {payload.jury_id} has already scored participant {participant_id}. "
                f"Use PATCH to update existing score (id: {existing_score.id})",
            )

        # All validations passed, create the score
        return await self._score_repo.create_score(payload)

    async def update_score(
        self, participant_id: int, score_id: int, payload: JuryScoreUpdate, jury_id: int
    ) -> JuryScore | None:
        """
        Update an existing jury score and create audit trail.

        Args:
            participant_id: ID of the participant (from URL)
            score_id: ID of the score to update
            payload: Update data
            jury_id: ID of the jury member making the update (for audit trail)

        Returns:
            Updated JuryScore or None if not found

        Raises:
            HTTPException: 404 if not found, 422 for validation failures
        """
        # Retrieve the score
        score = await self._score_repo.get_score_by_id(score_id)
        if score is None:
            return None

        # Verify the score belongs to the specified participant
        if score.participant_id != participant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Score {score_id} does not belong to participant {participant_id}",
            )

        # Validate jury member exists (for audit trail)
        jury = await self._jury_repo.get_jury_by_id(jury_id)
        if jury is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Jury member with id {jury_id} not found",
            )

        # Update the score
        updated_score = await self._score_repo.update_score(score, payload)

        # Create audit trail entry
        await self._score_repo.create_score_change(jury_score_id=updated_score.id, jury_id=jury_id)

        return updated_score

    async def delete_score(self, participant_id: int, score_id: int) -> bool:
        """
        Delete a jury score.

        Args:
            participant_id: ID of the participant (from URL)
            score_id: ID of the score to delete

        Returns:
            True if deleted, False if not found
        """
        score = await self._score_repo.get_score_by_id(score_id)
        if score is None:
            return False

        # Verify the score belongs to the specified participant
        if score.participant_id != participant_id:
            return False

        await self._score_repo.delete_score(score)
        return True
