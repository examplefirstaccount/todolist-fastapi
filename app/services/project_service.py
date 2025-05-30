from typing import List

from app.api.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.exceptions import ProjectNotFoundError, PermissionDeniedError
from app.utils.unitofwork import UnitOfWork


class ProjectService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_project(self, user_id: int, project: ProjectCreate) -> ProjectResponse:
        async with self.uow:
            project_data = project.model_dump()
            project_data["owner_id"] = user_id

            project_db = await self.uow.project.add(project_data)
            project_response = ProjectResponse.model_validate(project_db)
            await self.uow.commit()

            return project_response

    async def get_projects(self, user_id: int, skip: int = 0, limit: int | None = None) -> List[ProjectResponse]:
        async with self.uow:
            projects = await self.uow.project.find_all(skip, limit, owner_id=user_id)
            return [ProjectResponse.model_validate(p) for p in projects]

    async def get_project(self, user_id: int, project_id: int) -> ProjectResponse:
        async with self.uow:
            project = await self.uow.project.find_one(id=project_id)
            if not project:
                raise ProjectNotFoundError(project_id)
            if project.owner_id != user_id:
                raise PermissionDeniedError("You do not own this project.")
            return ProjectResponse.model_validate(project)

    async def update_project(self, user_id: int, project_id: int, project: ProjectUpdate) -> ProjectResponse:
        async with self.uow:
            project_db = await self.uow.project.find_one(id=project_id)
            if not project_db:
                raise ProjectNotFoundError(project_id)
            if project_db.owner_id != user_id:
                raise PermissionDeniedError("You do not own this project.")

            update_data = project.model_dump()
            project_updated = await self.uow.project.update(update_data, id=project_id)
            if not project_updated:
                raise ProjectNotFoundError(project_id)
            project_response = ProjectResponse.model_validate(project_updated)
            await self.uow.commit()

            return project_response

    async def delete_project(self, user_id: int, project_id: int) -> None:
        async with self.uow:
            project = await self.uow.project.find_one(id=project_id)
            if not project:
                raise ProjectNotFoundError(project_id)
            if project.owner_id != user_id:
                raise PermissionDeniedError("You do not own this project.")

            deleted = await self.uow.project.delete(id=project_id)
            if not deleted:
                raise ProjectNotFoundError(project_id)
            await self.uow.commit()
